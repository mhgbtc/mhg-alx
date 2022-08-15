#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
from unicodedata import name
from urllib import response
from webbrowser import get
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
from models import db, Artist, Venue, Show, Genre

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# ================================================================== #
# --------------------------- VENUE ---------------------------
# ================================================================== #


@app.route('/')
def index():
    return render_template('pages/home.html')


# =============== Lorsqu'on visite /venues, on liste les venues par City & State =============================

@app.route('/venues')
def venues():
    data = []
    cities = []
    venues = Venue.query.all()  # =======Retourne toutes les venues

    # Etant donner que l'affichage des venues est fonction du city,
    # ======== Je cree une liste de city ========
    for venue in venues:
        cities.append(venue.city)

    # ============ Je filtre ce dont on a besoin (id, name, state) par city =================
    for city in cities:
        zone = Venue.query.with_entities(Venue.id, Venue.name, Venue.state).filter_by(city=city).all()  # =======Me retourne une list of tuples
        state = zone[0].state
        to_send = {
            'city': city,
            'state': state,
            'venues': zone
        }
        data.append(to_send)

    return render_template('pages/venues.html', areas=data)

# ======== J'implemente la fonctionnalite de recherche incensive a la casse =========================


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # =========Je recupere ce que recherche l'utilisateur
    search_term = request.form.get('search_term', '')
    # ====== << ilike >> pour retourner des resultats ne prenant pas en charge la casse
    response = Venue.query.order_by(Venue.name).filter(Venue.name.ilike('%' + search_term + '%')).all()
    count = len(response)
    return render_template('pages/search_venues.html', results=response, count=count)

# ============== Pour afficher une venue unique =====================================

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# ===============Prendre la premiere venue dont l'id est donnee sinon retourne << none >>
	good_venue_id = Venue.query.get(venue_id)

	if not good_venue_id:
		abort(404)

	# Une jointure s'impose parce qu'on fait intervenir la table Show

	shows_query = db.session.query(Show).join(Venue).filter(Venue.id==venue_id).order_by(Show.start_time)

	upcoming_shows = shows_query.filter(Show.start_time >= datetime.datetime.now()).all() #== pour garder les show a venir

	past_shows = shows_query.filter(Show.start_time < datetime.datetime.now()).all() #== pour garder les show passer deja

	# Recuperation de tous les Genres du venue
	venue_genres = []
	for genre in good_venue_id.genres:
		venue_genres.append(genre.name)

	data = {
		"id": good_venue_id.id,
		"name": good_venue_id.name,
		"genres": venue_genres,
		"address": good_venue_id.address,
		"city": good_venue_id.city,
		"state": good_venue_id.state,
		"phone": good_venue_id.phone,
		"website_link": good_venue_id.website_link,
		"facebook_link": good_venue_id.facebook_link,
		"seeking_talent": good_venue_id.seeking_talent,
		"image_link": good_venue_id.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}

	if good_venue_id.seeking_talent:
		data['seeking_description'] = good_venue_id.seeking_description
	else:
		data['seeking_description'] = ''

	return render_template('pages/show_venue.html', venue=data)

# ==========ICI je vais creer une venue==================


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	try:

		form = VenueForm()

		if not form.validate():
			raise Exception('Oups, invalid input')

		venue = Venue(
			name=form.name.data,
			city=form.city.data,
			state=form.state.data,
			address=form.address.data,
			phone=form.phone.data,
			image_link=form.image_link.data,
			facebook_link=form.facebook_link.data,
			seeking_description=form.seeking_description.data,
			website_link=form.website_link.data
		)

		if request.form.get('seeking_talent'):
			venue.seeking_talent = True

		if request.form.getList('genres'):
			for genre in request.form.getList('genres'):
				new_genre = Genre.query.filter(Genre.name==genre).first()
				if new_genre:
					venue.genres.append(new_genre)

		db.session.add(venue)
		db.session.commit()

		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully listed!')
	
	except:
		# on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
		db.session.rollback()
	finally:
		db.session.close()
	
	return render_template('pages/home.html')


