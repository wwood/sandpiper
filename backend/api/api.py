"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""
import re

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.sql import func
from .models import NcbiMetadata, db, Marker, Otu, CondensedProfile, Taxonomy

from singlem.condense import WordNode

api = Blueprint('api', __name__)

sandpiper_total_terrabases = None
sandpiper_num_runs = None
sandpiper_num_bioprojects = None

@api.route('/sandpiper_stats', methods=['GET'])
def sandpiper_stats():
    global sandpiper_total_terrabases
    global sandpiper_num_runs
    global sandpiper_num_bioprojects
    # Cache results because they don't change unless the DB changes
    if sandpiper_total_terrabases is None:
        sandpiper_total_terrabases = db.session.query(func.sum(NcbiMetadata.mbases)).scalar()/10**6
    if sandpiper_num_runs is None:
        sandpiper_num_runs = NcbiMetadata.query.distinct(NcbiMetadata.acc).count()
    if sandpiper_num_bioprojects is None:
        sandpiper_num_bioprojects = NcbiMetadata.query.distinct(NcbiMetadata.bioproject).count()
    return jsonify({
        'num_terrabases': round(sandpiper_total_terrabases),
        'num_runs': sandpiper_num_runs,
        'num_bioprojects': sandpiper_num_bioprojects
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

    condensed = CondensedProfile.query.filter_by(sample_name=sample_name).all()
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
        wn.coverage = entry.coverage

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

@api.route('/taxonomy_search/<string:taxon>', methods=('GET',))
def taxonomy_search(taxon):
    taxonomy = Taxonomy.query.filter_by(name=taxon).first()
    if taxonomy is None:
        return jsonify({ 'taxon': 'no taxonomy found for '+taxon })
    else:
        # Query for samples that contain this taxon
        condensed_profile_hits = taxonomy.condensed_profiles
        return jsonify({
            'taxon': taxonomy.split_taxonomy(),
            'condensed_profiles': [{
                'sample_name': c.sample_name,
                'relative_abundance': round(c.relative_abundance*100,2),
                'coverage': c.coverage }
                for c in condensed_profile_hits] })

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
