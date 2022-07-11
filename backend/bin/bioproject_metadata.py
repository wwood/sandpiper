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
from tqdm import tqdm

from bird_tool_utils import iterable_chunks


NCBI_API_KEY_ENV = 'NCBI_API_KEY'
def add_api_key(other_params):
    if NCBI_API_KEY_ENV in os.environ:
        other_params['api_key'] = os.environ[NCBI_API_KEY_ENV]
    return other_params

def _retry_request(description, func):
    '''Retry a reqests.post or requests.get 3 times, returning the request
    when OK, otherwise raising an Exception'''

    num_retries = 3
    sleep_time = 60
    def retrying(i, num_retries=3):
        if i < num_retries-1:
            logging.warning("Retrying request (retry {} of {})".format(i+1, num_retries-1))
    
    for i in range(num_retries):
        try:
            this_res = func()
            if not this_res.ok:
                logging.warning("Request not OK when {}: {}: {}".format(description, this_res, this_res.text))
                logging.warning("Sleeping for {} seconds before retrying".format(sleep_time))
                time.sleep(60)
                retrying(i)
            else:
                return this_res
        except Exception as e:
            logging.warning("Exception raised when {}: {}".format(description, e))
            logging.warning("Sleeping for {} seconds before retrying".format(sleep_time))
            time.sleep(60)
            retrying(i)
    raise Exception("Failed to {} after {} attempts".format(description, num_retries))

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    parent_parser.add_argument('--metadata-json-files', nargs='+', required=True)
    parent_parser.output_directory = parent_parser.add_argument('--output-directory', required=True)

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # Read in list of bioproject IDs
    logging.info("Reading metadata ..")
    bioproject_ids = []
    for path in args.metadata_json_files:
        for line in open(path):
            j = json.loads(line)
            if 'bioproject' in j:
                bioproject_ids.append(j['bioproject'])
    logging.info("Found %d bioproject IDs to annotate", len(bioproject_ids))

    # print('\t'.join(['bioproject','db','id']))
    os.makedirs(args.output_directory, exist_ok=True)
    
    chunks = list(iterable_chunks(bioproject_ids, 50))
    for i, chunk in enumerate(tqdm(chunks, total=len(chunks))):
        ids = ','.join([c for c in chunk if c is not None])
        res = _retry_request(
            'efetch_from_bioproject_ids',
            lambda: requests.post(
                url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                data=add_api_key({
                    "db": "bioproject",
                    "id": ids,
                    "tool": "kingfisher",
                    "email": "kingfisher@github.com",
                    }),
                )
        )
        if not res.ok:
            raise Exception("HTTP Failure: {}: {}".format(res, res.text))
        root = ET.fromstring(res.text)
        with open('{}/bioproject_metadata{}.xml'.format(args.output_directory, i), 'wb') as f:
            f.write(ET.tostring(root, encoding='utf-8'))

        # import IPython; IPython.embed()
        #         <Project>
        # <ProjectID>
        # <ArchiveID accession="PRJNA640379" archive="NCBI" id="640379"/>
        # projects = root.findall('DocumentSummary/Project')
        # for project in projects:
        #     publications = project.findall("ProjectDescr/Publication")
        #     if len(publications) > 0:
        #         bioproject = project.find("ProjectID/ArchiveID").attrib['accession']
        #         for pub in publications:
        #             dbtype = pub.find('DbType').text
        #             pub_id = pub.attrib['id']
        #             print("{}\t{}\t{}".format(bioproject, dbtype, pub_id))
            
