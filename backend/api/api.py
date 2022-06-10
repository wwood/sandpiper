"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""
from email import header
import re

from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import select, distinct
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, lazyload
from .models import NcbiMetadata, ParsedSampleAttribute, db, Marker, OtuIndexed, CondensedProfile, Taxonomy, BiosampleAttribute
import pandas as pd
# from api.models import #for flask shell
from .version import __version__, __gtdb_version__, __scrape_date__

import os, sys
sys.path = [os.environ['HOME']+'/git/singlem-local'] + [os.environ['HOME']+'/git/singlem'] + sys.path
from singlem.condense import WordNode

api = Blueprint('api', __name__)

sandpiper_stats_cache = None
sandpiper_taxonomy_id_to_full_name = None
sandpiper_marker_id_to_name = None

def generate_cache():
    global sandpiper_stats_cache
    global sandpiper_taxonomy_id_to_full_name
    global sandpiper_marker_id_to_name

    if sandpiper_stats_cache is None or len(sandpiper_stats_cache) != 3:
        sandpiper_stats_cache = {}
        sandpiper_stats_cache['sandpiper_total_terrabases'] = db.session.query(func.sum(NcbiMetadata.mbases)).scalar()/10**6
        sandpiper_stats_cache['sandpiper_num_runs'] = db.session.query(func.count(distinct(NcbiMetadata.acc))).scalar() #NcbiMetadata.query.distinct(NcbiMetadata.acc).count()
        sandpiper_stats_cache['sandpiper_num_bioprojects'] = db.session.query(func.count(distinct(NcbiMetadata.bioproject))).scalar()
    if sandpiper_taxonomy_id_to_full_name is None:
        print('Caching taxonomy names')
        cache = {}
        for taxon in Taxonomy.query.all():
            cache[taxon.id] = taxon.full_name
        sandpiper_taxonomy_id_to_full_name = cache # Roughly atomic
    if sandpiper_marker_id_to_name is None:
        print('Caching marker names')
        cache = {}
        for marker in Marker.query.all():
            cache[marker.id] = marker.marker
        sandpiper_marker_id_to_name = cache


@api.route('/sandpiper_stats', methods=['GET'])
def sandpiper_stats():
    global sandpiper_stats_cache, sandpiper_taxonomy_id_to_full_name, sandpiper_marker_id_to_name

    # Cache results because they don't change unless the DB changes
    generate_cache()

    return jsonify({
        'num_terrabases': round(sandpiper_stats_cache['sandpiper_total_terrabases']),
        'num_runs': sandpiper_stats_cache['sandpiper_num_runs'],
        'num_bioprojects': sandpiper_stats_cache['sandpiper_num_bioprojects'],
        'version': __version__,
        'scrape_date': __scrape_date__,
    })

@api.route('/markers/', methods=('GET',))
def fetch_markers():
    markers = Marker.query.all()
    return jsonify({ 'markers': [s.to_dict() for s in markers] })

@api.route('/condensed/<string:sample_name>', methods=('GET',))
def fetch_condensed(sample_name):
    root = WordNode(None, 'Root')
    taxons_to_wordnode = {root.word: root}

    condensed = db.session.execute(
        select(CondensedProfile.coverage, Taxonomy.full_name).join(CondensedProfile.ncbi_metadata).
            filter(NcbiMetadata.acc == sample_name).filter(CondensedProfile.taxonomy_id==Taxonomy.id)
        ).fetchall()
    if len(condensed) is None:
        return jsonify({ sample_name: 'no condensed data found' })
    # condensed = CondensedProfile.query.filter_by(run_id=run_id).options(joinedload(CondensedProfile.taxonomy)).all()

    for entry in condensed:
        taxons = entry.full_name.split('; ')

        last_taxon = root
        wn = None
        for (i, tax) in enumerate(taxons):
            if tax not in taxons_to_wordnode:
                wn = WordNode(last_taxon, tax)
                last_taxon.children[tax] = wn
                taxons_to_wordnode[tax] = wn #TODO: Problem when there is non-unique labels? Require full taxonomy used?
            last_taxon = taxons_to_wordnode[tax]
        last_taxon.coverage = entry.coverage

    return jsonify({ 'condensed': wordnode_json(root, 0, 0), 'sample_name': sample_name })

def wordnode_json(wordnode, order, depth):
    r = re.compile('^.__(.+)')
    matches = r.match(wordnode.word)
    if matches is None:
        name = wordnode.word
    else:
        name = matches.group(1)
    j = {
        'name': '' if name == 'Root' else name,
        'size': wordnode.coverage,
        'order': order,
        'condensed_depth': depth,
    }
    # Sort children descending by coverage so more abundance lineages are first
    sorted_children = sorted(wordnode.children.values(), key=lambda x: x.get_full_coverage(), reverse=True)
    if len(wordnode.children.values()) > 0:
        j['children'] = [wordnode_json(child, order+i, depth+1) for i, child in enumerate(sorted_children)]
    return j

