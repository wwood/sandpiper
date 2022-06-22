import xml.etree.ElementTree as ET
from dataclasses import dataclass
import os

XML = os.path.join(os.path.dirname(__file__), 'biosample_attributes.20220621.xml')

@dataclass
class BioSampleAttribute:
    name: str
    harmonized_name: str
    description: str

class BioSampleAttributes:
    def __init__(self, log):
        self.attributes = {}
        self.parse_xml(log)

    def parse_xml(self, log):
        tree = ET.parse(XML)
        root = tree.getroot()
        for child in root.findall('Attribute'):
            desc = child.find('Description')
            attr = BioSampleAttribute(
                name=child.find('Name').text,
                harmonized_name=child.find('HarmonizedName').text,
                description=desc.text if desc is not None else None)
            self.attributes[attr.harmonized_name] = attr
        log.info("Parsed in {} attributes".format(len(self.attributes)))

IDENTIFIERS_TYPE_METADATA = 'identity_metadata'
SEQUENCING_TYPE_METADATA = 'sequencing_metadata'
CONTACT_TYPE_METADATA = 'contact_metadata'
SAMPLE_INFO_TYPE_METADATA = 'sample_info_metadata'

@dataclass
class NcbiMetadataExtraInfo:
    name: str
    classification: str
    description: str

class NcbiMetadataExtraInfos:
    EXTRA_INFO = [
        # First batch are described at https://www.ncbi.nlm.nih.gov/sra/docs/sra-cloud-based-metadata-table/
        ['acc', IDENTIFIERS_TYPE_METADATA, 'SRA Run accession in the form of SRR######## (ERR or DRR for INSDC partners)'],
        ['assay_type', SEQUENCING_TYPE_METADATA, 'Type of library (i.e. AMPLICON, RNA-Seq, WGS, etc)'],
        ['center_name', CONTACT_TYPE_METADATA, 'Name of the sequencing center'],
        ['experiment', IDENTIFIERS_TYPE_METADATA, 'The accession in the form of SRX######## (ERX or DRX for INSDC partners)'],
        ['sample_name', SAMPLE_INFO_TYPE_METADATA, 'Name of the sample'],
        ['instrument', SEQUENCING_TYPE_METADATA, 'Name of the sequencing instrument model'],
        ['librarylayout', SEQUENCING_TYPE_METADATA, 'Whether the data is SINGLE or PAIRED'],
        ['libraryselection', SEQUENCING_TYPE_METADATA, 'Library selection methodology (i.e. PCR, RANDOM, etc)'],
        ['librarysource', SEQUENCING_TYPE_METADATA, 'Source of the biological data (i.e. GENOMIC, METAGENOMIC, etc)'],
        ['platform', SEQUENCING_TYPE_METADATA, 'Name of the sequencing platform (i.e. ILLUMINA)'],
        ['sample_acc', IDENTIFIERS_TYPE_METADATA, 'SRA Sample accession in the form of SRS######## (ERS or DRS for INSDC partners)'],
        ['biosample', IDENTIFIERS_TYPE_METADATA, 'BioSample accession in the form of SAMN######## (SAMEA##### or SAMD##### for INSDC partners)'],
        ['organism', SAMPLE_INFO_TYPE_METADATA, 'Scientific name of the organism that was sequenced (as found in the NCBI Taxonomy Browser)'],
        ['sra_study', IDENTIFIERS_TYPE_METADATA, 'SRA Study accession in the form of SRP######## (ERP or DRP for INSDC partners)'],
        ['releasedate', IDENTIFIERS_TYPE_METADATA, 'The date on which the data was released'],
        ['bioproject', IDENTIFIERS_TYPE_METADATA, 'BioProject accession in the form of PRJNA######## (PRJEB####### or PRJDB###### for INSDC partners)'],
        ['mbytes', SEQUENCING_TYPE_METADATA, 'Number of mega bytes of data in the SRA Run'],
        ['loaddate', IDENTIFIERS_TYPE_METADATA, 'The date when the data was loaded into SRA'],
        ['avgspotlen', SEQUENCING_TYPE_METADATA, 'Calculated average read length'],
        ['mbases', SEQUENCING_TYPE_METADATA, 'Number of mega bases in the SRA Runs'],
        ['insertsize', SEQUENCING_TYPE_METADATA, 'Submitter provided insert size'],
        ['library_name', SAMPLE_INFO_TYPE_METADATA, 'The name of the library'],
        ['biosamplemodel_sam', SAMPLE_INFO_TYPE_METADATA, 'The BioSample package/model that was picked'],
        ['collection_date_sam', SAMPLE_INFO_TYPE_METADATA, 'The collection date of the sample'],
        ['geo_loc_name_country_calc', SAMPLE_INFO_TYPE_METADATA, 'Name of the country where the sample was collected'],
        ['geo_loc_name_country_continent_calc', SAMPLE_INFO_TYPE_METADATA, 'Name of the continent where the sample was collected'],
        ['geo_loc_name_sam', SAMPLE_INFO_TYPE_METADATA, 'Full location of collection'],
        ['ena_first_public_run', IDENTIFIERS_TYPE_METADATA, 'Date when INSDC partner record was public'],
        ['ena_last_update_run', IDENTIFIERS_TYPE_METADATA, 'Date when INSDC partner record was updated'],
        ['sample_name_sam', SAMPLE_INFO_TYPE_METADATA, 'INSDC sample name'],

        # Below descriptions were cobbled together from submit ncbi template sheets, etc.
        ['experiment_title',SAMPLE_INFO_TYPE_METADATA,'Title of the experiment the sequencing is associated with'],
        ['library_strategy',SEQUENCING_TYPE_METADATA,'The strategy used to prepare nucleic acids for sequencing e.g. WGS, AMPLICON'],
        ['instrument_model',SEQUENCING_TYPE_METADATA,'The specific model used for sequencing'],
        ['organisation_name',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_department',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_institution',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_street',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_city',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_country',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['organisation_contact_name',CONTACT_TYPE_METADATA,'Part of submitter contact details'],
        ['study_title',SAMPLE_INFO_TYPE_METADATA,'Title of the study the sequencing is associated with'],
        ['study_abstract', SAMPLE_INFO_TYPE_METADATA,'Abstract of associated study'],
        ['design_description', SEQUENCING_TYPE_METADATA,'Free-form description of the methods used to create the sequencing library; a brief \'materials and methods\' section.']
    ]
    
    def __init__(self):
        self.extra_info = {}
        for extra_info in self.EXTRA_INFO:
            self.extra_info[extra_info[0]] = NcbiMetadataExtraInfo(
                name=extra_info[0],
                classification=extra_info[1],
                description=extra_info[2])

# For testing, is below
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    biosample_attributes = BioSampleAttributes(log)
    # print(biosample_attributes.attributes)

    ncbi_extras = NcbiMetadataExtraInfos()
    print(ncbi_extras.extra_info)