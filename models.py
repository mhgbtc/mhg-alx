from flask_sqlalchemy import  SQLAlchemy
from sqlalchemy import ARRAY, String

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Show Model
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show: id: {self.id} venue_id: {self.venue_id} artist_id: {self.artist_id} start {self.start_time}>'

#----------------------------------------------------------------------------#
# Venue Model
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    #=================== Une venue a plusieurs shows =============================#
    shows = db.relationship("Show", backref="venue", cascade="all, delete")

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.state} {self.address} {self.phone} {self.genres} {self.facebook_link} {self.image_link} {self.image_link} {self.seeking_talent} {self.seeking_description}>'

#----------------------------------------------------------------------------#
# Artist Model
#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    #=================== Un artiste a plusieurs shows =============================#
    shows = db.relationship("Show", backref="artist", cascade="all, delete")

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_venue} {self.seeking_description}>'
