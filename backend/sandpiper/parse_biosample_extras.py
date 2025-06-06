#!/usr/bin/env python3

import re
import argparse
import logging
import sys
import os
import polars as pl
from datetime import datetime

import iso8601

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

ACTUALLY_MISSING = set([None]+[s.lower() for s in [
    'missing','not applicable','NA','Missing','Not collected','not provided','Missing: Not provided','', 'uncalculated','not applicable','no applicable','unspecified','restricted access']])

def validate_lat_lon(lat, lon):
    if lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180:
        return True
    return False

def parse_json_to_lat_lon_dict(j):
    lat_long_dict = {}

    biosample_keys_for_lat_long_parsing = LAT_LON_KEYS

    for attr in j['attributes']:
        if attr['k'] in biosample_keys_for_lat_long_parsing and attr['v'].lower() not in ACTUALLY_MISSING:
            lat_long_dict[attr['k']] = attr['v']
    logging.debug("Parsed lat_long_dict: %s" % lat_long_dict)
    return lat_long_dict

def parse_lat_lon_sam(lat_lon_sam):
    lat_lon_regex = re.compile('^([0-9.-]+) {0,1}([NSns]),{0,1} {0,1}([0-9.-]+) ([EWew])$')
    matches = lat_lon_regex.match(lat_lon_sam)
    if matches is None:
        logging.warning("Unexpected lat_lon_sam value: %s" % lat_lon_sam)
        return False, False
    try:
        lat = float(matches.group(1))
    except ValueError:
        logging.warning("Unexpected lat_lon_sam value: %s" % lat_lon_sam)
        return False, False
    if matches.group(2) in ['S','s']:
        lat = -lat
    try:
        lon = float(matches.group(3))
    except ValueError:
        logging.warning("Unexpected lat_lon_sam value: %s" % lat_lon_sam)
        return False, False
    if matches.group(4) in ['W','w']:
        lon = -lon
    if validate_lat_lon(lat, lon):
        return True, (lat, lon)
    else:
        logging.warning("Unvalidated lat_lon_sam value: %s" % lat_lon_sam)

def degrees_minutes_to_decimal(degrees, minutes, seconds=0):
    if seconds == '':
        seconds = 0
    return float(degrees) + float(minutes) / 60.0 + float(seconds) / 3600.0

