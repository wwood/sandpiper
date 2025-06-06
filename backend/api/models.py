"""
models.py
- Data classes for SingleM databases
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Otu(db.Model):
    ''' This table is actually dropped during DB generation '''
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

class OtuIndexed(db.Model):
    '''This table is intended to be quickly queried based on run_id only, with
    taxonomy and marker names cached. SQLite seems to be slow at this query when
    running it on the original Otu table object.'''
    
    __tablename__ = 'otus_indexed'
    id = db.Column(db.Integer, primary_key=True)
    # sample_name|num_hits|coverage|taxonomy|marker_id|sequence_id
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False, index=True)
    num_hits = db.Column(db.Integer, nullable=False)
    coverage = db.Column(db.Float, nullable=False)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False)
    marker_id = db.Column(db.Integer, db.ForeignKey('markers.id'), nullable=False)
    sequence = db.Column(db.String, nullable=False)

    ncbi_metadata = db.relationship("NcbiMetadata", back_populates="otus")
    taxonomy = db.relationship("Taxonomy", back_populates="otus", foreign_keys=[taxonomy_id])
   
    def to_dict(self):
        return dict(id=self.id,
                    run_id=self.run_id,
                    num_hits=self.num_hits,
                    coverage=self.coverage,
                    taxonomy_id=self.taxonomy_id,
                    marker_id=self.marker_id,
                    sequence=self.sequence
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
    # relative_abundance is a filled coverage
    relative_abundance = db.Column(db.Float, nullable=False, index=True)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False, index=True)

    # domain_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # phylum_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # class_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # order_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # family_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # genus_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)
    # species_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), index=True)

    ncbi_metadata = db.relationship("NcbiMetadata", back_populates="condensed_profiles")
    taxonomy = db.relationship("Taxonomy", back_populates="condensed_profiles", foreign_keys=[taxonomy_id])


class Taxonomy(db.Model):
    # Not used here but this is the logical place to put it since it is used in the condensed profile, plus maybe otus in the future
    # taxonomy_level_columns = ['domain_id','phylum_id','class_id','order_id','family_id','genus_id','species_id']

    #     "CREATE TABLE taxonomies (id INTEGER PRIMARY KEY, taxonomy_level TEXT, parent_id INTEGER, name TEXT); \n"
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    taxonomy_level = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxonomies.id'), nullable=False)
    name = db.Column(db.String, nullable=False, index=True)
    full_name = db.Column(db.String, nullable=False)
    host_sample_count = db.Column(db.Integer)
    ecological_sample_count = db.Column(db.Integer)

    condensed_profiles = db.relationship('CondensedProfile', back_populates='taxonomy', foreign_keys=[CondensedProfile.taxonomy_id])
    # condensed_profile_domains = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.domain_id])
    # condensed_profile_phyla = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.phylum_id])
    # condensed_profile_classes = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.class_id])
    # condensed_profile_orders = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.order_id])
    # condensed_profile_families = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.family_id])
    # condensed_profile_genera = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.genus_id])
    # condensed_profile_species = db.relationship('CondensedProfile', foreign_keys=[CondensedProfile.species_id])

    otus = db.relationship('OtuIndexed', back_populates='taxonomy', foreign_keys=[OtuIndexed.taxonomy_id])

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
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)
    depth = db.Column(db.Float)
    temperature = db.Column(db.Float)
    host_or_not_prediction = db.Column(db.String)
    host_or_not_recorded = db.Column(db.String)
    host_or_not_mature = db.Column(db.String)
    # sample  bacterial_archaeal_bases        metagenome_size read_fraction   warning
    bacterial_archaeal_bases = db.Column(db.Float)
    # metagenome_size = db.Column(db.Float) #=> use mbases from ncbi_metadata
    smf = db.Column(db.Float)
    smf_warning = db.Column(db.Boolean)
    known_species_fraction = db.Column(db.Float)

    def to_displayable_dict(self):
        return dict(
            collection_year=self.collection_year,
            collection_month=self.collection_month,
            latitude=self.latitude,
            longitude=self.longitude,
            depth=self.depth,
            temperature=self.temperature,
            host_or_not_prediction=self.host_or_not_prediction,
            host_or_not_recorded=self.host_or_not_recorded,
            host_or_not_mature=self.host_or_not_mature,
            bacterial_archaeal_bases=self.bacterial_archaeal_bases,
            smf=self.smf,
            smf_warning=self.smf_warning,
            known_species_fraction=self.known_species_fraction)


class StudyLink(db.Model):
    __tablename__ = 'study_links'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False, index=True)
    study_id = db.Column(db.String)
    database = db.Column(db.String)
    label = db.Column(db.String)
    url = db.Column(db.String)

    def to_displayable_dict(self):
        if self.database:
            return dict(
                study_id=self.study_id,
                database=self.database)
        else:
            return dict(
                label=self.label,
                url=self.url)


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
    experiment = db.Column(db.String, index=True)
    sample_name = db.Column(db.String)
    model = db.Column(db.String)
    librarylayout = db.Column(db.String)
    libraryselection = db.Column(db.String)
    librarysource = db.Column(db.String)
    platform = db.Column(db.String)
    sample_acc = db.Column(db.String, index=True)
    biosample = db.Column(db.String, index=True)
    taxon_name = db.Column(db.String)
    sra_study = db.Column(db.String, index=True)
    published = db.Column(db.DateTime)
    bioproject = db.Column(db.String, index=True)
    # mbytes = db.Column(db.Integer)
    # avgspotlen = db.Column(db.Integer)
    bases = db.Column(db.Integer)
    spots = db.Column(db.Integer)
    insertsize = db.Column(db.Integer)
    library_name = db.Column(db.String)
    collection_date_parsed = db.Column(db.DateTime)
    geo_loc_name_country_calc = db.Column(db.String)
    geo_loc_name_country_continent_calc = db.Column(db.String)
    geo_loc_name = db.Column(db.String)
    ena_first_public_run = db.Column(db.String)
    ena_last_update_run = db.Column(db.String)

    # Below are fields found from kingfisher annotate
    experiment_title = db.Column(db.String)
    library_strategy = db.Column(db.String)
    organisation_name = db.Column(db.String)
    organisation_department = db.Column(db.String)
    organisation_institution = db.Column(db.String)
    organisation_street = db.Column(db.String)
    organisation_city = db.Column(db.String)
    organisation_country = db.Column(db.String)
    organisation_contact_name = db.Column(db.String)
    study_title = db.Column(db.String, index=True) # Index because /project matches via title when abstract is not available
    study_abstract = db.Column(db.String, index=True) # Index for /project
    design_description = db.Column(db.String)
    read1_length_average = db.Column(db.Float)
    read1_length_stdev = db.Column(db.Float)
    read2_length_average = db.Column(db.Float)
    read2_length_stdev = db.Column(db.Float)

    study_links = db.relationship('StudyLink', backref='ncbi_metadata', foreign_keys=[StudyLink.run_id])
    biosample_attributes = db.relationship('BiosampleAttribute', backref='ncbi_metadata', foreign_keys=[BiosampleAttribute.run_id])
    condensed_profiles = db.relationship('CondensedProfile', back_populates='ncbi_metadata', foreign_keys=[CondensedProfile.run_id])
    parsed_sample_attributes = db.relationship('ParsedSampleAttribute', backref='ncbi_metadata', foreign_keys=[ParsedSampleAttribute.run_id])
    otus = db.relationship('OtuIndexed', back_populates='ncbi_metadata', foreign_keys=[OtuIndexed.run_id])

    def to_displayable_dict(self):
        biosample_attrs = [x for x in self.biosample_attributes if x.k != 'primary_search']
        # Temporary fix - somehow study_links are in the wrong table atm. HACK!!
        study_links_tmp = [x.v for  x in biosample_attrs if x.k == 'study_links']
        print('tmp: '+str(study_links_tmp)+' type is '+str(type(study_links_tmp)))
        # study_links_tmp currently a list of str e.g. ([{"db": "pubmed", "id": "29669589"}])
        # convert to list of dicts
        study_links = [study_link.to_displayable_dict() for study_link in self.study_links]
        for sl0 in study_links_tmp:
            try:
                print("Evaluating study_links sl0: "+str(sl0))
                sl = eval(sl0)
                for s in sl:
                    if 'id' in s:
                        s['study_id'] = s['id']
                        del s['id']
                    if 'db' in s:
                        s['database'] = s['db']
                        del s['db']
                    if 'label' in s:
                        s['label'] = s['label']
                    if 'url' in s:
                        s['url'] = s['url']
                    study_links.append(s)
            except Exception as e:
                print(f"Error parsing study_links: {e}")
        return dict(acc=self.acc,
                    assay_type=self.assay_type,
                    center_name=self.center_name,
                    experiment=self.experiment,
                    sample_name=self.sample_name,
                    model=self.model,
                    librarylayout=self.librarylayout,
                    libraryselection=self.libraryselection,
                    librarysource=self.librarysource,
                    platform=self.platform,
                    sample_acc=self.sample_acc,
                    biosample=self.biosample,
                    taxon_name=self.taxon_name,
                    sra_study=self.sra_study,
                    releasedate=self.published.strftime('%-d %B %Y') if self.published else None,
                    bioproject=self.bioproject,
                    # bytes=self.bytes,
                    # loaddate=self.loaddate,
                    # avgspotlen=self.avgspotlen,
                    bases=self.bases,
                    spots=self.spots,
                    insertsize=self.insertsize,
                    library_name=self.library_name,
                    collection_date_parsed=self.collection_date_parsed.strftime('%-d %B %Y') if self.collection_date_parsed else None,
                    geo_loc_name_country_calc=self.geo_loc_name_country_calc,
                    geo_loc_name_country_continent_calc=self.geo_loc_name_country_continent_calc,
                    geo_loc_name=self.geo_loc_name,
                    ena_first_public_run=self.ena_first_public_run,
                    ena_last_update_run=self.ena_last_update_run,
                    experiment_title=self.experiment_title,
                    library_strategy=self.library_strategy,
                    organisation_department=self.organisation_department,
                    organisation_institution=self.organisation_institution,
                    organisation_street=self.organisation_street,
                    organisation_city=self.organisation_city,
                    organisation_country=self.organisation_country,
                    organisation_contact_name=self.organisation_contact_name,
                    study_title=self.study_title,
                    study_abstract=self.study_abstract,
                    design_description=self.design_description,
                    read1_length_average=self.read1_length_average,
                    read1_length_stdev=self.read1_length_stdev,
                    read2_length_average=self.read2_length_average,
                    read2_length_stdev=self.read2_length_stdev,
                    study_links=study_links,
                    biosample_attributes=[{'k': x.k, 'v': x.v} for x in self.biosample_attributes if x.k != 'primary_search'],
                    parsed_sample_attributes=self.parsed_sample_attributes[0].to_displayable_dict())

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    def to_displayable_dict(self):
        return dict(
            name=self.name,
            description=self.description)

class RunTag(db.Model):
    __tablename__ = 'run_tags'
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey('ncbi_metadata.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

    def to_displayable_dict(self):
        return dict(
            run_id=self.run_id,
            tag_id=self.tag_id)