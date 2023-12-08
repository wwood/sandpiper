#!/usr/bin/env python3

###############################################################################
#
#    Copyright (C) 2020 Ben Woodcroft
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
__copyright__ = "Copyright 2020"
__credits__ = ["Ben Woodcroft"]
__license__ = "GPL3"
__maintainer__ = "Ben Woodcroft"
__email__ = "benjwoodcroft near gmail.com"
__status__ = "Development"

import argparse
import logging
import sys
import os

import extern

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()

    parent_parser.add_argument('--date',required=True, help='date of run e.g. 20111130')
    
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")
    parent_parser.add_argument('--target', help='amplicon or shotgun', choices=['amplicon','shotgun'], required=True)

    args = parent_parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    sql_pretable = """
-- STEP 1: Create temporary table with metagenome taxonomy entries
-- Loop counter
DECLARE counter int64 default 1;

-- Create intermediate table with initial records where employee directly reports
CREATE OR REPLACE TABLE test.emp
AS
WITH cte AS
(
SELECT 1 AS xlevel, tax_id, parent_id, sci_name
FROM `nih-sra-datastore.sra_tax_analysis_tool.taxonomy` e
WHERE e.sci_name = 'metagenomes'
)
SELECT *
FROM cte;

WHILE EXISTS (
SELECT c.*
FROM test.emp p
INNER JOIN `nih-sra-datastore.sra_tax_analysis_tool.taxonomy` c ON p.tax_id = c.parent_id
WHERE p.xlevel = counter
)
DO
-- Insert next level
INSERT INTO test.emp ( xlevel, tax_id, parent_id, sci_name )
SELECT counter + 1 AS xlevel, c.tax_id, c.parent_id, c.sci_name
FROM test.emp p
INNER JOIN `nih-sra-datastore.sra_tax_analysis_tool.taxonomy` c ON p.tax_id = c.parent_id
WHERE p.xlevel = counter;

SET counter = counter + 1;

-- Loop safely
IF counter > 10
THEN
	BREAK;
END IF;
END WHILE;

-- -- Display employee-manger hierarchy
-- -- SELECT  xlevel, tax_id, parent_id, sci_name  FROM test.emp ORDER BY xlevel;
"""

    sql = """
-- STEP 2: Define output

-- Now do the full query 
EXPORT DATA OPTIONS(
  uri='__SQL_JSON_RESULTS_URI__',
  format='JSON') AS

SELECT
-- count(*)
  acc,
  mbases,
  mbytes,
  assay_type,
  releasedate,
  organism,
  libraryselection,
  librarysource,
  bioproject,
  sra_study,
  attributes
FROM
  `nih-sra-datastore.sra.metadata`
WHERE
  acc IN (
  SELECT
    acc
  FROM
    `nih-sra-datastore.sra.metadata`
  WHERE
    (
		librarysource = 'METAGENOMIC'
		 or 
	organism IN (SELECT sci_name FROM test.emp)
	)
    AND platform = 'ILLUMINA'
    AND consent = 'public'
"""

    metagenome_specfic_sql = """
    AND (mbases > 1000
      OR (libraryselection = 'RANDOM'
        AND mbases > 100))
    AND mbases <= 200000
    AND librarysource != 'VIRAL RNA' and librarysource != 'METATRANSCRIPTOMIC' and librarysource != 'TRANSCRIPTOMIC')
;
"""

    amplicon_specific_sql = """
    AND libraryselection = 'PCR'
    AND mbases <= 2000
    AND librarysource != 'VIRAL RNA' and librarysource != 'METATRANSCRIPTOMIC' and librarysource != 'TRANSCRIPTOMIC')
;
"""

    # https://www.ncbi.nlm.nih.gov/sra/?term=SRR12280810 - covid, source VIRAL RNA - want to exclude
    # https://www.ncbi.nlm.nih.gov/sra?term=srr7694367 covid, source VIRAL RNA - want to exclude


    ## CREATE TEMPORARY TABLE
    logging.info("Creating temporary taxonomy table ...")
    extern.run('bq query --use_legacy_sql=false', stdin=sql_pretable)
    logging.info("Finished querying")

    ##### SHOTGUN
    if args.target == 'shotgun':
      shotgun_destination_path = 'gs://cmr-big-data-microbiome/shotgun_sra_{}/*'.format(args.date)
      logging.info("Querying and writing shotgun results to {} ..".format(shotgun_destination_path))

      sql1 = sql.replace('__SQL_JSON_RESULTS_URI__',shotgun_destination_path) + metagenome_specfic_sql

      extern.run('bq query --use_legacy_sql=false', stdin=sql1)
      logging.info("Finished querying for shotgun")


    ##### AMPLICON
    elif args.target == 'amplicon':
      amplicon_destination_path = 'gs://cmr-big-data-microbiome/amplicon_sra_{}/*'.format(args.date)
      logging.info("Querying and writing shotgun results to {} ..".format(amplicon_destination_path))

      sql2 = sql.replace('__SQL_JSON_RESULTS_URI__',amplicon_destination_path) + amplicon_specific_sql
      # print(sql2)

      extern.run('bq query --use_legacy_sql=false', stdin=sql2)
      logging.info("Finished querying for amplicon")

    else: raise ValueError("Unknown target: {}".format(args.target))

    # Now write the taxonomy table
    destination_path = 'gs://cmr-big-data-microbiome/sra_taxonomy_table_{}/*'.format(args.date)
    logging.info("Querying and writing taxonomy table results to {} ..".format(destination_path))

    sql = "EXPORT DATA OPTIONS(uri='{}', format='JSON') AS select * from test.emp".format(destination_path)

    extern.run('bq query --use_legacy_sql=false', stdin=sql)
    logging.info("Finished querying for the taxonomy table")