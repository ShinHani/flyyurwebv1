# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
migrate = Migrate(app, db)


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


# with app.app_context():
#     db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    error = False
    upcoming_shows_count = 0
    data = []
    try:
        # City list from venues not duplicated
        areas = db.session.query(
            Venue.city, Venue.state).distinct(Venue.city).all()
        # All venues
        venues = db.session.query(Venue).all()
        # Count shows by upcomming dated
        upcoming_shows_count = db.session.query(Show).filter(
            Show.start_time > datetime.now()).count()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venues could not be listed.')
        print(sys.exc_info())
    else:
        flash('Venues has been successfully listed!')

        for area in areas:
            data.append({
                "city": area.city,
                "state": area.state,
                "venues": [
                    {
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": upcoming_shows_count
                    } for venue in venues if venue.city == area.city
                ]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    error = False
    response = {}

    try:
        search_by_name = db.session.query(Venue).filter(Venue.name.ilike(
            '%' + request.form.get('search_term', '') + '%')).all()
        search_by_city = db.session.query(Venue).filter(Venue.city.ilike(
            '%' + request.form.get('search_term', '') + '%')).all()
        search_by_state = db.session.query(Venue).filter(
            Venue.state.ilike('%' + request.form.get('search_term', '') + '%')).all()
        search = search_by_name + search_by_city + search_by_state

    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venues could not be listed.')
        print(sys.exc_info())
    else:
        flash('Venues has been successfully listed!')

    response = {
        "count": len(search),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
            }for venue in search
        ]
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    error = False
    data1 = {}
    data2 = {}
    data3 = {}

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    try:
        venue = db.get_or_404(Venue, venue_id)
        past_shows = db.session.query(Show.venue_id, Show.start_time, Artist.id, Artist.name, Artist.image_link).join(
            Venue).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows = db.session.query(Show.venue_id, Show.start_time, Artist.id, Artist.name, Artist.image_link).join(
            Venue).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time >= datetime.now()).all()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        # (Check) TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              venue.name + ' could not be displayed.')
        print(sys.exc_info())
    else:
        # (check) on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully displayed!')
        # To display in the template each gender as a whole word by color span
        genres = "".join(venue.genres).strip('{}')
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genres.split(','),
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": [
                {
                    "artist_id": show.id,
                    "artist_name": show.name,
                    "artist_image_link": show.image_link,
                    "start_time": str(show.start_time)
                }for show in past_shows
            ],
            "upcoming_shows": [
                {
                    "artist_id": show.id,
                    "artist_name": show.name,
                    "artist_image_link": show.image_link,
                    "start_time": str(show.start_time)
                }for show in upcoming_shows
            ],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    if seeking_talent == 'y':
        seeking_talent = True
    else:
        seeking_talent = False

    try:
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres,
                      facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        # (Check) TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        venue = db.get_or_404(Venue, venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
        print(sys.exc_info())
    else:
        flash('Venue ' + venue.name + ' was successfully deleted!')

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    error = False
    try:
        # Artist by name
        data = db.session.query(Artist).all()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artists could not be listed.')
        print(sys.exc_info())
    else:
        flash('Artists has been successfully listed!')
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    error = False
    response = {}
    try:
        search_by_name = db.session.query(Artist).filter(
            Artist.name.ilike('%' + request.form.get('search_term', '') + '%')).all()
        search_by_city = db.session.query(Artist).filter(
            Artist.city.ilike('%' + request.form.get('search_term', '') + '%')).all()
        search_by_state = db.session.query(Artist).filter(
            Artist.state.ilike('%' + request.form.get('search_term', '') + '%')).all()
        search = search_by_name + search_by_city + search_by_state
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artists could not be listed.')
        print(sys.exc_info())
    else:
        flash('Artists has been successfully listed!')

    response = {
        "count": 1,
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
            } for artist in search
        ]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    error = False

    try:
        artist = db.get_or_404(Artist, artist_id)
        past_shows = db.session.query(Show.artist_id, Show.start_time, Venue.id, Venue.name, Venue.image_link).join(
            Venue).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows = db.session.query(Show.artist_id, Show.start_time, Venue.id, Venue.name, Venue.image_link).join(
            Venue).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time >= datetime.now()).all()
    except:
        error: True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. The artist could not be displayed.')
        print(sys.exc_info())
    else:
        flash(artist.name + ' has been successfully listed!')
        genres = "".join(artist.genres).strip('{}')

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres.split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": [
                {
                    "venue_id": show.id,
                    "venue_name": show.name,
                    "venue_image_link": show.image_link,
                    "start_time": str(show.start_time)
                }for show in past_shows
            ],
            "upcoming_shows": [
                {
                    "venue_id": show.id,
                    "venue_name": show.name,
                    "venue_image_link": show.image_link,
                    "start_time": str(show.start_time)
                }for show in upcoming_shows
            ],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    error = False
    try:
        artist = db.get_or_404(Artist, artist_id)
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              artist.name + ' could not be displayed.')
        print(sys.exc_info())
    else:
        flash('Artist ' + artist.name + ' was successfully displayed!')

# (Check) TODO: Que se muestren la lista de genres marcadas en el form.control de opciones
    genres = "".join(artist.genres).strip('{}')
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = genres.split(',')
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_venue = True if request.form.get('seeking_venue') else False
    seeking_description = request.form.get('seeking_description')
    try:
        artist = db.get_or_404(Artist, artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.image_link = image_link
        artist.genres = genres
        artist.facebook_link = facebook_link
        artist.website_link = website_link
        artist.seeking_venue = seeking_venue
        artist.seeking_description = seeking_description
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + name + ' could not be displayed.')
        print(sys.exc_info())
    else:
        flash('Artist ' + name + ' was successfully displayed')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    error = False
    try:
        venue = db.get_or_404(Venue, venue_id)
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be displayed.')
        print(sys.exc_info())
    else:
        flash('Venue ' + venue.name + ' was successfully displayed!')

# (Check) TODO: Que se muestren la lista de genres marcadas en el form.control de opciones
        genres = "".join(venue.genres).strip('{}')

        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.genres.data = genres.split(',')
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website_link.data = venue.website_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_talent = True if request.form.get('seeking_talent') else False
    seeking_description = request.form.get('seeking_description')

    try:
        venue = db.get_or_404(Venue, venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.image_link = image_link
        venue.genres = genres
        venue.facebook_link = facebook_link
        venue.website_link = website_link
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be displayed.')
        print(sys.exc_info())
    else:
        flash('Venue ' + name + ' was successfully listed!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_venue = True if request.form.get('seeking_venue') else False
    seeking_description = request.form.get('seeking_description')

    try:
        artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,
                        website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        # (Check) TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    error = False
    data = []
    try:
        # data_list=db.session.query(Show).all()
        show_list = db.session.query(
            Show, Venue, Artist).join(Venue).join(Artist).all()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Shows could not be listed.')
        print(sys.exc_info())
    else:
        flash('Shows has been successfully listed!')

    for show in show_list:
        data.append({
            "venue_id": show.Venue.id,
            "venue_name": show.Venue.name,
            "artist_id": show.Artist.id,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": str(show.Show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
    try:
        show = Show(venue_id=venue_id, artist_id=artist_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