@api.route('/metadata/<string:sample_name>', methods=('GET',))
def fetch_metadata(sample_name):
    metadata = NcbiMetadata.query.filter_by(acc=sample_name).all()
    if metadata == [] or metadata is None:
        return jsonify({ "error": 'No metadata found for '+sample_name+'. This likely means that this run was not included when the list of runs to analyse was gathered ('+__scrape_date__+').' })
    meta = metadata[0]
    return jsonify({ 
        'metadata': meta.to_displayable_dict()
        })

def taxonomy_search_fail_json(reason):
    return jsonify({ 'taxon': reason })

@api.route('/taxonomy_search_global_data/<string:taxon>', methods=('GET',))
def taxonomy_search_global_data(taxon):
    taxonomy = Taxonomy.query.filter_by(name=taxon).first()
    if taxonomy is None:
        return taxonomy_search_fail_json('"'+taxon+'" is not a known taxonomy in GTDB '+__gtdb_version__+', or no records of this taxon are recorded in Sandpiper. We recommend using the auto-complete function when searching to avoid typographical errors.')
    total_num_hits = CondensedProfile.query.filter_by(taxonomy_id=taxonomy.id).count()
    if total_num_hits == 0:
        # This happens when there's a taxonomy in the full table that didn't make it into any condensed table
        return taxonomy_search_fail_json('"'+taxon+'" is a known taxonomy, however no records of it are recorded in Sandpiper.')
    num_host_runs = NcbiMetadata.query. \
        join(NcbiMetadata.condensed_profiles).filter_by(taxonomy_id=taxonomy.id). \
        join(NcbiMetadata.parsed_sample_attributes).filter_by(host_or_not_mature='host'). \
        count()
    num_ecological_runs = NcbiMetadata.query. \
        join(NcbiMetadata.condensed_profiles).filter_by(taxonomy_id=taxonomy.id). \
        join(NcbiMetadata.parsed_sample_attributes).filter_by(host_or_not_mature='ecological'). \
        count()
    # lat_lons are commented out for now because it is too slow to query and
    # render. SQL needs better querying i.e. in batch, and multiple
    # annotations at a single location need to be collapsed.
    lat_lons, lat_lons_count = get_lat_lons(taxonomy.id, 1000)
    return jsonify({ 
        'total_num_results': total_num_hits,
        'taxon_name': taxonomy.name.split('__')[-1],
        'lineage': taxonomy.split_taxonomy(),
        'taxonomy_level': taxonomy.taxonomy_level,
        'lat_lons': lat_lons,
        'num_lat_lon_runs': lat_lons_count,
        'num_host_runs': num_host_runs,
        'num_ecological_runs': num_ecological_runs,
    })

# sort_field=${sortField}&sort_direction=${sortDirection}&page=${page
@api.route('/taxonomy_search_run_data/<string:taxon>', methods=('GET',))
def taxonomy_search_run_data(taxon):
    worked, condensed_profile_hits = taxonomy_search_core(taxon, request.args)

    if worked:
        return jsonify({
            'results': {
                'condensed_profiles': [{
                    'sample_acc': c.acc,
                    'relative_abundance': round(c.relative_abundance*100,2),
                    'coverage': round(c.filled_coverage, 2),
                    'organism': c.organism.replace(' metagenome',''),
                    'collection_year': c.collection_year,}
                    for c in condensed_profile_hits],                
            }
        })
    else:
        return condensed_profile_hits # Really returning a JSON indicating the failure

@api.route('/taxonomy_search_csv/<string:taxon>', methods=('GET',))
def taxonomy_search_csv(taxon):
    worked, condensed_profile_hits = taxonomy_search_core(taxon, request.args, no_limit=True)

    if worked:
        df = pd.DataFrame(
            [[
                c.acc,
                round(c.relative_abundance*100,2),
                round(c.filled_coverage, 2),
                c.organism]
                for c in condensed_profile_hits],
            columns=['sample', 'relative_abundance', 'coverage', 'organism']
        )
        response = make_response(df.to_csv(index=False, header=True))
        cd = 'attachment; filename=sandpiper_v{}_{}_condensed.csv'.format(__version__, taxon)
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response
    else:
        return condensed_profile_hits # Really returning a JSON indicating the failure

