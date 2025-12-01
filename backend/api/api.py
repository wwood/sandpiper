"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""
import csv
import io
import re
import requests

from flask import Blueprint, jsonify, request, make_response, current_app, Response, stream_with_context

from sqlalchemy import select, distinct, or_
from sqlalchemy.sql import func, text
from sqlalchemy.orm import joinedload, lazyload

from .models import (
    NcbiMetadata,
    ParsedSampleAttribute,
    db,
    Marker,
    OtuIndexed,
    CondensedProfile,
    CondensedProfileCtas1,
    Taxonomy,
    SandpiperCache,
)
import pandas as pd
import polars as pl
# from api.models import #for flask shell
from .version import __version__, __gtdb_version__, __scrape_date__

import os, sys, json
sys.path = [os.environ['HOME']+'/git/singlem-local'] + [os.environ['HOME']+'/git/singlem'] + sys.path
from singlem.condense import WordNode
from singlem.summariser import Summariser

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path
from sandpiper.biosample_attributes import *
from sandpiper.parse_biosample_extras import ACTUALLY_MISSING

api = Blueprint('api', __name__)

sandpiper_stats_cache = None
sandpiper_taxonomy_id_to_full_name = None
sandpiper_marker_id_to_name = None
biosample_attribute_definitions = None
ncbi_metadata_infos = None

def generate_cache():
    global sandpiper_stats_cache
    global sandpiper_taxonomy_id_to_full_name
    global sandpiper_marker_id_to_name
    global biosample_attribute_definitions
    global ncbi_metadata_infos

    if (
        sandpiper_stats_cache is None
        or sandpiper_taxonomy_id_to_full_name is None
        or sandpiper_marker_id_to_name is None
        or biosample_attribute_definitions is None
        or ncbi_metadata_infos is None
    ):
        try:
            cache_rows = SandpiperCache.query.all()
            cache = {row.key: json.loads(row.value) for row in cache_rows}
            if 'stats' in cache and sandpiper_stats_cache is None:
                sandpiper_stats_cache = cache['stats']
            if 'taxonomy_id_to_full_name' in cache and sandpiper_taxonomy_id_to_full_name is None:
                sandpiper_taxonomy_id_to_full_name = {
                    int(k): v for k, v in cache['taxonomy_id_to_full_name'].items()
                }
            if 'marker_id_to_name' in cache and sandpiper_marker_id_to_name is None:
                sandpiper_marker_id_to_name = {
                    int(k): v for k, v in cache['marker_id_to_name'].items()
                }
            if 'biosample_attribute_definitions' in cache and biosample_attribute_definitions is None:
                biosample_attribute_definitions = {
                    k: BioSampleAttribute(**v)
                    for k, v in cache['biosample_attribute_definitions'].items()
                }
            if 'ncbi_metadata_infos' in cache and ncbi_metadata_infos is None:
                ncbi_metadata_infos = {
                    k: NcbiMetadataExtraInfo(**v)
                    for k, v in cache['ncbi_metadata_infos'].items()
                }
        except Exception as e:
            current_app.logger.warning(
                'Failed to load cache table, regenerating dynamically: %s', e
            )

    if sandpiper_stats_cache is None or len(sandpiper_stats_cache) != 3:
        sandpiper_stats_cache = {}
        sandpiper_stats_cache['sandpiper_total_terrabases'] = db.session.query(func.sum(NcbiMetadata.bases)).scalar()/10**12
        sandpiper_stats_cache['sandpiper_num_runs'] = db.session.query(func.count(distinct(NcbiMetadata.acc))).scalar()
        sandpiper_stats_cache['sandpiper_num_bioprojects'] = db.session.query(func.count(distinct(NcbiMetadata.bioproject))).scalar()
    if sandpiper_taxonomy_id_to_full_name is None:
        cache = {}
        for taxon in Taxonomy.query.all():
            cache[taxon.id] = taxon.full_name
        sandpiper_taxonomy_id_to_full_name = cache
    if sandpiper_marker_id_to_name is None:
        cache = {}
        for marker in Marker.query.all():
            cache[marker.id] = marker.marker
        sandpiper_marker_id_to_name = cache
    if biosample_attribute_definitions is None:
        biosample_attribute_definitions = BioSampleAttributes(current_app.logger).attributes
    if ncbi_metadata_infos is None:
        ncbi_metadata_infos = NcbiMetadataExtraInfos().extra_info



######## DEBUG to find slow SQL queries ########
# Set up SQL logging for debugging
from sqlalchemy import event
import time
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.perf_counter() - getattr(context, "_query_start_time", 0)
    print(f"[SQL] {statement} - {total:.6f} sec")
