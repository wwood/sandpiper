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
    id = db.Column(db.Integer, primary_key=True)
    sample_name = db.Column(db.String, nullable=False)
    coverage = db.Column(db.Float, nullable=False)
    taxonomy = db.Column(db.String, nullable=False)
