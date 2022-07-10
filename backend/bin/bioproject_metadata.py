#!/usr/bin/env python3

###############################################################################
#
#    Copyright (C) 2021 Ben Woodcroft
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

__author__ = "Ben Woodcroft"
__copyright__ = "Copyright 2022"
__credits__ = ["Ben Woodcroft"]
__license__ = "GPL3"
__maintainer__ = "Ben Woodcroft"
__email__ = "benjwoodcroft near gmail.com"
__status__ = "Development"

import argparse
import logging
import sys
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import json

from bird_tool_utils import iterable_chunks


NCBI_API_KEY_ENV = 'NCBI_API_KEY'
def add_api_key(other_params):
    if NCBI_API_KEY_ENV in os.environ:
        other_params['api_key'] = os.environ[NCBI_API_KEY_ENV]
    return other_params

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    parent_parser.add_argument('--metadata-json-files', nargs='+', required=True)

    args = parent_parser.parse_args()

    # Read in list of bioproject IDs
    bioproject_ids = []
    for path in args.metadata_json_files:
        for line in open(path):
            j = json.loads(line)
            if 'bioproject' in j:
                bioproject_ids.append(j['bioproject'])
    logging.info("Found %d bioproject IDs to annotate", len(bioproject_ids))

    print('\t'.join(['bioproject','db','id']))
    
    for chunk in iterable_chunks(bioproject_ids, 500):
        ids = ','.join([c for c in chunk if c is not None])
        res = requests.post(
            url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params=add_api_key({
                "db": "bioproject",
                "id": ids,
                "tool": "kingfisher",
                "email": "kingfisher@github.com",
                }),
            )
        if not res.ok:
            raise Exception("HTTP Failure: {}: {}".format(res, res.text))
        root = ET.fromstring(res.text)

        # import IPython; IPython.embed()
        #         <Project>
        # <ProjectID>
        # <ArchiveID accession="PRJNA640379" archive="NCBI" id="640379"/>
        projects = root.findall('DocumentSummary/Project')
        for project in projects:
            publications = project.findall("ProjectDescr/Publication")
            if len(publications) > 0:
                bioproject = project.find("ProjectID/ArchiveID").attrib['accession']
                for pub in publications:
                    dbtype = pub.find('DbType').text
                    pub_id = pub.attrib['id']
                    print("{}\t{}\t{}".format(bioproject, dbtype, pub_id))
            