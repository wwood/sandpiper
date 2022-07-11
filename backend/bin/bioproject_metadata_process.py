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

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    parent_parser.add_argument('--xml-directory', required=True)

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # Gather XML entries
    import glob
    xmls = glob.glob('{}/*.xml'.format(args.xml_directory))
    logging.info("Found {} XML files to process".format(len(xmls)))
    print('\t'.join(['bioproject','db','id']))

    for xlm in tqdm(xmls, total=len(xmls)):
        with open(xlm) as f:
            xml = f.read()
        root = ET.fromstring(xml)
        
        projects = root.findall('DocumentSummary/Project')
        for project in projects:
            publications = project.findall("ProjectDescr/Publication")
            if len(publications) > 0:
                bioproject = project.find("ProjectID/ArchiveID").attrib['accession']
                for pub in publications:
                    dbtype = pub.find('DbType').text
                    pub_id = pub.attrib['id']
                    print("{}\t{}\t{}".format(bioproject, dbtype, pub_id))
        