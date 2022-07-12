#!/usr/bin/env python3

import os
import argparse
import logging
import json
import tempfile

import extern

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # Read accessions file
    test_data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../test/data/6_runs')
    with open(os.path.join(test_data_directory, 'accessions')) as f:
        accessions = f.read().splitlines()
    logging.info("Found %d accessions to annotate", len(accessions))

    # bigquery for the json
    sql = """SELECT
  acc,
  assay_type,
  center_name,
  experiment,
  sample_name,
  instrument,
  libraryselection,
  librarysource,
  platform,
  sample_acc,
  biosample,
  organism,
  sra_study,
  releasedate,
  bioproject,
  avgspotlen,
  mbases,
  insertsize,
  library_name,
  biosamplemodel_sam,
  collection_date_sam,
  geo_loc_name_country_calc,
  geo_loc_name_country_continent_calc,
  geo_loc_name_sam,
  sample_name_sam,
  loaddate,
  attributes
FROM
  `nih-sra-datastore.sra.metadata`
WHERE
  acc IN ('{}')
    """.format('\',\''.join(accessions))

    # logging.info("Running biqquery ..")
    # j = extern.run('bq query --use_legacy_sql=false --format json', stdin=sql)
    # j2 = json.loads(j)
    # with open(os.path.join(test_data_directory, 'metadata_each_line.json'), 'w') as f:
    #     for e in j2:
    #         f.write(json.dumps(e)+'\n')
    # logging.info("Finished bigquery gathering of metadata")

    # logging.info("Gathering OTU tables ..")
    # otu_table_files = []
    # for accession in accessions:
    #     t = tempfile.NamedTemporaryFile()
    #     otu_table_files.append(t)
    #     extern.run("curl https://sandpiper.qut.edu.au/api/otus/{} >{}".format(accession, t.name))
    
    # logging.info("Gathering OTU tables into 1 file ..")
    # extern.run("singlem summarise --input-otu-tables {} --output-otu-table /dev/stdout |gzip >{}".format(
    #     ' '.join([t.name for t in otu_table_files]),
    #     os.path.join(test_data_directory, 'otu_table.csv.gz')))

    logging.info("Condensing OTU tables ..")
    extern.run("singlem condense --input-otu-table <(zcat {}) --metapackage ~/git/singlem/db/S3.metapackage_20211101.smpkg --output-otu-table /dev/stdout |gzip >{}".format(
        os.path.join(test_data_directory, 'otu_table.csv.gz'),
        os.path.join(test_data_directory, 'condensed.csv.gz')))

    logging.info("Finished")