# Supprimer une venue unique

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	venue = Venue.query.get(venue_id)
	
	if not venue:
		abort(404)
	
	try:
		db.session.delete(venue)
		db.session.commit()
	except:
		db.session.rollback()
	finally:
		db.session.close()
	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return render_template('pages/venues.html')


# ================================================================== #
# --------------------------- ARTIST ---------------------------
# Les fonctionnalites sont presque pareils, alors ici, je ne commenterai pas assez
# ================================================================== #

# --------------------------Obtenir l'id et le nom de tous les artistes--------------------------------------------#

@app.route('/artists')
def artists():
	data = Artist.query.with_entities(Artist.id, Artist.name).all()
	# TODO: replace with real data returned from querying the database
	return render_template('pages/artists.html', artists=data)

# --------------------------Chercher des artistes avec non sensitive casse--------------------------------------------#


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = Artist.query.order_by(Artist.name).filter(Artist.name.ilike('%' + search_term + '%')).all()
    count = len(response)
    return render_template('pages/search_artists.html', results=response, count=count, search_term=search_term)

# --------------------------Obtenir tous les details sur un artiste selon son id--------------------------------------------#


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	
	good_artist_id = Artist.query.get(artist_id)

	if not good_artist_id:
		abort(404)

	# Une jointure s'impose parce qu'on fait intervenir la table Show

	shows_query = db.session.query(Venue.id.label('venue_id'),Venue.name.label('venue_name'),Venue.image_link.label('venue_image_link'),Show.start_time).filter(Venue.id==Show.venue_id).filter(Show.artist_id==Artist.id).filter(Artist.id==artist_id)

	upcoming_shows = shows_query.filter(Show.start_time >= datetime.datetime.now()).all() #== pour garder les show a venir

	past_shows = shows_query.filter(Show.start_time < datetime.datetime.now()).all() #== pour garder les show passer deja

	# Recuperation de tous les Genres de l'artist
	artist_genres = []
	for genre in good_artist_id.genres:
		artist_genres.append(genre.name)

	data = {
		"id": good_artist_id.id,
		"name": good_artist_id.name,
		"genres": artist_genres,
		"city": good_artist_id.city,
		"state": good_artist_id.state,
		"phone": good_artist_id.phone,
		"website_link": good_artist_id.website_link,
		"facebook_link": good_artist_id.facebook_link,
		"seeking_venue": good_artist_id.seeking_venue,
		"image_link": good_artist_id.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}

	if good_artist_id.seeking_venue:
		data['seeking_description'] = good_artist_id.seeking_description
	else:
		data['seeking_description'] = ''

	return render_template('pages/show_artist.html', artist=data)

# --------------------------Mettre a jour les informations d'un artiste--------------------------------------------#


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
		
		get_artist = Artist.query.get(artist_id)

		if not get_artist:
			abort(404)
		
		form = ArtistForm()

		artist = {
			"id": get_artist.id,
			"name": get_artist.name
		}

		artist_genres = []
		for genre in get_artist.genres:
			artist_genres.append(genre.name)
		
		if artist_genres:
			form.genres.data = artist_genres

		return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
		
		get_artist = Artist.query.get(artist_id)

		if not get_artist:
			abort(404)

		try:
			form = ArtistForm(obj=get_artist)

			if not form.validate():
				raise Exception("Grrrr! You must filled validate input.")

			get_artist.name=form.name.data,
			get_artist.city=form.city.data,
			get_artist.state=form.state.data,
			get_artist.phone=form.phone.data,
			get_artist.image_link=form.image_link.data,
			get_artist.facebook_link=form.facebook_link.data,
			get_artist.seeking_venue=form.seeking_venue.data,
			get_artist.seeking_description=form.seeking_description.data
			get_artist.website_link=form.website_link.data

			edited_artist_genres = []
			if request.form.getlist('genres'):
				for genre in request.form.getlist('genres'):
					edited_genre = Genre.query.filter(Genre.name==genre).first()
					edited_artist_genres.append(edited_genre)

			get_artist.genres=edited_artist_genres

			db.session.commit()

			# on successful db update, flash success
			flash('Artist ' + request.form['name'] + ' was successfully updated!')

		except:
			db.session.rollback()

			# on unsuccessful db update, flash an error instead.
			flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
		finally:
			db.session.close()

		return redirect(url_for('show_artist', artist_id=artist_id))