def taxonomy_search_core(taxon, args, no_limit=False):
    '''Returns (bool, iterable|json) where bool is whether it worked (True)
    or not (False) and iterable is the data to render. json is the error if
    it failed.'''

    sort_field = args.get('sort_field')
    sort_direction = args.get('sort_direction')
    page = args.get('page')
    page_size = args.get('page_size')
    sort_field = 'relative_abundance' if sort_field is None else sort_field
    sort_direction = 'desc' if sort_direction is None else sort_direction
    page = int(page) if page is not None else 0
    page_size = int(page_size) if page_size is not None else 100

    if sort_field not in ['relative_abundance', 'coverage']:
        return False, jsonify({ 'error': 'invalid sort field' })
    if sort_direction not in ['asc', 'desc']:
        return False, jsonify({ 'error': 'invalid sort direction' })

    taxonomy = Taxonomy.query.filter_by(name=taxon).first()
    if taxonomy is None:
        return False, taxonomy_search_fail_json('"'+taxon+'" is not a known taxonomy, or no records of this taxon are recorded in Sandpiper.')
    else:
        # Query for samples that contain this taxon
        stmt = select(
            NcbiMetadata.acc,
            CondensedProfile.relative_abundance,
            CondensedProfile.filled_coverage,
            NcbiMetadata.organism,
            ParsedSampleAttribute.collection_year,
            # TODO: Add experiment title here, not currently in DB
        ).where(CondensedProfile.run_id == NcbiMetadata.id).where(
            NcbiMetadata.id == ParsedSampleAttribute.run_id)
        
        if sort_field == 'relative_abundance':
            if sort_direction == 'desc':
                hits_query = stmt.order_by(CondensedProfile.relative_abundance.desc())
            else:
                hits_query = stmt.order_by(CondensedProfile.relative_abundance.asc())
        elif sort_field == 'coverage':
            if sort_direction == 'desc':
                hits_query = stmt.order_by(CondensedProfile.filled_coverage.desc())
            else:
                hits_query = stmt.order_by(CondensedProfile.filled_coverage.asc())

        if not no_limit:
            hits_query = hits_query.limit(page_size).offset((page-1)*page_size)
            
        condensed_profile_hits = db.session.execute(
            hits_query.where(
                CondensedProfile.taxonomy_id == taxonomy.id))

        return True, condensed_profile_hits


@api.route('/taxonomy_search_hints/<string:taxon>', methods=('GET',))
def taxonomy_search_hints(taxon):
    if len(taxon) < 3: return jsonify(['3 or more characters are required'])

    # Underscores are wildcards, but we don't want that since there are names like p__Actinobacteria
    sql = "select name from taxonomies where name like :taxon escape \'\\\' order by name limit 30"
    results = db.session.execute(sql, {'taxon': '%'+taxon.replace('_','\_')+'%'})
    taxonomies = []
    for r in results:
        taxonomies.append(r)
    if len(taxonomies) == 0:
        return jsonify(['no taxonomy found for '+taxon])

    return jsonify({ 'taxonomies': [t.name for t in taxonomies] })

def get_lat_lons(taxonomy_id, max_to_show):
    lat_lon_db_entries = db.session.execute(
        select(NcbiMetadata.acc, ParsedSampleAttribute.latitude, ParsedSampleAttribute.longitude, NcbiMetadata.study_title).where(
            CondensedProfile.taxonomy_id == taxonomy_id).where(
            NcbiMetadata.id == ParsedSampleAttribute.run_id).where(
            NcbiMetadata.id == CondensedProfile.run_id).where(
            ParsedSampleAttribute.latitude.is_not(None)
            ).order_by(CondensedProfile.relative_abundance.desc(), CondensedProfile.id).limit(max_to_show).distinct()).fetchall()

    lat_lons = {}
    lat_lons_count = 0
    for (sample_name, lat, lon, description) in lat_lon_db_entries:
        lat_lons_count += 1
        mykey = '%s %s' % (lat, lon)
        if mykey in lat_lons:
            if description in lat_lons[mykey]['samples']:
                lat_lons[mykey]['samples'][description].append(sample_name)
            else:
                lat_lons[mykey]['samples'][description] = [sample_name]
        else:
            lat_lons[mykey] = {'lat_lon': [lat, lon], 'samples': {description: [sample_name]}}
    return list(lat_lons.values()), lat_lons_count

@api.route('/otus/<string:acc>', methods=('GET',))
def otus(acc):
    global sandpiper_taxonomy_id_to_full_name, sandpiper_marker_id_to_name

    # Doesn't usually cache anything, but useful to have here for testing
    generate_cache()

    run_id = NcbiMetadata.query.filter_by(acc=acc).first().id
    if run_id is None:
        return jsonify({ 'error': 'no run found for acc '+acc })

    otus = OtuIndexed.query.filter_by(run_id=run_id).order_by(OtuIndexed.id).all()
    print(otus[0].to_dict())
    print(sandpiper_marker_id_to_name)

    df = pd.DataFrame(
        [[
            # gene	sample	sequence	num_hits	coverage	taxonomy
            sandpiper_marker_id_to_name[otu.marker_id],
            acc,
            otu.sequence,
            otu.num_hits,
            otu.coverage,
            'Root; ' + sandpiper_taxonomy_id_to_full_name[otu.taxonomy_id]
        ] for otu in otus],
        columns=['gene','sample','sequence','num_hits','coverage','taxonomy']
    )
    response = make_response(df.to_csv(index=False, header=True, sep='\t'))
    cd = 'attachment; filename=sandpiper_v{}_{}_condensed.csv'.format(__version__, acc)
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response
