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
import subprocess
import sys
import os

import extern

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

raise Exception("""AroneyS — 8:54 AM
According to https://doi.org/10.1099/mgen.0.001853, there are many runs with >1x coverage of a microbe that are not in Sandpiper. According to AI there are ~6.2 million. Judging from a sample, most of them are single-cell, transcriptomes, non-illumina, weird seq or amplicon (~5.5 million). But there are 500k WGS that are marked eukaryotic/host genomic and have >1x coverage. But only ~4% have a "real community" with at least 4 species, so ~120k. These include things like dog saliva swabs, insect whole-organism...
We can't filter them by NCBI metadata, but can use bigquery STAT to filter by things like % prokaryotic, N Gbp prokaryotic sequences, N species at >1x coverage, top species <80% of prok seq
Metadata pre-filter:
     
public runs, platform Illumina, BGISEQ or DNBSEQ;
librarysource is GENOMIC, GENOMIC SINGLE CELL or OTHER;
assay_type is WGS, WGA or OTHER;
1–200 Gbp;
organism doesn't contain "metagenome", since those already go through the current Sandpiper query.
Ben W — 8:56 AM
we haven't established whether BGISEQ or DNBSEQ are singlem-compatible though
we might have to relax that 200G max too, some are just legit that big now
AroneyS — 8:57 AM
Yeh, I assume ignore that and go Illumina only. Most of the extras are illumina
The 120k number is from illumina only
Ben W — 8:58 AM
ok, thanks. Sounds like we should include these for next year though
I'll put a croak in the query script to remind us.
is that 4% known species?
AroneyS — 9:00 AM
No, 4% are likely not contamination
Ben W — 9:00 AM
another approach might be to include a larger set when we are running logan contig-singlem, and then only include ones that have enough diversity
sorry I meant 4 species, not 4%
AroneyS — 9:01 AM
I think STAT only works with known?
Ben W — 9:01 AM
some kmers are indicative of higher level clades
but not sure where the threshold lies
annoying thing about logan is that it is out of date too. Maybe could design some threshold by running singlem on a random subset of the 500k
"""

def gcs_destination_exists(destination_path):
    '''Return True if the GCS export destination (a path ending in '/*') already
    contains any objects, since BigQuery EXPORT DATA fails rather than overwrite.'''
    prefix = destination_path.rstrip('*')
    result = subprocess.run(
        ['gcloud', 'storage', 'ls', prefix],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return result.stdout.decode().strip() != ''
    stderr = result.stderr.decode()
    # A missing prefix is not an error condition, anything else is.
    if 'not found' in stderr.lower() or 'matched no objects' in stderr.lower():
        return False
    raise Exception("Failed to list {}: {}".format(prefix, stderr))

def export_data(destination_path, sql, description):
    if gcs_destination_exists(destination_path):
        logging.info("Skipping export of {} because {} already exists".format(
            description, destination_path))
        return
    logging.info("Querying and writing {} results to {} ..".format(description, destination_path))
    extern.run('bq query --use_legacy_sql=false', stdin=sql)
    logging.info("Finished querying for {}".format(description))

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()

    parent_parser.add_argument('--date',required=True, help='date of run e.g. 20111130')
    
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")
    parent_parser.add_argument('--target', help='amplicon or shotgun', choices=['amplicon','shotgun','shotgun-nanopore','shotgun-pacbio'], required=True)
    parent_parser.add_argument('--bucket-name', help='bucket name', default='singlem-sra-metadata-gathering')

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
CREATE OR REPLACE TABLE metadata.emp
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
FROM metadata.emp p
INNER JOIN `nih-sra-datastore.sra_tax_analysis_tool.taxonomy` c ON p.tax_id = c.parent_id
WHERE p.xlevel = counter
)
DO
-- Insert next level
INSERT INTO metadata.emp ( xlevel, tax_id, parent_id, sci_name )
SELECT counter + 1 AS xlevel, c.tax_id, c.parent_id, c.sci_name
FROM metadata.emp p
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
-- -- SELECT  xlevel, tax_id, parent_id, sci_name  FROM metadata.emp ORDER BY xlevel;
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
  librarylayout,
  bioproject,
  sra_study,
  avgspotlen,
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
	organism IN (SELECT sci_name FROM metadata.emp)
	)
    AND platform = '__SQL_PLATFORM__'
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

    logging.info("(re-)Creating metadata dataset ...")
    extern.run('bq mk -f -d metadata')
    logging.info("Finished creating metadata dataset")

    ## CREATE TEMPORARY TABLE
    logging.info("Creating temporary taxonomy table ...")
    extern.run('bq query --use_legacy_sql=false', stdin=sql_pretable)
    logging.info("Finished querying")

    ##### SHOTGUN
    if args.target == 'shotgun':
      shotgun_destination_path = 'gs://{}/shotgun_sra_{}/*'.format(args.bucket_name, args.date)

      sql1 = sql.replace(
         '__SQL_JSON_RESULTS_URI__',shotgun_destination_path).replace(
            '__SQL_PLATFORM__', 'ILLUMINA') + metagenome_specfic_sql

      export_data(shotgun_destination_path, sql1, 'shotgun')


    #### SHOTGUN NANOPORE
    elif args.target == 'shotgun-nanopore':
      shotgun_destination_path = 'gs://{}/shotgun_nanopore_sra_{}/*'.format(args.bucket_name, args.date)

      sql1 = sql.replace(
         '__SQL_JSON_RESULTS_URI__',shotgun_destination_path).replace(
            '__SQL_PLATFORM__', 'OXFORD_NANOPORE') + metagenome_specfic_sql

      export_data(shotgun_destination_path, sql1, 'shotgun nanopore')


    #### SHOTGUN PACBIO
    # PACBIO_SMRT is the only PacBio platform value - RS/RS II/Sequel/Revio/Onso
    # are distinguished by the instrument column, not platform.
    elif args.target == 'shotgun-pacbio':
      shotgun_destination_path = 'gs://{}/shotgun_pacbio_sra_{}/*'.format(args.bucket_name, args.date)

      sql1 = sql.replace(
         '__SQL_JSON_RESULTS_URI__',shotgun_destination_path).replace(
            '__SQL_PLATFORM__', 'PACBIO_SMRT') + metagenome_specfic_sql

      export_data(shotgun_destination_path, sql1, 'shotgun pacbio')


    ##### AMPLICON
    elif args.target == 'amplicon':
      amplicon_destination_path = 'gs://{}/amplicon_sra_{}/*'.format(args.bucket_name, args.date)

      sql2 = sql.replace(
         '__SQL_JSON_RESULTS_URI__',amplicon_destination_path).replace(
            '__SQL_PLATFORM__', 'ILLUMINA') + amplicon_specific_sql

      export_data(amplicon_destination_path, sql2, 'amplicon')

    else: raise ValueError("Unknown target: {}".format(args.target))

    # Now write the taxonomy table
    destination_path = 'gs://{}/sra_taxonomy_table_{}/*'.format(args.bucket_name, args.date)

    sql = "EXPORT DATA OPTIONS(uri='{}', format='JSON') AS select * from metadata.emp".format(destination_path)

    export_data(destination_path, sql, 'taxonomy table')