def parse_two_part_lat_lon(sample_name, lat_input, lon_input):
    geoloc_lat_regex = re.compile(r'^([0-9.-]+)[°\?]{0,1} {0,1}([NSns])$')
    geoloc_lon_regex = re.compile(r'^([0-9.-]+)[°\?]{0,1} {0,1}([EWew])$')
    # e.g. S 12°37.707′
    sexigesimal_regex_lat1 = re.compile(r'^([NSns]) ([0-9]+)[°\?]([0-9.]+)[\'′]$')
    sexigesimal_regex_lon1 = re.compile(r'^([EWew]) ([0-9]+)[°\?]([0-9.]+)[\'′]$')
    # e.g. 52?09'50.8N
    sexigesimal_regex_lat2 = re.compile(r'^([0-9]+)[°\?]([0-9.]+)[\'′]([0-9.]*)([NSns])$')
    sexigesimal_regex_lon2 = re.compile(r'^([0-9]+)[°\?]([0-9.]+)[\'′]([0-9.]*)([EWew])$')
    # e.g.  ERR2824916: ["S33°28'21.68", "O70°38'50.06"] -> Actually that one is fail
    sexigesimal_regex_lat3 = re.compile(r'^([NSns])([0-9]+)[°\?]([0-9.]+)[\'′]([0-9.]*)$')
    sexigesimal_regex_lon3 = re.compile(r'^([EWew])([0-9]+)[°\?]([0-9.]+)[\'′]([0-9.]*)$')
    # e.g. ERR5173566: ['N 43.8047886', 'E 15.9637432']
    geoloc_lat_regex2 = re.compile(r'^([NSns]) {0,1}([0-9.-]+)[°\?]{0,1}$')
    geoloc_lon_regex2 = re.compile(r'^([EWew]) {0,1}([0-9.-]+)[°\?]{0,1}$')

    try:
        lat = float(lat_input)
        lon = float(lon_input)
    except ValueError:
        # Try comma to dot and then convert
        try:
            lat = float(lat_input.replace(',','.'))
            lon = float(lon_input.replace(',','.'))
        except ValueError:
            matches_lat = geoloc_lat_regex.match(lat_input)
            matches_lon = geoloc_lon_regex.match(lon_input)
            if matches_lat is not None and matches_lon is not None:
                try:
                    lat = float(matches_lat.group(1))
                    lon = float(matches_lon.group(1))
                    if matches_lat.group(2) in ['S','s']:
                        lat = -lat
                    if matches_lon.group(2) in ['W','w']:
                        lon = -lon
                except ValueError:
                    logging.warning("Unexpected (type 1) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                    return False, False
            else:
                # Try sexigesimal
                matches_lat1 = sexigesimal_regex_lat1.match(lat_input)
                matches_lon1 = sexigesimal_regex_lon1.match(lon_input)
                if matches_lat1 is not None and matches_lon1 is not None:
                    try:
                        lat = degrees_minutes_to_decimal(matches_lat1.group(2), matches_lat1.group(3))
                        lon = degrees_minutes_to_decimal(matches_lon1.group(2), matches_lon1.group(3))

                        if matches_lat1.group(1) in ['S','s']: lat = -lat
                        if matches_lon1.group(1) in ['W','w']: lon = -lon
                    except ValueError:
                        logging.warning("Unexpected (type 2) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                        return False, False
                else:
                    matches_lat2 = sexigesimal_regex_lat2.match(lat_input)
                    matches_lon2 = sexigesimal_regex_lon2.match(lon_input)
                    if matches_lat2 is not None and matches_lon2 is not None:
                        try:
                            lat = degrees_minutes_to_decimal(matches_lat2.group(1), matches_lat2.group(2), matches_lat2.group(3))
                            lon = degrees_minutes_to_decimal(matches_lon2.group(1), matches_lon2.group(2), matches_lon2.group(3))

                            if matches_lat2.group(4) in ['S','s']: lat = -lat
                            if matches_lon2.group(4) in ['W','w']: lon = -lon
                        except ValueError:
                            logging.warning("Unexpected (type 4) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                            return False, False
                    else:
                        matches_lat3 = sexigesimal_regex_lat3.match(lat_input)
                        matches_lon3 = sexigesimal_regex_lon3.match(lon_input)
                        if matches_lat3 is not None and matches_lon3 is not None:
                            try:
                                lat = degrees_minutes_to_decimal(matches_lat3.group(2), matches_lat3.group(3), matches_lat3.group(4))
                                lon = degrees_minutes_to_decimal(matches_lon3.group(2), matches_lon3.group(3), matches_lon3.group(4))

                                if matches_lat3.group(1) in ['S','s']: lat = -lat
                                if matches_lon3.group(1) in ['W','w']: lon = -lon
                            except ValueError:
                                logging.warning("Unexpected (type 5) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                                return False, False
                        else:
                            matches_lat4 = geoloc_lat_regex2.match(lat_input)
                            matches_lon4 = geoloc_lon_regex2.match(lon_input)
                            if matches_lat4 is not None and matches_lon4 is not None:
                                try:
                                    lat = float(matches_lat4.group(2))
                                    lon = float(matches_lon4.group(2))
                                    if matches_lat4.group(1) in ['S','s']: lat = -lat
                                    if matches_lon4.group(1) in ['W','w']: lon = -lon
                                except ValueError:
                                    logging.warning("Unexpected (type 6) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                                    return False, False
                            else:
                                logging.warning("Unexpected (no regex match) 2 part value for %s: %s" % (sample_name, [lat_input, lon_input]))
                                return False, False
                    


    if lat and lon and validate_lat_lon(lat, lon):
        return True, (lat, lon)
    else:
        logging.warning("Unvalidated 2-part value: %s / %s" % (lat_input, lon_input))
        return False, False

def parse_temp(acc, temp):
    if temp.lower() in ACTUALLY_MISSING:
        return ''
    
    endings = ['°C','C','°c','c',' celcius']
    temp2 = temp
    for e in endings:
        if temp2.endswith(e):
            temp2 = temp2[:-len(e)]

    if ',' in temp2:
        # Replace comma with dot
        temp2 = temp2.replace(',', '.')

    try:
        if '.' in temp2:
            # Cast as float only if there is a decimal point
            f = float(temp2)
        else:
            f = int(temp2)
        if f > 100: # SRR12345782 has 255C
            logging.warning("Too big temperature value for %s: %s from %s" % (acc, temp2, temp))
            return ''
        return f
    except ValueError:
        logging.warning("Unexpected temperature value for %s: %s from %s" % (acc, temp2, temp))
        return ''

def parse_depth(acc, depth):
    if depth.lower() in ACTUALLY_MISSING:
        return ''
    
    depth2 = depth

    cm_endings = ['cm','centimeters','centimeter','centimetres','centimetre']
    is_cm = False # Assume metres
    for e in cm_endings:
        if depth2.endswith(e):
            depth2 = depth2[:-len(e)]
            is_cm = True

    if not is_cm:
        endings = ['m','meters','meter','metres','metre']
        for e in endings:
            if depth2.endswith(e):
                depth2 = depth2[:-len(e)]

    try:
        # Cast as float only if there is a decimal point
        if '.' in depth2:
            if is_cm:
                return float(depth2) / 100.0
            else:
                return float(depth2)
        else:
            if is_cm:
                return float(depth2) / 100.0
            else:
                return int(depth2)
    except ValueError:
        logging.warning("Unexpected depth value for %s: %s from %s" % (acc, depth2, depth))
        return ''

def parse_date(acc, date):
    if date.lower() in ACTUALLY_MISSING:
        return ''

    try:
        d = iso8601.parse_date(date)
    except iso8601.ParseError:
        logging.warning("Unexpected date value for %s: %s" % (acc, date))
        return ['']*2
    
    if d.year < 1990 or d.year > datetime.now().year:
        logging.warning("Unexpected year value for %s: %s" % (acc, date))
    else:
        return [d.year, d.month]

    logging.warning("Unexpected date value for %s: %s" % (acc, date))
    return ['']*2

    # import IPython; IPython.embed()

    # for format in [
    #     '%Y-%m-%d', # ERR2604420
    #     '%Y-%m', # SRR11296602
    #     '%m/%d/%y', # ERR557315
    # ]:
    #     try:
    #         d = datetime.strptime(date, format)
    #         if d.year < 2000 or d.year > datetime.now().year:
    #             logging.warning("Unexpected year value for %s: %s" % (acc, date))
    #         else:
    #             return [d.year, d.month]
    #     except ValueError:
    #         pass
    
    # logging.warning("Unexpected date value for %s: %s" % (acc, date))
    # return ['']*2

def parse_lat_lons(acc, lat_long_dict):
    to_return = []

    got_a_lat_lon = False
    for k in LAT_LON_SINGLE_PART_KEYS:
        if k in lat_long_dict:
            returned = parse_lat_lon_sam(lat_long_dict[k])
            if returned is not None:  # Happens when validation fails
                got_a_lat_lon, lat_lon = returned
                if got_a_lat_lon:
                    to_return.append(lat_lon[0])
                    to_return.append(lat_lon[1])
                    break

    if not got_a_lat_lon:
        for k in LAT_LON_TWO_PART_KEYS:
            if k[0] in lat_long_dict and k[1] in lat_long_dict:
                got_a_lat_lon, lat_lon = parse_two_part_lat_lon(acc, lat_long_dict[k[0]], lat_long_dict[k[1]])
                if got_a_lat_lon:
                    to_return.append(lat_lon[0])
                    to_return.append(lat_lon[1])
                    break

    if not got_a_lat_lon:
        to_return.append(None)
        to_return.append(None)

    return to_return


LAT_LON_SINGLE_PART_KEYS = [
    'lat_lon',
    'geographic location (latitude and longitude)'
]
LAT_LON_TWO_PART_KEYS = [
    ['geographic location (latitude)',
    'geographic location (longitude)'],
    ['latitude_start',
    'longitude_start'],
    ['latitude',
    'longitude'],
    ['sampling event (latitude)_start',
    'sampling event (longitude)_start'],
]
LAT_LON_KEYS = LAT_LON_SINGLE_PART_KEYS + [item for sublist in LAT_LON_TWO_PART_KEYS for item in sublist]

# Special parsing methods
parsing_hash = {
    'depth': parse_depth,
    'temperature': parse_temp,
    'collection_date': parse_date,
}
# For when the number of fields returned by parsing != 1
non_standard_output_field_names_hash = {
    'collection_date': ['collection_year', 'collection_month'],
}

def parse_attribute_fields(j, extra_sample_keys):
    result_hash = {}

    for attr in j['attributes']:
        if attr['v'] and attr['k'] in extra_sample_keys and attr['v'].lower() not in ACTUALLY_MISSING:
            if attr['k'] in parsing_hash:
                # Special parsing function
                result_hash[attr['k']] = parsing_hash[attr['k']](j['acc'], attr['v'])
            else:
                # Just output as-is (except if ACTUALLY_MISSING)
                result_hash[attr['k']] = [attr['v']]
    return result_hash


def parse_extra_sample_attributes(j, extra_sample_keys):
    result_hash = parse_attribute_fields(j, extra_sample_keys)

    to_return = []
    for k in extra_sample_keys:
        if k in result_hash:
            if k in non_standard_output_field_names_hash:
                to_return.extend(result_hash[k])
            else:
                to_return.append(result_hash[k])
        else:
            if k in non_standard_output_field_names_hash:
                to_return.extend(['']*len(non_standard_output_field_names_hash[k]))
            else:
                to_return.append('')

    return to_return

def prepare_attributes(attributes):
    # start by removing __sam from the end of each key, and also anythi9ng matching _sam_.* e.g. lat_lon_sam_s_dpl34
    re1 = re.compile(r'_{1,2}sam$')
    re2 = re.compile(r'_sam_.*$')

    attr2 = []
    for attr in attributes:
        if attr['v'] is None:
            continue
        # apply re1 and re2, replace with ''
        real_key = re1.sub('', attr['k'])
        real_key = re2.sub('', real_key)
        # temp -> temperature
        if real_key == 'temp':
            real_key = 'temperature'
        if real_key in attr2:
            logging.warning("Duplicate key %s in attributes for %s" % (real_key, j['acc']))
        attr2.append({'k': real_key, 'v': attr['v']})
    return attr2


if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    # parent_parser.add_argument('--json-input', help='json from bigquery, one json per line', required=True)
    parent_parser.add_argument('--kingfisher-annotate-tsvs', help='CSV files generated by kingfisher annotate -f tsv', required=False, nargs='+')
    parent_parser.add_argument('--kingfisher-annotate-tsv-list', help='newline separated list of CSV files generated by kingfisher annotate -f tsv', required=False)

    parent_parser.add_argument('--extra-sample-keys', help='output these values from the sample k/v pairs', nargs='+', default=[])
    parent_parser.add_argument('--extra-attributes', help='extra attributes to output', nargs='+', default=[])

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    extra_attributes = args.extra_attributes
    extra_sample_keys = args.extra_sample_keys

    headers = ['run', 'latitude', 'longitude']+extra_attributes

    for k in extra_sample_keys:
        if k in non_standard_output_field_names_hash:
            headers.extend(non_standard_output_field_names_hash[k])
        else:
            headers.append(k)

    tsvs = args.kingfisher_annotate_tsvs
    if tsvs is None:
        tsvs = []
    if args.kingfisher_annotate_tsv_list:
        with open(args.kingfisher_annotate_tsv_list) as f:
            for line in f:
                line = line.strip()
                if line:
                    tsvs.append(line)
    if len(tsvs) == 0:
        logging.error("No TSV files provided")
        sys.exit(1)
    
    logging.info("Processing %d TSV files" % (len(tsvs)))
    print('\t'.join(headers))
    for path in tsvs:
        if not os.path.exists(path):
            raise Exception("File %s does not exist" % path)

        # no casting of columns
        df = pl.read_csv(path, separator='\t', has_header=True, infer_schema=False)
        
        for row in df.rows(named=True):
            j = {
                'acc': row['run'],
                'attributes': []
            }
            for col in df.columns:
                if col in ['run', 'Gbp']: continue

                if row[col] is None or row[col] in ACTUALLY_MISSING:
                    continue
                j['attributes'].append({'k': col, 'v': row[col]})

            # start by removing __sam from the end of each key, and also anythi9ng matching _sam_.* e.g. lat_lon_sam_s_dpl34
            # (needed any more?)
            j['attributes'] = prepare_attributes(j['attributes'])

            lat_long_res = [j['acc']]
            lat_lon = parse_lat_lons(j['acc'], parse_json_to_lat_lon_dict(j))
            if lat_lon == [None, None]:
                lat_long_res.append('')
                lat_long_res.append('')
            else:
                lat_long_res.extend(lat_lon)

            for k in extra_attributes:
                if k in j:
                    lat_long_res.append(j[k])
                else:
                    lat_long_res.append('')

            lat_long_res.extend(parse_extra_sample_attributes(j, extra_sample_keys))

            print('\t'.join([str(s) for s in lat_long_res]))



        # 2019-08-01T09:00:09Z