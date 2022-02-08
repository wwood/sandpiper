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
    sample_name = db.Column(db.String, nullable=False)
    coverage = db.Column(db.Float, nullable=False)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False)

class Taxonomy(db.Model):
    #     "CREATE TABLE taxonomies (id INTEGER PRIMARY KEY, taxonomy_level TEXT, parent_id INTEGER, name TEXT); \n"
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    taxonomy_level = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    condensed_profiles = db.relationship('CondensedProfile', backref='taxonomy')

    def to_dict(self):
        return dict(id=self.id,
                    taxonomy_level=self.taxonomy_level,
                    parent_id=self.parent_id,
                    name=self.name)

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
    acc = db.Column(db.String, nullable=False)
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

    biosample_attributes = db.relationship('BiosampleAttribute', backref='ncbi_metadata')

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


class BiosampleAttribute(db.Model):
    __tablename__ = 'biosample_attributes'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False)
    k = db.Column(db.String, nullable=False)
    v = db.Column(db.String, nullable=False)