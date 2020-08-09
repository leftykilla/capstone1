from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class State(db.Model):
    """An individual state."""

    __tablename__ = 'states'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    counties = db.relationship('County', secondary='zip_codes', backref='states')


class County(db.Model):
    """An individual county."""

    __tablename__ = 'counties'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey('states.id', ondelete='CASCADE'),
        nullable=False,
    )

class Mental_Health_Center(db.Model):
    """An individual mental health center (MHC)."""

    __tablename__ = 'mhcs'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    crisis_number = db.Column(
        db.Text,
        nullable=False
    )

    website = db.Column(
        db.Text,
        nullable=False
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey('states.id', ondelete='CASCADE'),
        nullable=False
    )

    states = db.relationship('State', backref='mhcs')

    counties = db.relationship('County', backref='mhcs')




class Zip_Code(db.Model):
    """An individual zip code."""

    __tablename__ = 'zip_codes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    county_id = db.Column(
        db.Integer,
        db.ForeignKey('counties.id', ondelete='CASCADE'),
        nullable=False
    )

    mhc_id = db.Column(
        db.Integer, 
        db.ForeignKey('mhcs.id', ondelete='CASCADE')
    )