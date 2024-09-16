from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from flask_sqlalchemy import SQLAlchemy
from forms import *


db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = 'show'

    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow, primary_key=True)
    venue_child = db.relationship("Venue", back_populates="artists")
    artist_parent = db.relationship("Artist", back_populates="venues")


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(120), nullable=True)
    artists = db.relationship("Show", back_populates="venue_child")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(120), nullable=True)
    venues = db.relationship("Show", back_populates="artist_parent")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
