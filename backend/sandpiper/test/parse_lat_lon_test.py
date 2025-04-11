#!/usr/bin/env python

#=======================================================================
# Author:
#
# Unit tests.
#
# Copyright
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================

import unittest
import os.path
import extern

script = os.path.join(os.path.dirname(__file__), '../parse_biosample_extras.py')


class Tests(unittest.TestCase):
    def test_previously_ok(self):
        stdin = '{"acc":"ERR5757773","mbases":"4675","mbytes":"1406","assay_type":"WGS","releasedate":"2022-01-10T00:00:00+00:00","organism":"soil metagenome","libraryselection":"unspecified","librarysource":"METAGENOMIC","bioproject":"PRJEB44414","sra_study":"ERP128471","avgspotlen":"302","attributes":[{"k":"bases","v":"4675396994"},{"k":"bytes","v":"1474332866"},{"k":"run_file_create_date","v":"2022-03-20T09:42:00.000Z"},{"k":"collection_date_sam","v":"2014-01-24"},{"k":"common_name_sam","v":"soil metagenome"},{"k":"ena_first_public_sam","v":"2022-01-10"},{"k":"ena_last_update_sam_ss_dpl537","v":"2022-01-10"},{"k":"environment__biome__sam","v":"terrestrial biome"},{"k":"environment__feature__sam","v":"valley"},{"k":"environment__material__sam","v":"soil"},{"k":"external_id_sam","v":"SAMEA8585603"},{"k":"geographic_location__country_and_or_sea__sam","v":"Australia"},{"k":"geographic_location__depth__sam","v":"0"},{"k":"geographic_location__elevation__sam","v":"0"},{"k":"geographic_location__latitude__sam","v":"-42.1744"},{"k":"geographic_location__longitude__sam","v":"146.5762"},{"k":"insdc_center_alias_sam","v":"Quadram Institute Bioscience"},{"k":"insdc_center_name_sam","v":"Quadram Institute Bioscience"},{"k":"insdc_first_public_sam","v":"2022-01-10T12:20:17Z"},{"k":"insdc_last_update_sam","v":"2022-01-10T12:20:17Z"},{"k":"insdc_status_sam","v":"public"},{"k":"investigation_type_sam","v":"metagenome"},{"k":"land_use_1_sam","v":"peat_extraction"},{"k":"land_use_sam","v":"peat_extraction"},{"k":"landscape_sam","v":"mountain_valley"},{"k":"project_name_sam","v":"wetSoilMG"},{"k":"region_iso_code_sam","v":"AU-TAS"},{"k":"sequencing_method_sam","v":"Illumina NovaSeq with 2 x 150 bp paired-end"},{"k":"site_sam","v":"Tasmania_raised_bog"},{"k":"soil_environmental_package_sam","v":"soil"},{"k":"submitter_id_sam","v":"Y88"},{"k":"vegetation_sam","v":"bare_soil"},{"k":"vegetation_simple_sam","v":"bare_soil"},{"k":"primary_search","v":"24827287"},{"k":"primary_search","v":"796882"},{"k":"primary_search","v":"ERP128471"},{"k":"primary_search","v":"ERR5757773"},{"k":"primary_search","v":"ERS6270254"},{"k":"primary_search","v":"ERX5467430"},{"k":"primary_search","v":"PRJEB44414"},{"k":"primary_search","v":"SAMEA8585603"},{"k":"primary_search","v":"Y88"},{"k":"primary_search","v":"ena-STUDY-Quadram Institute Bioscience-20-04-2021-11:20:51:615-1003"},{"k":"primary_search","v":"webin-reads-Sample_SE-2178-Y088"}]}'

        self.assertEqual(
            '\n'.join(
                ['\t'.join('sample_name     latitude        longitude'.split()),
                '\t'.join(['ERR5757773','-42.1744','146.5762']),
                '']),
            extern.run(f'{script} --json-input /dev/stdin', stdin=stdin))

    def test_dpl_issue1(self):
        stdin = '{"acc":"SRR5923187","mbases":"7904","mbytes":"3799","assay_type":"WGS","releasedate":"2017-08-10T00:00:00+00:00","organism":"soil metagenome","libraryselection":"PCR","librarysource":"METAGENOMIC","bioproject":"PRJNA317932","sra_study":"SRP074055","avgspotlen":"302","attributes":[{"k":"bases","v":"7904786580"},{"k":"bytes","v":"3983864712"},{"k":"run_file_create_date","v":"2017-08-10T05:20:00.000Z"},{"k":"forward_read_length_run","v":"150bp"},{"k":"md5_checksum2_run","v":"81fcdebda68eeec6b678981014e94d31"},{"k":"md5_checksum3_run","v":"f2ebc7e76fce2c156d753e4294760858"},{"k":"md5_checksum4_run","v":"ff553cad29b8acffd6ee4bc2cfa7525f"},{"k":"md5_checksum_run","v":"5e647efe34562b6508a08050f09fed37"},{"k":"reverse_read_length_run","v":"150bp"},{"k":"collection_date_sam","v":"2015-02-18"},{"k":"depth_sam","v":"0.0"},{"k":"isolate_sam_ss_dpl100","v":"102.100.100/19473_0"},{"k":"isolation_source_sam","v":"soil"},{"k":"lat_lon_sam_s_dpl34","v":"33.620750 S 150.734230 E"},{"k":"primary_search","v":"102.100.100/19473"},{"k":"primary_search","v":"19473_1_PE_550bp_BASE_UNSW_HFMKTBCXX_GAGATTCC-CAGGACGT_L002_R2_001.fastq.gz"},{"k":"primary_search","v":"19473_HFMKTBCXX"},{"k":"primary_search","v":"317932"},{"k":"primary_search","v":"7488528"},{"k":"primary_search","v":"PRJNA317932"},{"k":"primary_search","v":"PRJNA597010"},{"k":"primary_search","v":"SAMN07488528"},{"k":"primary_search","v":"SRP074055"},{"k":"primary_search","v":"SRR5923187"},{"k":"primary_search","v":"SRS2422214"},{"k":"primary_search","v":"SRX3083517"}]}'

        self.assertEqual(
            '\n'.join(
                ['\t'.join('sample_name     latitude        longitude'.split()),
                '\t'.join(['SRR5923187','-33.62075','150.73423']),
                '']),
            extern.run(f'{script} --json-input /dev/stdin', stdin=stdin))

    def test_depth(self):
        stdin = '{"acc":"SRR27444525","mbases":"1177","mbytes":"461","assay_type":"WGS","releasedate":"2025-01-31T00:00:00+00:00","organism":"marine metagenome","libraryselection":"MDA","librarysource":"GENOMIC SINGLE CELL","bioproject":"PRJNA1061664","sra_study":"SRP482214","avgspotlen":"302","attributes":[{"k":"bases","v":"1177063120"},{"k":"bytes","v":"484217282"},{"k":"run_file_create_date","v":"2024-01-06T07:59:00.000Z"},{"k":"collection_date_sam","v":"2014-03-20"},{"k":"depth_sam","v":"20"},{"k":"env_broad_scale_sam","v":"marine biome [ENVO_00000447]"},{"k":"env_local_scale_sam","v":"marine pelagic biome [ENVO:01000023]"},{"k":"env_medium_sam","v":"marine biome [ENVO_00000447]"},{"k":"lat_lon_sam_s_dpl34","v":"36.688 N 122.386 W"},{"k":"n_cells_sam","v":"1"},{"k":"source_material_identifiers_sam","v":"Worden-01-jan2019-H12-S83"},{"k":"staining_sam","v":"LysoTracker"},{"k":"station_sam","v":"M2"},{"k":"primary_search","v":"1061664"},{"k":"primary_search","v":"39278315"},{"k":"primary_search","v":"PRJNA1061664"},{"k":"primary_search","v":"SAMN39278315"},{"k":"primary_search","v":"SRP482214"},{"k":"primary_search","v":"SRR27444525"},{"k":"primary_search","v":"SRS20070799"},{"k":"primary_search","v":"SRX23116321"},{"k":"primary_search","v":"bp0"},{"k":"primary_search","v":"sort_0891"},{"k":"primary_search","v":"sort_0891_L001_R1_001.fastq.gz"}]}'

        self.assertEqual(
            '\n'.join(
                ['\t'.join('sample_name     latitude        longitude  depth collection_year collection_month        temperature'.split()),
                '\t'.join(['SRR27444525','36.688','-122.386','20','2014','3','']),
                '']),
            extern.run(f'{script} --json-input /dev/stdin --extra-sample-keys depth collection_date temperature', stdin=stdin))

    def test_temp(self):
        stdin = '{"acc":"SRR3286242","mbases":"6611","mbytes":"3799","assay_type":"AMPLICON","releasedate":"2016-03-28T00:00:00+00:00","organism":"lake water metagenome","libraryselection":"PCR","librarysource":"METAGENOMIC","bioproject":"PRJNA217938","sra_study":"SRP029470","avgspotlen":"500","attributes":[{"k":"bases","v":"6611837000"},{"k":"bytes","v":"3983652328"},{"k":"run_file_create_date","v":"2016-03-23T12:45:00.000Z"},{"k":"chloride_sam","v":"104.025"},{"k":"collection_date_sam","v":"2013-01-14"},{"k":"conduc_sam","v":"0.722"},{"k":"depth_sam","v":"6"},{"k":"diss_oxygen_sam","v":"11.15"},{"k":"env_biome_sam","v":"aquatic"},{"k":"env_feature_sam","v":"lake"},{"k":"env_material_sam","v":"water"},{"k":"lat_lon_sam_s_dpl34","v":"42.26 N 71.08 W"},{"k":"nitrate_sam_s_dpl36","v":"0.524"},{"k":"sulfate_sam","v":"4.335"},{"k":"temp_sam","v":"3"},{"k":"primary_search","v":"131001Alm_D13-4961_phiX_best_2.fastq"},{"k":"primary_search","v":"217938"},{"k":"primary_search","v":"4567392"},{"k":"primary_search","v":"B011413TAWMD06"},{"k":"primary_search","v":"PRJNA217938"},{"k":"primary_search","v":"SAMN04567392"},{"k":"primary_search","v":"SB011413TAWMD06VV4TMR1"},{"k":"primary_search","v":"SRP029470"},{"k":"primary_search","v":"SRR3286242"},{"k":"primary_search","v":"SRS1357114"},{"k":"primary_search","v":"SRX1656859"}]}'

        self.assertEqual(
            '\n'.join(
                ['\t'.join('sample_name     latitude        longitude  depth collection_year collection_month        temperature'.split()),
                '\t'.join(['SRR3286242','42.26','-71.08','6','2013','1','3']),
                '']),
            extern.run(f'{script} --json-input /dev/stdin --extra-sample-keys depth collection_date temperature', stdin=stdin))



if __name__ == "__main__":
	unittest.main()