# --------------------------Mettre a jour les informations d'une venue--------------------------------------------#

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
		
		get_venue = Venue.query.get(venue_id)

		if not get_venue:
			abort(404)

		form = VenueForm(obj=get_venue)

		venue = {
			"id": get_venue.id,
			"name": get_venue.name
		}

		venue_genres = []
		for genre in get_venue.genres:
			venue_genres.append(genre.name)

		form.genres.data=venue_genres
		
		return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

	get_venue = Venue.query.get(venue_id)

	if not get_venue:
		abort(404)

	try:
		
		form = VenueForm(obj=get_venue)

		if not form.validate():
			raise Exception("Grrrr! You must filled validate input.")

		get_venue.name=form.name.data,
		get_venue.city=form.city.data,
		get_venue.state=form.state.data,
		get_venue.address=form.address.data,
		get_venue.phone=form.phone.data,
		get_venue.image_link=form.image_link.data,
		get_venue.facebook_link=form.facebook_link.data,
		get_venue.website_link=form.website_link.data,
		get_venue.seeking_talent=form.seeking_talent.data,
		get_venue.seeking_description=form.seeking_description.data

		edited_venue_genres = []				
		for genre in get_venue.genres:
			edited_genre = Genre.query.filter(Genre.name==genre).first()
			edited_venue_genres.append(edited_genre)

		get_venue.genres=edited_venue_genres

		db.session.commit()

		flash('Venue ' + request.form['name'] + ' was successfully updated')
	except:
		flash('An error occured. Venue ' + request.form['name'] + ' could not be updated!')
		db.session.rollback()
	finally:
		db.session.close()
		
	return redirect(url_for('show_venue', venue_id=venue_id))

# --------------------------Implementation de la creation d'un artiste--------------------------------------------#


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

	try:

		form = ArtistForm()

		if not form.validate:
			raise Exception('Oups, invalid input')

		artist = Artist(
			name=form.name.data,
			city=form.city.data,
			state=form.state.data,
			phone=form.phone.data,
			image_link=form.image_link.data,
			facebook_link=form.facebook_link.data,
			website_link=form.website_link.data,
			seeking_description=form.seeking_description.data
		)

		if request.form.get('seeking_venue'):
			artist.seeking_venue=True

		if request.form.getlist('genres'):
			for genre in request.form.getlist('genres'):
				new_genre=Genre.query.filter(Genre.name==genre).first()
				artist.genres.append(new_genre)

		db.session.add(artist)
		db.session.commit()

		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
	except:
		# on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
		db.session.rollback()
	finally:
		db.session.close()

	return render_template('pages/home.html')

# ================================================================== #
# --------------------------- SHOW ---------------------------
# ================================================================== #

@app.route('/shows')
def shows():
    all_shows = Show.query.all()
    data = []
    for one_show in all_shows:
        single_show = {
            "venue_id": one_show.venue_id,
            "venue_name": Venue.query.with_entities(Venue.name).filter_by(id=one_show.venue_id).first(),
            "artist_id": one_show.artist_id,
            "artist_name": Artist.query.with_entities(Artist.name).filter_by(id=one_show.artist_id).first(),
            "artist_image_link": Artist.query.with_entities(Artist.image_link).filter_by(id=one_show.artist_id).first(),
            "start_time": str(one_show.start_time)
        }
        data.append(single_show)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

	try:

		form = ShowForm()

		if not form.validate():
			raise Exception("Failure! Invalid input")

		show = Show(
			venue_id=form.venue_id.data,
			artist_id=form.artist_id.data,
			start_time=form.start_time.data
		)

		db.session.add(show)
		db.session.commit()

		# on successful db insert, flash success
		flash('Show was successfully listed!')
	except:
		db.session.rollback()

		# on unsuccessful db insert, flash an error instead.
		flash('An error occurred. Show could not be listed.')
	finally:
		db.session.close()

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