# Attach listeners when the application context is available (on first request).
# Attaching at import time caused "Working outside of application context" because
# db.engine requires the current_app to be set up.
@api.before_app_request
def setup_sql_logging():
    # Only enable SQL timing when in debug mode (or if explicitly enabled via config)
    try:
        event.listen(db.engine, "before_cursor_execute", before_cursor_execute)
        event.listen(db.engine, "after_cursor_execute", after_cursor_execute)
    except RuntimeError:
        # If for some reason the app context is still not available, log a warning.
        try:
            current_app.logger.warning("Could not attach SQL event listeners at setup_sql_logging()")
        except Exception:
            # Fallback to printing if logger isn't available
            print("Warning: Could not attach SQL event listeners at setup_sql_logging()")
######## END DEBUG to find slow SQL queries ########



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
        'gtdb_version': __gtdb_version__,
    })

@api.route('/markers/', methods=('GET',))
def fetch_markers():
    markers = Marker.query.all()
    return jsonify({ 'markers': [s.to_dict() for s in markers] })

@api.route('/condensed/<string:sample_name>', methods=('GET',))
def fetch_condensed(sample_name):
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    root = WordNode(None, 'Root')
    taxons_to_wordnode = {root.word: root}

    condensed = db.session.execute(
        select(CondensedProfile.coverage, Taxonomy.full_name)
            .join(CondensedProfile.ncbi_metadata)
            .filter(NcbiMetadata.acc == sample_name)
            .filter(CondensedProfile.taxonomy_id == Taxonomy.id)
            .filter(Taxonomy.taxonomy_type == taxonomy_type)
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

@api.route('/condensed_csv/<string:sample_name>', methods=('GET',))
def fetch_condensed_csv(sample_name):
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    condensed = db.session.execute(
        select(CondensedProfile.coverage, Taxonomy.full_name, Taxonomy.taxonomy_level)
            .join(CondensedProfile.ncbi_metadata)
            .filter(NcbiMetadata.acc == sample_name)
            .filter(CondensedProfile.taxonomy_id == Taxonomy.id)
            .filter(Taxonomy.taxonomy_type == taxonomy_type)
            .filter(CondensedProfile.coverage > 0)
        ).fetchall()
    if len(condensed) is None:
        return jsonify({ sample_name: 'no condensed data found' })
    
    # Sort df by taxonomy level. Since they are strings, we convert to int first
    level_to_int = {
        'domain': 1,
        'phylum': 2,
        'class': 3,
        'order': 4,
        'family': 5,
        'genus': 6,
        'species': 7,
    }
    df = pl.DataFrame(
        [[
            sample_name,
            d.coverage,
            'Root; '+d.full_name if d.full_name != 'Root' else d.full_name,
            level_to_int[d.taxonomy_level]
        ] for d in condensed],
        orient="row",
        schema=['sample', 'coverage', 'taxonomy', 'taxonomy_level_int']
    ).sort( # sort by taxonomy level_int first, then coverage descending
        ['taxonomy_level_int', 'coverage'], descending=[False, True]).select(['sample', 'coverage', 'taxonomy'])
    
    response = make_response(df.write_csv(separator='\t'))
    cd = 'attachment; filename=sandpiper_v{}_{}_{}_condensed.csv'.format(__version__, sample_name, taxonomy_type)
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response

@api.route('/condensed_csv_with_extras/<string:sample_name>', methods=('GET',))
def fetch_condensed_csv_with_extras(sample_name):
    # TODO: remove duplication with above?
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    condensed = db.session.execute(
        select(CondensedProfile.coverage, Taxonomy.full_name, Taxonomy.taxonomy_level)
            .join(CondensedProfile.ncbi_metadata)
            .filter(NcbiMetadata.acc == sample_name)
            .filter(CondensedProfile.taxonomy_id == Taxonomy.id)
            .filter(Taxonomy.taxonomy_type == taxonomy_type)
            .filter(CondensedProfile.coverage > 0) # zeroes are introduced later, so this filter makes no difference
        ).fetchall()
    if len(condensed) is None:
        return jsonify({ sample_name: 'no condensed data found' })

    # Use the Summarise.write_taxonomic_profile_with_extras function logic to implement
    df = pl.DataFrame(
        [[
            sample_name,
            d.coverage,
            'Root; '+d.full_name if d.full_name != 'Root' else d.full_name,
        ] for d in condensed],
        orient="row",
        schema=['sample', 'coverage', 'taxonomy']
    )
    # write_taxonomic_profile_with_extras takes a list of input files, so we
    # need to simulate that by writing our df to a temp file first. The output
    # will be also be a file, so create a temp file for that too.
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as input_tempfile, tempfile.NamedTemporaryFile(mode='r+', delete=True) as output_tempfile:
        df.write_csv(input_tempfile.name, separator='\t')
        input_taxonomic_profile_files = [input_tempfile.name]
        Summariser.write_taxonomic_profile_with_extras(
            input_taxonomic_profile_files=input_taxonomic_profile_files,
            output_taxonomic_profile_extras_io=output_tempfile,
            num_decimal_places=2, # As of 0.20.2, defaulting to 2 fails
        )
        output_tempfile.seek(0)
        response = make_response(output_tempfile.read())
        cd = 'attachment; filename=sandpiper_v{}_{}_{}_condensed_with_extras.csv'.format(__version__, sample_name, taxonomy_type)
        response.headers['Content-Disposition'] = cd
        response.mimetype = 'text/csv'
        return response


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

@api.route('/full_profile/<string:sample_name>', methods=('GET',))
def fetch_full_profile(sample_name):
    global sandpiper_taxonomy_id_to_full_name, sandpiper_marker_id_to_name

    # Doesn't usually cache anything, but useful to have here for testing
    generate_cache()

    run_id = NcbiMetadata.query.filter_by(acc=sample_name).first().id
    if run_id is None:
        return jsonify({ 'error': 'no run found for acc '+sample_name })

    otus = OtuIndexed.query.filter_by(run_id=run_id, marker_id=1).order_by(OtuIndexed.id).all()

    root = WordNode(None, 'Root')
    taxons_to_wordnode = {root.word: root}

    for (i, otu) in enumerate(otus):
        taxonomy = ('Root' if otu.taxonomy_id==0 else 'Root; ' + sandpiper_taxonomy_id_to_full_name[otu.taxonomy_id]) if otu.taxonomy_id in sandpiper_taxonomy_id_to_full_name else otu.taxonomy_id
        taxons = taxonomy.split('; ')+['OTU '+str(i+1)]

        last_taxon = root
        wn = None
        for tax in taxons:
            if tax not in taxons_to_wordnode:
                wn = WordNode(last_taxon, tax)
                last_taxon.children[tax] = wn
                taxons_to_wordnode[tax] = wn #TODO: Problem when there is non-unique labels? Require full taxonomy used?
            last_taxon = taxons_to_wordnode[tax]
        last_taxon.coverage = otu.coverage

    return jsonify({ 'otus': wordnode_json(root, 0, 0), 'sample_name': sample_name })


def _read_length_summary(read1_length_average, read2_length_average):
    if read1_length_average is not None and read2_length_average is not None:
        return '%.0fx%.0fbp reads' % (read1_length_average, read2_length_average)
    if read1_length_average is not None:
        return '%.0fbp reads' % read1_length_average
    return None


@api.route('/metadata/<string:sample_name>', methods=('GET',))
def fetch_metadata(sample_name):
    global biosample_attribute_definitions, ncbi_metadata_infos

    # Doesn't usually cache anything, but useful to have here for testing
    generate_cache()

    metadata = NcbiMetadata.query.filter_by(acc=sample_name).all()
    if metadata == [] or metadata is None:
        return jsonify({ "error": 'No metadata found for '+sample_name+'. This likely means that this run was not included when the list of runs to analyse was gathered ('+__scrape_date__+').' })
    meta = metadata[0]

    metadata_dict = meta.to_displayable_dict()

    host_mature = metadata_dict['parsed_sample_attributes']['host_or_not_mature']
    if host_mature == 'host':
        host_mature = 'Eukaryote host-associated'
    
    metadata_parsed = {
        'mbases': round(metadata_dict['bases']/1e6),
        'spots': metadata_dict['spots'],
        'organism': metadata_dict['taxon_name'],
        'instrument': metadata_dict['model'],
        'collection_time': metadata_dict['parsed_sample_attributes']['collection_year'],
        'release_month': meta.published.strftime('%Y'),
        'latitude': metadata_dict['parsed_sample_attributes']['latitude'],
        'longitude': metadata_dict['parsed_sample_attributes']['longitude'],
        'num_related_runs': related_run_count(meta.bioproject)-1,
        'host_or_not_mature': host_mature,
        'smf': round(metadata_dict['parsed_sample_attributes']['smf']),
        'smf_warning': metadata_dict['parsed_sample_attributes']['smf_warning'],
        'known_species_fraction': round(metadata_dict['parsed_sample_attributes']['known_species_fraction']*100),
        'globdb_known_species_fraction': (
            round(metadata_dict['parsed_sample_attributes']['globdb_known_species_fraction'] * 100)
            if metadata_dict['parsed_sample_attributes']['globdb_known_species_fraction'] is not None
            else None
        ),
        'sample_name': metadata_dict['sample_name'],
        'study_title': metadata_dict['study_title'],
        'bioproject': metadata_dict['bioproject'],
        'study_abstract': metadata_dict['study_abstract'],
    }

    metadata_parsed['read_length_summary'] = _read_length_summary(
        meta.read1_length_average, meta.read2_length_average
    )

    # Change format to be classification => [[name, description], [name, description], ..]
    # for fields that are known already
    d2 = {}
    basic_metadata_metadata = {}
    for info in ncbi_metadata_infos.values():
        basic_metadata_metadata[info.name] = info
        basic_metadata_metadata[info.name.replace('_', ' ')] = info
        basic_metadata_metadata[info.name.replace(' ', '_')] = info

    def add_annotation(k, v):
        if v is None or str(v).lower().strip() in ACTUALLY_MISSING:
            # Do not display missing / fake data
            return
        if k in basic_metadata_metadata:
            info = basic_metadata_metadata[k]
            to_add = {
                'k': basic_metadata_metadata[k].nice_name,
                'v': v,
                'description': basic_metadata_metadata[k].description,
                'is_custom': False}
            if info.classification in d2:
                d2[info.classification].append(to_add)
            else:
                d2[info.classification] = [to_add]
        else:
            to_add = {
                'k': k.replace('_', ' '),
                'v': v,
                'description': None,
                'is_custom': True}
            # by default, associate with sample
            if SAMPLE_INFO_TYPE_METADATA not in d2:
                d2[SAMPLE_INFO_TYPE_METADATA] = []
            d2[SAMPLE_INFO_TYPE_METADATA].append(to_add)

    for k, v in metadata_dict.items():
        if k in ['acc', 'biosample_attributes', 'study_links', 'parsed_sample_attributes', 'study_title', 'study_abstract']:
            continue
        add_annotation(k, v)

    # Give the biosample attributes a more friendly name, and annotate them as
    # being custom or not.
    biosample_dict = []
    sam_regex = re.compile(r'_sam$')

    for bs in metadata_dict['biosample_attributes']:
        k_original = bs['k']
        k = sam_regex.sub('', k_original)
        v = bs['v']

        if k_original in ['Gbp', 'run_size', 'study_links']: continue # This is a duplicate of mbases / spots
        # study_links is a temperorary fix

        if v is None or str(v).lower().strip() in ACTUALLY_MISSING:
            # Do not display missing / fake data
            continue
        
        if k in biosample_attribute_definitions:
            biosample_dict.append({ 
                'k': biosample_attribute_definitions[k].name, 
                'v': v,
                'is_custom': False,
                'description': biosample_attribute_definitions[k].description })
        else:
            # Submitters can upload custom attributes
            add_annotation(k, v)

    if SAMPLE_INFO_TYPE_METADATA not in d2:
        d2[SAMPLE_INFO_TYPE_METADATA] = []
    d2[SAMPLE_INFO_TYPE_METADATA].extend(biosample_dict)

    # Some are double e.g. https://sandpiper.qut.edu.au/run/SRR9224309 has 2 PubMed study_links
    final_study_links = []
    # print("Study links from dict: {}".format(metadata_dict['study_links']))
    for study_link_pair in metadata_dict['study_links']:
        if 'database' in study_link_pair:
            db = study_link_pair['database']
            study_id = study_link_pair['study_id']
            if db == 'ePubmed': db = 'pubmed'
            if db == 'eDOI': db = 'DOI'
            new_link = {
                'database': db,
                'study_id': study_id,
            }
            if new_link not in final_study_links:
                final_study_links.append(new_link)
        else:
            # label / url type
            if study_link_pair not in final_study_links:
                final_study_links.append(study_link_pair)
    d2['study_links'] = final_study_links

    # Order the values in each classification dict in alphabetical order
    for k, v in d2.items():
        if len(v) > 0 and 'k' in v[0]: # don't sort e.g. study_links
            d2[k] = sorted(v, key=lambda x: x['k'].lower())

    return jsonify({ 
        'metadata': d2,
        'metadata_parsed': metadata_parsed})

def taxonomy_search_fail_json(reason):
    return jsonify({ 'taxon': reason })


def taxonomy_types_for_name(taxon):
    return db.session.execute(
        select(distinct(Taxonomy.taxonomy_type)).where(Taxonomy.name == taxon)
    ).scalars().all()


def taxonomy_not_found_response(taxon):
    taxonomy_types = taxonomy_types_for_name(taxon)
    if len(taxonomy_types) == 0:
        reason = f'"{taxon}" is not a known taxonomy in Sandpiper, suggesting it is not known in GTDB or GlobDB either.'
    else:
        reason = (
            f'"{taxon}" is a known taxonomy, but no samples containing it were found. '
            f'It is a valid taxonomy in: {", ".join(sorted(taxonomy_types))}.'
        )
    return taxonomy_search_fail_json(reason)

@api.route('/taxonomy_search_global_data/<string:taxon>', methods=('GET',))
def taxonomy_search_global_data(taxon):
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    taxonomy = Taxonomy.query.filter_by(name=taxon, taxonomy_type=taxonomy_type).first()
    if taxonomy is None:
        return taxonomy_not_found_response(taxon)
    total_num_hits = CondensedProfileCtas1.query.filter_by(taxonomy_id=taxonomy.id).count()
    if total_num_hits == 0:
        # This happens when there's a taxonomy in the full table that didn't make it into any condensed table
        return taxonomy_not_found_response(taxon)
    num_host_runs = taxonomy.host_sample_count
    num_ecological_runs = taxonomy.ecological_sample_count
    # lat_lons are commented out for now because it is too slow to query and
    # render. SQL needs better querying i.e. in batch, and multiple
    # annotations at a single location need to be collapsed.
    lat_lons, lat_lons_count, min_lat_lon_relabund = get_lat_lons(taxonomy.id, 1000)
    return jsonify({ 
        'total_num_results': total_num_hits,
        'taxon_name': taxonomy.name.split('__')[-1],
        'lineage': taxonomy.split_taxonomy(),
        'taxonomy_level': taxonomy.taxonomy_level,
        'lat_lons': lat_lons,
        'lat_lons_min_relabund': min_lat_lon_relabund,
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
                'organism': "unspecified" if c.taxon_name is None else c.taxon_name.replace(' metagenome',''),
                'release_year': c.published.strftime('%Y'),}
                for c in condensed_profile_hits],                
            }
        })
    else:
        return condensed_profile_hits # Really returning a JSON indicating the failure

