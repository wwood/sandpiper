"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request
from .models import db, Marker, Otu, Nucleotide, CondensedProfile

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
        taxons = entry.taxonomy.split('; ')

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