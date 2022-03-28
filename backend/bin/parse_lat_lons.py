#!/usr/bin/env python3

import re
import argparse
import logging
import sys
import os

from sqlalchemy import select, distinct
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, lazyload, defaultload, load_only

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path
from api.application import create_app
from api.models import *


def validate_lat_lon(lat, lon):
    if lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180:
        return True
    return False

def parse_lat_lons():
    lat_lon_db_entries = NcbiMetadata.query.join(NcbiMetadata.biosample_attributes).with_entities(
        NcbiMetadata.id, NcbiMetadata.acc, BiosampleAttribute.k, BiosampleAttribute.v).where(
        BiosampleAttribute.k.in_(
            ['lat_lon_sam','geographic_location__latitude__sam','geographic_location__longitude__sam'])).where(
                BiosampleAttribute.v.not_in(['missing','not applicable','NA','Missing','Not collected','Not applicable','not collected','Not Collected','Not Applicable'])
            ).order_by(NcbiMetadata.id).all()

    # print('db entry hits: '+str(lat_lon_db_entries))

    lat_lon_regex = re.compile('^([0-9.-]+) {0,1}([NSns]),{0,1} {0,1}([0-9.-]+) ([EWew])$')
    geoloc_lat_regex = re.compile('^([0-9.-]+) {0,1}([NSns])$')
    geoloc_lon_regex = re.compile('^([0-9.-]+) {0,1}([EWew])$')

    previous_sample = None
    previous_geographic_lat_or_lon = None

    for (ncbi_metadata_id, sample_name, k, v) in lat_lon_db_entries:
        if v is None:
            continue
        # print((sample_name, k, v, previous_sample, previous_geographic_lat_or_lon))
        if k == 'lat_lon_sam':
            matches = lat_lon_regex.match(v)
            if matches is None:
                logging.warning("Unexpected lat_lon_sam value: %s" % v)
                continue
            lat = float(matches.group(1))
            if matches.group(2) in ['S','s']:
                lat = -lat
            try:
                lon = float(matches.group(3))
            except ValueError:
                logging.warning("Unexpected lat_lon_sam value: %s" % v)
                continue
            if matches.group(4) in ['W','w']:
                lon = -lon
            if validate_lat_lon(lat, lon):
                yield ncbi_metadata_id, sample_name, lat, lon
        else:
            if sample_name != previous_sample:
                previous_geographic_lat_or_lon = [k, v]
            else:
                if k == 'lat_lon_sam':
                    continue # duplicate entry (unless it doesn't validate, eh..)
                if previous_geographic_lat_or_lon is None:
                    previous_geographic_lat_or_lon = [k, v]
                else:
                    if len(set((k, previous_geographic_lat_or_lon[0]))) == 2:
                        lat = None
                        lon = None
                        if k == 'geographic_location__latitude__sam':
                            lat_input = v
                            lon_input = previous_geographic_lat_or_lon[1]
                        elif k == 'geographic_location__longitude__sam':
                            lat_input = previous_geographic_lat_or_lon[1]
                            lon_input = v
                        else:
                            logging.warning("Unexpected 1 geographic_location__latitude__sam or geographic_location__longitude__sam value for %s: %s" % (sample_name, [v, previous_geographic_lat_or_lon]))
                            continue

                        try:
                            lat = float(lat_input)
                            lon = float(lon_input)
                        except ValueError:
                            matches_lat = geoloc_lat_regex.match(lat_input)
                            matches_lon = geoloc_lon_regex.match(lon_input)
                            if matches_lat is None or matches_lon is None:
                                logging.warning("Unexpected 2 geographic_location__latitude__sam or geographic_location__longitude__sam value for %s: %s" % (sample_name, [lat_input, lon_input]))
                                continue
                            lat = float(matches_lat.group(1))
                            lon = float(matches_lon.group(1))
                            if matches_lat.group(2) in ['S','s']:
                                lat = -lat
                            if matches_lon.group(2) in ['W','w']:
                                lon = -lon
                        previous_geographic_lat_or_lon = None

                        if lat and lon and validate_lat_lon(lat, lon):
                            yield ncbi_metadata_id, sample_name, lat, lon
                    else:
                        logging.warning("Unexpected 3 geographic_location__latitude__sam or geographic_location__longitude__sam value: %s" % [sample_name, k, v, previous_geographic_lat_or_lon])
                        continue
            
        previous_sample = sample_name

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    parent_parser.add_argument('--sandpiper-db', help='sqlite file from sandpiper', required=True)

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.warn("There is better code for this at big_data/3")

    sqlite_db_path = args.sandpiper_db

    # Create the app and create the tables
    from api.application import create_app
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + sqlite_db_path
    app.config['SQLALCHEMY_ECHO'] = args.debug is True
    db = SQLAlchemy(app)

    with app.app_context():
        for (_ncbi_metadata_id, sample_name, lat, lon) in parse_lat_lons():
            print('\t'.join([sample_name, str(lat), str(lon)]))