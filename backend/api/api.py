"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""
import re

from flask import Blueprint, jsonify, request
from sqlalchemy import select, distinct
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, lazyload
from .models import NcbiMetadata, db, Marker, Otu, CondensedProfile, Taxonomy, BiosampleAttribute
# from api.models import #for flask shell

import os, sys
sys.path = [os.environ['HOME']+'/git/singlem-local'] + [os.environ['HOME']+'/git/singlem'] + sys.path
from singlem.condense import WordNode

api = Blueprint('api', __name__)

sandpiper_stats_cache = None

@api.route('/sandpiper_stats', methods=['GET'])
def sandpiper_stats():
    global sandpiper_stats_cache
    # Cache results because they don't change unless the DB changes
    if sandpiper_stats_cache is None:
        sandpiper_stats_cache = {}
        sandpiper_stats_cache['sandpiper_total_terrabases'] = db.session.query(func.sum(NcbiMetadata.mbases)).scalar()/10**6
        sandpiper_stats_cache['sandpiper_num_runs'] = db.session.query(func.count(distinct(NcbiMetadata.acc))).scalar() #NcbiMetadata.query.distinct(NcbiMetadata.acc).count()
        sandpiper_stats_cache['sandpiper_num_bioprojects'] = db.session.query(func.count(distinct(NcbiMetadata.bioproject))).scalar()
    return jsonify({
        'num_terrabases': round(sandpiper_stats_cache['sandpiper_total_terrabases']),
        'num_runs': sandpiper_stats_cache['sandpiper_num_runs'],
        'num_bioprojects': sandpiper_stats_cache['sandpiper_num_bioprojects']
    })

@api.route('/markers/', methods=('GET',))
def fetch_markers():
    markers = Marker.query.all()
    return jsonify({ 'markers': [s.to_dict() for s in markers] })

@api.route('/otus/<string:sample_name>/marker/<string:marker_name>', methods=('GET',))
def fetch_otus(sample_name, marker_name):
    otus = Otu.query.filter_by(sample_name=sample_name).join(Otu.marker, aliased=True).filter_by(marker=marker_name).all()
    return jsonify({ 'otus': [s.to_dict() for s in otus] })

@api.route('/condensed/<string:sample_name>', methods=('GET',))
def fetch_condensed(sample_name):
    root = WordNode(None, 'Root')
    taxons_to_wordnode = {root.word: root}

    # condensed = CondensedProfile.query.filter_by(sample_name=sample_name).options(lazyload(CondensedProfile.taxonomy)).all()
    condensed = CondensedProfile.query.filter_by(sample_name=sample_name).options(joinedload(CondensedProfile.taxonomy)).all()
    if len(condensed) == 0:
        return jsonify({ sample_name: 'no condensed data found' })
    for entry in condensed:
        taxons = entry.taxonomy.split_taxonomy()

        last_taxon = root
        wn = None
        for (i, tax) in enumerate(taxons):
            if tax not in taxons_to_wordnode:
                wn = WordNode(last_taxon, tax)
                # print("Adding tax %s with prev %s" % (tax, last_taxon.word))
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
        'name': name,
        'size': wordnode.coverage,
        'order': order,
        'depth': depth,
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
        return jsonify({ sample_name: 'no metadata found for '+sample_name })
    return jsonify({ 'metadata': metadata[0].to_displayable_dict() })

def taxonomy_search_fail_json(reason):
    return jsonify({ 'taxon': reason })

@api.route('/taxonomy_search_global_data/<string:taxon>', methods=('GET',))
def taxonomy_search_global_data(taxon):
    taxonomy = Taxonomy.query.filter_by(name=taxon).first()
    if taxonomy is None:
        return taxonomy_search_fail_json('no taxonomy found for '+taxon)
    total_num_hits = CondensedProfile.query.filter_by(taxonomy_id=taxonomy.id).count()
    # lat_lons are commented out for now because it is too slow to query and
    # render. SQL needs better querying i.e. in batch, and multiple
    # annotations at a single location need to be collapsed.
    lat_lons = get_lat_lons(taxonomy.id, 100)
    return jsonify({ 
        'total_num_results': total_num_hits,
        'taxon': taxonomy.split_taxonomy(),
        'lat_lons': lat_lons
    })

# sort_field=${sortField}&sort_direction=${sortDirection}&page=${page
@api.route('/taxonomy_search_run_data/<string:taxon>', methods=('GET',))
def taxonomy_search(taxon):
    args = request.args
    sort_field = args.get('sort_field')
    sort_direction = args.get('sort_direction')
    page = args.get('page')
    page_size = args.get('page_size')
    sort_field = 'relative_abundance' if sort_field is None else sort_field
    sort_direction = 'desc' if sort_direction is None else sort_direction
    page = int(page) if page is not None else 0
    page_size = int(page_size) if page_size is not None else 100

    if sort_field not in ['relative_abundance', 'coverage']:
        return jsonify({ 'error': 'invalid sort field' })
    if sort_direction not in ['asc', 'desc']:
        return jsonify({ 'error': 'invalid sort direction' })

    taxonomy = Taxonomy.query.filter_by(name=taxon).first()
    if taxonomy is None:
        return taxonomy_search_fail_json('no taxonomy found for '+taxon)
    else:
        # Query for samples that contain this taxon
        if sort_field == 'relative_abundance':
            if sort_direction == 'desc':
                hits_query = CondensedProfile.query.order_by(CondensedProfile.relative_abundance.desc())
            else:
                hits_query = CondensedProfile.query.order_by(CondensedProfile.relative_abundance.asc())
        elif sort_field == 'coverage':
            if sort_direction == 'desc':
                hits_query = CondensedProfile.query.order_by(CondensedProfile.filled_coverage.desc())
            else:
                hits_query = CondensedProfile.query.order_by(CondensedProfile.filled_coverage.asc())

        condensed_profile_hits = hits_query.where(
                CondensedProfile.taxonomy_id == taxonomy.id).limit(
                    page_size).offset((page-1)*page_size).all()
        
        return jsonify({
            'taxon': taxonomy.split_taxonomy(),
            'results': {
                'condensed_profiles': [{
                    'sample_name': c.sample_name,
                    'relative_abundance': round(c.relative_abundance*100,2),
                    'coverage': round(c.filled_coverage, 2) }
                    for c in condensed_profile_hits],                
            }
        })

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
    # It would be ideal to order by relative_abundance desc, but this seems to
    # not be performant. We must order by CondensedProfile.id at least because
    # the lat and lon of geographic_location__latitude__sam /
    # geographic_location__longitude__sam are in separate rows.
    lat_lon_db_entries = NcbiMetadata.query.join(NcbiMetadata.condensed_profiles).with_entities(
        NcbiMetadata.acc, NcbiMetadata.latitude, NcbiMetadata.longitude).where(
            NcbiMetadata.latitude != None
        ).where(
            CondensedProfile.relative_abundance > 0.01
        ).where(
            CondensedProfile.taxonomy_id == taxonomy_id
        ).order_by(CondensedProfile.relative_abundance.desc(), CondensedProfile.id).limit(max_to_show).all()

    lat_lons = {}
    print(lat_lon_db_entries)
    for (sample_name, lat, lon) in lat_lon_db_entries:
        mykey = '%s %s' % (lat, lon)
        if mykey in lat_lons:
            lat_lons[mykey]['sample_names'].append(sample_name)
        else:
            lat_lons[mykey] = {'lat_lon': [lat, lon], 'sample_names': [sample_name]}
    return list(lat_lons.values())   


def validate_lat_lon(lat, lon):
    if lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180:
        return True
    return False
