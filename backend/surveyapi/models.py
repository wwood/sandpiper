"""
models.py
- Data classes for the surveyapi application
"""

from datetime import datetime
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

# class Survey(db.Model):
#     __tablename__ = 'surveys'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     questions = db.relationship('Question', backref="survey", lazy=False)

#     def to_dict(self):
#       return dict(id=self.id,
#                   name=self.name,
#                   created_at=self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                   questions=[question.to_dict() for question in self.questions])

# class Question(db.Model):
#     __tablename__ = 'questions'

#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String(500), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
#     choices = db.relationship('Choice', backref='question', lazy=False)

#     def to_dict(self):
#         return dict(id=self.id,
#                     text=self.text,
#                     created_at=self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                     survey_id=self.survey_id,
#                     choices=[choice.to_dict() for choice in self.choices])

# class Choice(db.Model):
#     __tablename__ = 'choices'

#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String(100), nullable=False)
#     selected = db.Column(db.Integer, default=0)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

#     def to_dict(self):
#         return dict(id=self.id,
#                     text=self.text,
#                     created_at=self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                     question_id=self.question_id)
