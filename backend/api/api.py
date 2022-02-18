"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request
from .models import NcbiMetadata, db, Marker, Otu, CondensedProfile, Taxonomy

from singlem.condense import WordNode

api = Blueprint('api', __name__)

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
    j = {
        'name': wordnode.word,
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