@api.route('/taxonomy_search_csv/<string:taxon>', methods=('GET',))
def taxonomy_search_csv(taxon):
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    from datetime import datetime
    print('=== {}: running core'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    worked, condensed_profile_hits = taxonomy_search_core(taxon, request.args, no_limit=True, include_extras=True)
    print('=== {}: after core'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    if worked:
        print('=== {}: worked core'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        headers = [
            'sample', 'relative_abundance', 'coverage', 'taxon_name', 'study_title', 'release_year',
            'metagenome_base_pairs', 'bacterial_archaeal_bases',
            'eukaryotic_host_association', 'num_reads', 'read_length_summary', 'sequencing_instrument', 'collection_year',
            'spf', 'spf_warning',
            'gtdb_known_species_fraction_percent', 'globdb_known_species_fraction_percent',
            'latitude', 'longitude'
        ]

        def generate_csv_rows():
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(headers)
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            try:
                while True:
                    chunk = condensed_profile_hits.fetchmany(1000)
                    if not chunk:
                        break
                    for c in chunk:
                        writer.writerow([
                            c.acc,
                            round(c.relative_abundance * 100, 2),
                            round(c.filled_coverage, 2),
                            c.taxon_name,
                            c.study_title,
                            c.published.strftime('%Y'),
                            c.bases,
                            c.bacterial_archaeal_bases,
                            c.host_or_not_mature,
                            c.spots,
                            _read_length_summary(c.read1_length_average, c.read2_length_average),
                            c.model,
                            c.collection_year,
                            round(c.smf, 2) if c.smf is not None else None,
                            c.smf_warning,
                            round(c.known_species_fraction * 100, 2)
                            if c.known_species_fraction is not None
                            else None,
                            round(c.globdb_known_species_fraction * 100, 2)
                            if c.globdb_known_species_fraction is not None
                            else None,
                            c.latitude,
                            c.longitude,
                        ])
                    yield buffer.getvalue()
                    buffer.seek(0)
                    buffer.truncate(0)
            finally:
                condensed_profile_hits.close()

        response = Response(stream_with_context(generate_csv_rows()), mimetype='text/csv')
        cd = 'attachment; filename=sandpiper_v{}_{}_{}_sample_coverage.csv'.format(__version__, taxon, taxonomy_type)
        response.headers['Content-Disposition'] = cd
        return response
    else:
        return condensed_profile_hits # Really returning a JSON indicating the failure


@api.route('/taxonomy_search_csv_minimal/<string:taxon>', methods=('GET',))
def taxonomy_search_csv_minimal(taxon):
    taxonomy_type = request.args.get('taxonomy_type', 'gtdb')
    worked, condensed_profile_hits = taxonomy_search_core(
        taxon, request.args, no_limit=True, include_extras=False
    )

    if worked:
        headers = [
            'run', 'environment', 'release_year', 'relative_abundance_percent', 'coverage'
        ]

        def generate_csv_rows():
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(headers)
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            try:
                while True:
                    chunk = condensed_profile_hits.fetchmany(1000)
                    if not chunk:
                        break
                    for c in chunk:
                        environment = (
                            "unspecified"
                            if c.taxon_name is None
                            else c.taxon_name.replace(' metagenome', '')
                        )
                        release_year = c.published.strftime('%Y') if c.published else None
                        writer.writerow([
                            c.acc,
                            environment,
                            release_year,
                            round(c.relative_abundance * 100, 2),
                            round(c.filled_coverage, 2),
                        ])
                    yield buffer.getvalue()
                    buffer.seek(0)
                    buffer.truncate(0)
            finally:
                condensed_profile_hits.close()

        response = Response(stream_with_context(generate_csv_rows()), mimetype='text/csv')
        cd = 'attachment; filename=sandpiper_v{}_{}_{}_runs.csv'.format(
            __version__, taxon, taxonomy_type
        )
        response.headers['Content-Disposition'] = cd
        return response
    else:
        return condensed_profile_hits # Really returning a JSON indicating the failure

def taxonomy_search_core(taxon, args, no_limit=False, include_extras=False):
    '''Returns (bool, iterable|json) where bool is whether it worked (True)
    or not (False) and iterable is the data to render. json is the error if
    it failed.'''

    sort_field = args.get('sort_field')
    sort_direction = args.get('sort_direction')
    page = args.get('page')
    page_size = args.get('page_size')
    taxonomy_type = args.get('taxonomy_type', 'gtdb')
    sort_field = 'relative_abundance' if sort_field is None else sort_field
    sort_direction = 'desc' if sort_direction is None else sort_direction
    page = int(page) if page is not None else 0
    page_size = int(page_size) if page_size is not None else 100

    if sort_field not in ['relative_abundance', 'coverage', 'release_year']:
        return False, jsonify({ 'error': 'invalid sort field' })
    if sort_direction not in ['asc', 'desc']:
        return False, jsonify({ 'error': 'invalid sort direction' })

    taxonomy = Taxonomy.query.filter_by(name=taxon, taxonomy_type=taxonomy_type).first()
    if taxonomy is None:
        return False, taxonomy_not_found_response(taxon)
    else:
        total_num_hits = CondensedProfileCtas1.query.filter_by(taxonomy_id=taxonomy.id).count()
        if total_num_hits == 0:
            return False, taxonomy_not_found_response(taxon)
        # Query for samples that contain this taxon
        if include_extras:
            stmt = select(
                NcbiMetadata.acc,
                CondensedProfileCtas1.relative_abundance,
                CondensedProfileCtas1.filled_coverage,
                NcbiMetadata.taxon_name,
                NcbiMetadata.study_title,
                NcbiMetadata.published,
                ParsedSampleAttribute.host_or_not_mature,
                ParsedSampleAttribute.latitude,
                ParsedSampleAttribute.longitude,
                NcbiMetadata.bases,
                ParsedSampleAttribute.bacterial_archaeal_bases,
                NcbiMetadata.spots,
                NcbiMetadata.read1_length_average,
                NcbiMetadata.read2_length_average,
                NcbiMetadata.model,
                ParsedSampleAttribute.collection_year,
                ParsedSampleAttribute.smf,
                ParsedSampleAttribute.smf_warning,
                ParsedSampleAttribute.known_species_fraction,
                ParsedSampleAttribute.globdb_known_species_fraction,
            ).where(CondensedProfileCtas1.run_id == NcbiMetadata.id
            ).where(ParsedSampleAttribute.run_id == NcbiMetadata.id)
        else:
            stmt = select(
                NcbiMetadata.acc,
                CondensedProfileCtas1.relative_abundance,
                CondensedProfileCtas1.filled_coverage,
                NcbiMetadata.taxon_name,
                NcbiMetadata.published,
                # TODO: Add experiment title here, not currently in DB
            ).where(CondensedProfileCtas1.run_id == NcbiMetadata.id)

        
        if sort_field == 'relative_abundance':
            if sort_direction == 'desc':
                hits_query = stmt.order_by(CondensedProfileCtas1.relative_abundance.desc())
            else:
                hits_query = stmt.order_by(CondensedProfileCtas1.relative_abundance.asc())
        elif sort_field == 'coverage':
            if sort_direction == 'desc':
                hits_query = stmt.order_by(CondensedProfileCtas1.filled_coverage.desc())
            else:
                hits_query = stmt.order_by(CondensedProfileCtas1.filled_coverage.asc())
        elif sort_field == 'release_year':
            if sort_direction == 'desc':
                hits_query = stmt.order_by(NcbiMetadata.published.desc())
            else:
                hits_query = stmt.order_by(NcbiMetadata.published.asc())

        if not no_limit:
            hits_query = hits_query.limit(page_size).offset((page-1)*page_size)
            
        hits_query = hits_query.where(CondensedProfileCtas1.taxonomy_id == taxonomy.id)
        if no_limit:
            hits_query = hits_query.execution_options(stream_results=True)

        condensed_profile_hits = db.session.execute(hits_query)

        return True, condensed_profile_hits


@api.route('/taxonomy_search_hints/<string:taxon>', methods=('GET',))
def taxonomy_search_hints(taxon):
    if len(taxon) < 3: return jsonify(['3 or more characters are required'])
    taxonomy_type = request.args.get('taxonomy_type', None)

    # Underscores are wildcards, but we don't want that since there are names like p__Actinobacteria
    search = '%'+taxon.lower().replace('_','\\_')+'%'
    if taxonomy_type is None:
        sql = (
            "select name from taxonomies "
            "where lower(name) like :taxon escape \'\\' "
            "order by taxonomy_type, name limit 30"
        )
        results = db.session.execute(text(sql), {'taxon': search})
    else:
        sql = (
            "select name from taxonomies where taxonomy_type = :taxonomy_type "
            "and lower(name) like :taxon escape \'\\' order by name limit 30"
        )
        results = db.session.execute(text(sql), {'taxon': search, 'taxonomy_type': taxonomy_type})
    taxonomies = []
    for r in results:
        taxonomies.append(r)
    if len(taxonomies) == 0:
        return jsonify(['no taxonomy found for '+taxon])

    return jsonify({ 'taxonomies': [t.name for t in taxonomies] })

def get_lat_lons(taxonomy_id, max_to_show):
    lat_lon_db_entries = db.session.execute(
        select(NcbiMetadata.acc, ParsedSampleAttribute.latitude, ParsedSampleAttribute.longitude, NcbiMetadata.study_title, CondensedProfileCtas1.relative_abundance).where(
            CondensedProfileCtas1.taxonomy_id == taxonomy_id).where(
            NcbiMetadata.id == ParsedSampleAttribute.run_id).where(
            NcbiMetadata.id == CondensedProfileCtas1.run_id).where(
            ParsedSampleAttribute.latitude.is_not(None)
            ).order_by(CondensedProfileCtas1.relative_abundance.desc(), CondensedProfileCtas1.run_id).limit(max_to_show).distinct()).fetchall()

    lat_lons = {}
    lat_lons_count = 0
    min_lat_lon_relabund = None
    for (sample_name, lat, lon, description, _relabund) in lat_lon_db_entries:
        lat_lons_count += 1
        mykey = '%s %s' % (lat, lon)
        if mykey in lat_lons:
            if description in lat_lons[mykey]['samples']:
                lat_lons[mykey]['samples'][description].append(sample_name)
            else:
                lat_lons[mykey]['samples'][description] = [sample_name]
        else:
            lat_lons[mykey] = {'lat_lon': [lat, lon], 'samples': {description: [sample_name]}}
    if len(lat_lon_db_entries) > 0:
        min_lat_lon_relabund = lat_lon_db_entries[-1][4] # sorted by descending, so last one is the min
    else:
        # Currently occurs for
        # http://localhost:8080/taxonomy/s__Nanoarchaeum%20equitans where there
        # are no lat lons for any sample where this taxon is found.
        min_lat_lon_relabund = 0
    return list(lat_lons.values()), lat_lons_count, min_lat_lon_relabund

@api.route('/otus/<string:acc>', methods=('GET',))
def otus(acc):
    global sandpiper_taxonomy_id_to_full_name, sandpiper_marker_id_to_name

    # Doesn't usually cache anything, but useful to have here for testing
    generate_cache()

    run_id = NcbiMetadata.query.filter_by(acc=acc).first().id
    if run_id is None:
        return jsonify({ 'error': 'no run found for acc '+acc })

    otus = OtuIndexed.query.filter_by(run_id=run_id).order_by(OtuIndexed.id).all()

    df = pd.DataFrame(
        [[
            # gene	sample	sequence	num_hits	coverage	taxonomy
            sandpiper_marker_id_to_name[otu.marker_id],
            acc,
            otu.sequence,
            otu.num_hits,
            otu.coverage,
            ('Root' if otu.taxonomy_id==0 else 'Root; ' + sandpiper_taxonomy_id_to_full_name[otu.taxonomy_id]) if otu.taxonomy_id in sandpiper_taxonomy_id_to_full_name else otu.taxonomy_id
        ] for otu in otus],
        columns=['gene','sample','sequence','num_hits','coverage','taxonomy']
    )
    response = make_response(df.to_csv(index=False, header=True, sep='\t'))
    taxonomy_type = 'gtdb' #TODO: Add GlobDB
    cd = 'attachment; filename=sandpiper_v{}_{}_{}.otu_table.csv'.format(__version__, acc, taxonomy_type)
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response

# ?host=${host}&ecological=${ecological}&two_gbp=${two_gbp}
@api.route('/random_run', methods=('GET',))
def random_run():
    host = request.args.get('host') == 'true'
    ecological = request.args.get('ecological') == 'true'
    two_gbp = request.args.get('two_gbp') == 'true'

    stmt = select(NcbiMetadata.acc).order_by(func.random())
    if host==True and ecological==True:
        # Nothing to do
        pass
    elif host==True:
        stmt = stmt.where(
            NcbiMetadata.id == ParsedSampleAttribute.run_id).where(
                ParsedSampleAttribute.host_or_not_mature=='host'
            )
    elif ecological==True:
        stmt = stmt.where(
            NcbiMetadata.id == ParsedSampleAttribute.run_id).where(
                ParsedSampleAttribute.host_or_not_mature=='ecological'
            )

    if two_gbp == True:
        stmt = stmt.where(NcbiMetadata.bases >= 2e9)

    ran = db.session.execute(stmt).fetchone()

    return jsonify({
        'run': ran.acc
    })

def related_run_query(example_run):
    if example_run.study_abstract is None or example_run.study_abstract == '':
        q = NcbiMetadata.query.filter_by(study_title=example_run.study_title)
    else:
        q = NcbiMetadata.query.filter_by(study_abstract=example_run.study_abstract)
    return q.join(ParsedSampleAttribute).add_columns(
        ParsedSampleAttribute.smf,
        ParsedSampleAttribute.smf_warning,
        ParsedSampleAttribute.known_species_fraction)

@api.route('/project', methods=('GET',))
def project():
    projects = []
    # if request.args.get('bioproject') is not None:
    #     projects.extend(NcbiMetadata.query.filter_by(bioproject=request.args.get('bioproject')).all())
    if request.args.get('model_bioproject') is not None:
        # Match for new samples based on the study abstract, which JGI keeps constant, I think
        example_run = NcbiMetadata.query.filter_by(bioproject=request.args.get('model_bioproject')).first()
        if example_run is None:
            return jsonify({ 'error': 'no run found for bioproject '+request.args.get('model_bioproject') })
        projects.extend(related_run_query(example_run).all())
    if projects == []:
        return jsonify({ 'error': 'No runs found' })
    else:
        # Sort projects by run acc, numerically after removing the SRR/DRR/etc prefix
        projects.sort(key=lambda x: int(x[0].acc[3:]))
        return jsonify({
            'study_abstract': projects[0][0].study_abstract,
            'smf_mean': round(sum([p[1] for p in projects]) / len(projects), 0),
            'known_species_mean': round(sum([p[3] for p in projects])*100 / len(projects), 0),
            'projects': [{
                'acc': p[0].acc,
                'study_title': p[0].study_title,
                'sample_name': p[0].sample_name,
                'library_name': p[0].library_name,
                'experiment_title': p[0].experiment_title,
                'gbp': round(p[0].bases/1e9, 2),
                'smf': p[1],
                'smf_warning': p[2],
                'known_species_fraction': round(p[3]*100,1),
            } for p in projects]
        })

def related_run_count(model_bioproject):
    example_run = NcbiMetadata.query.filter_by(bioproject=model_bioproject).first()
    if example_run is None:
        return 0
    return related_run_query(example_run).count()
        
@api.route('/accession/<string:acc>', methods=('GET',))
def accession(acc):
    acc = acc.strip()
    # If it is a bioproject, then return that and a model bioproject
    bioproject_example = NcbiMetadata.query.filter(or_(
        NcbiMetadata.bioproject==acc, # These columns need to be indexed
        NcbiMetadata.sra_study==acc
    )).first()
    if bioproject_example is not None:
        return jsonify({
            #   const result_type = response.data.result_type
            #   const acc = response.data.accession
            'result_type': 'project',
            'accession': bioproject_example.bioproject,
        })
    
    run_example = NcbiMetadata.query.filter(or_(
        NcbiMetadata.acc == acc, 
        NcbiMetadata.experiment == acc, # These columns need to be indexed
        NcbiMetadata.biosample == acc,
        NcbiMetadata.sample_acc == acc,
    )).first()
    if run_example is not None:
        return jsonify({
            'result_type': 'run',
            'accession': run_example.acc,
        })
    else:
        return jsonify({ 
            'result_type': 'fail',
            'error': 'No accession identified when searching for "'+acc+'". Please let us know if you believe this is a valid identifier.'})


RECAPTCHA_SECRET_KEY = '6LdZXhorAAAAAJOtcFJj6SBkOKW4bhKu80khNcH2'


@api.route('/verify-recaptcha', methods=['POST'])
def verify_recaptcha():
    data = request.json
    token = data.get('recaptchaResponse')
    if token is None:  # Sometimes get either (in localhost testing at least)? Bit confused as to why
        token = data.get('token')

    if not token:
        return jsonify(success=False, message='No token provided'), 400

    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': token
        }
    )

    result = response.json()

    if result.get('success'):
        return jsonify(success=True)
    else:
        return jsonify(success=False, errors=result.get('error-codes', [])), 400
