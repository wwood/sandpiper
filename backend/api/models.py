"""
models.py
- Data classes for SingleM databases
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Otu(db.Model):
    __tablename__ = 'otus'
    id = db.Column(db.Integer, primary_key=True)
    # sample_name|num_hits|coverage|taxonomy|marker_id|sequence_id
    sample_name = db.Column(db.String, nullable=False)
    num_hits = db.Column(db.Integer, nullable=False)
    coverage = db.Column(db.Float, nullable=False)
    taxonomy = db.Column(db.String, nullable=False)
    marker_id = db.Column(db.Integer, db.ForeignKey('markers.id'), nullable=False)
    sequence_id = db.Column(db.Integer, db.ForeignKey('nucleotides.id'), nullable=False)
   
    def to_dict(self):
        return dict(id=self.id,
                    sample_name=self.sample_name,
                    num_hits=self.num_hits,
                    coverage=self.coverage,
                    taxonomy=self.taxonomy,
                    marker=self.marker.marker,
                    sequence=self.sequence.sequence
                    )

class Marker(db.Model):
    __tablename__ = 'markers'
    id = db.Column(db.Integer, primary_key=True)
    marker = db.Column(db.String, nullable=False)
    otus = db.relationship('Otu', backref='marker')

    def to_dict(self):
        return dict(id=self.id,
                    marker=self.marker)

class Nucleotide(db.Model):
    __tablename__ = 'nucleotides'
    id = db.Column(db.Integer, primary_key=True)
    marker_id = db.Column(db.Integer, db.ForeignKey('markers.id'), nullable=False)
    sequence = db.Column(db.String, nullable=False)
    marker_wise_id = db.Column(db.Integer, nullable=False)
    otus = db.relationship('Otu', backref='sequence')

    def to_dict(self):
        return dict(id=self.id,
                    marker_id=self.marker_id,
                    sequence=self.sequence,
                    marker_wise_id=self.marker_wise_id)

class CondensedProfile(db.Model):
    __tablename__ = 'condensed_profiles'
    #     "CREATE TABLE condensed_profiles (id INTEGER PRIMARY KEY,"
    #     " sample_name text, coverage float, taxonomy_id INTEGER);\n")
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False, index=True)
    coverage = db.Column(db.Float, nullable=False, index=True)
    filled_coverage = db.Column(db.Float, nullable=False, index=True)
    relative_abundance = db.Column(db.Float, nullable=False, index=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False, index=True)

    domain_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    phylum_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    family_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    genus_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    species_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)

    ncbi_metadata = db.relationship("NcbiMetadata", back_populates="condensed_profiles")
    taxonomy = db.relationship("Taxonomy", back_populates="condensed_profiles", foreign_keys=[taxonomy_id])


class Taxonomy(db.Model):
    # Not used here but this is the logical place to put it since it is used in the condensed profile, plus maybe otus in the future
    taxonomy_level_columns = ['domain_id','phylum_id','class_id','order_id','family_id','genus_id','species_id']

    #     "CREATE TABLE taxonomies (id INTEGER PRIMARY KEY, taxonomy_level TEXT, parent_id INTEGER, name TEXT); \n"
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    taxonomy_level = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False)
    name = db.Column(db.String, nullable=False, index=True)
    full_name = db.Column(db.String, nullable=False)

    condensed_profiles = db.relationship('CondensedProfile', back_populates='taxonomy', foreign_keys=[CondensedProfile.taxonomy_id])
    condensed_profile_domains = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.domain_id])
    condensed_profile_phyla = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.phylum_id])
    condensed_profile_classes = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.class_id])
    condensed_profile_orders = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.order_id])
    condensed_profile_families = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.family_id])
    condensed_profile_genera = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.genus_id])
    condensed_profile_species = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.species_id])

    def to_dict(self):
        return dict(id=self.id,
                    taxonomy_level=self.taxonomy_level,
                    parent_id=self.parent_id,
                    name=self.name)

    def split_taxonomy(self):
        return self.full_name.split('; ')

class BiosampleAttribute(db.Model):
    __tablename__ = 'biosample_attributes'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False, index=True)
    k = db.Column(db.String, nullable=False, index=True)
    v = db.Column(db.String, nullable=False)
    
    def to_dict(self):
        return dict(id=self.id,
                    run_id=self.run_id,
                    k=self.k,
                    v=self.v)

class ParsedSampleAttribute(db.Model):
    __tablename__ = 'parsed_sample_attributes'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False, index=True)
    collection_year = db.Column(db.Integer)
    collection_month = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth = db.Column(db.Float)
    temperature = db.Column(db.Float)

class NcbiMetadata(db.Model):
    __tablename__ = 'ncbi_metadata'
    id = db.Column(db.Integer, primary_key=True)
    # acc,
    # assay_type,
    # center_name,
    # experiment,
    # sample_name,
    # instrument,
    # libraryselection,
    # librarysource,
    # platform,
    # sample_acc,
    # biosample,
    # organism,
    # sra_study,
    # releasedate,
    # bioproject,
    # avgspotlen,
    # mbases,
    # insertsize,
    # library_name,
    # biosamplemodel_sam,
    # collection_date_sam,
    # geo_loc_name_country_calc,
    # geo_loc_name_country_continent_calc,
    # geo_loc_name_sam,
    # sample_name_sam,
    # attributes
    acc = db.Column(db.String, nullable=False, index=True)
    assay_type = db.Column(db.String)
    center_name = db.Column(db.String)
    experiment = db.Column(db.String)
    sample_name = db.Column(db.String)
    instrument = db.Column(db.String)
    librarylayout = db.Column(db.String)
    libraryselection = db.Column(db.String)
    librarysource = db.Column(db.String)
    platform = db.Column(db.String)
    sample_acc = db.Column(db.String)
    biosample = db.Column(db.String)
    organism = db.Column(db.String)
    sra_study = db.Column(db.String)
    releasedate = db.Column(db.DateTime)
    bioproject = db.Column(db.String)
    mbytes = db.Column(db.Integer)
    loaddate = db.Column(db.DateTime)
    avgspotlen = db.Column(db.Integer)
    mbases = db.Column(db.Integer)
    insertsize = db.Column(db.Integer)
    library_name = db.Column(db.String)
    collection_date_sam = db.Column(db.DateTime)
    geo_loc_name_country_calc = db.Column(db.String)
    geo_loc_name_country_continent_calc = db.Column(db.String)
    geo_loc_name_sam = db.Column(db.String)
    ena_first_public_run = db.Column(db.String)
    ena_last_update_run = db.Column(db.String)
    sample_name_sam = db.Column(db.String)

    biosample_attributes = db.relationship('BiosampleAttribute', backref='ncbi_metadata', foreign_keys=[BiosampleAttribute.run_id])
    # condensed_profiles = db.relationship('CondensedProfile', backref='ncbi_metadata', foreign_keys=[CondensedProfile.run_id])
    condensed_profiles = db.relationship('CondensedProfile', back_populates='ncbi_metadata', foreign_keys=[CondensedProfile.run_id])

    def to_displayable_dict(self):
        return dict(acc=self.acc,
                    assay_type=self.assay_type,
                    center_name=self.center_name,
                    experiment=self.experiment,
                    sample_name=self.sample_name,
                    instrument=self.instrument,
                    librarylayout=self.librarylayout,
                    libraryselection=self.libraryselection,
                    librarysource=self.librarysource,
                    platform=self.platform,
                    sample_acc=self.sample_acc,
                    biosample=self.biosample,
                    organism=self.organism,
                    sra_study=self.sra_study,
                    releasedate=self.releasedate,
                    bioproject=self.bioproject,
                    mbytes=self.mbytes,
                    loaddate=self.loaddate,
                    avgspotlen=self.avgspotlen,
                    mbases=self.mbases,
                    insertsize=self.insertsize,
                    library_name=self.library_name,
                    collection_date_sam=self.collection_date_sam,
                    geo_loc_name_country_calc=self.geo_loc_name_country_calc,
                    geo_loc_name_country_continent_calc=self.geo_loc_name_country_continent_calc,
                    geo_loc_name_sam=self.geo_loc_name_sam,
                    ena_first_public_run=self.ena_first_public_run,
                    ena_last_update_run=self.ena_last_update_run,
                    sample_name_sam=self.sample_name_sam,
                    biosample_attributes=[{'k': x.k, 'v': x.v} for x in self.biosample_attributes if x.k != 'primary_search'])

# ncbi_metadata_biosample_model_association_table = db.Table(
#     'ncbi_metadata_biosample_model_association', 
#     db.Model.metadata, 
#     db.Column('ncbi_metadata_id', db.Integer, db.ForeignKey('ncbi_metadata.id')),
#     db.Column('biosamplemodel_id', db.Integer, db.ForeignKey('biosamplemodels.id'))
# )
    
# class BioSampleModel(db.Model):
#     __tablename__ = 'biosamplemodels'
#     id = db.Column(db.Integer, primary_key=True)
#     model_name = db.Column(db.String, nullable=False)
#     ncbi_metadata = db.relationship('BioSampleModel', secondary=ncbi_metadata_biosample_model_association_table, backref='biosamplemodels')

