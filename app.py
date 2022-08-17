#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from os import abort
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from datetime import datetime as dt
from models import *

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
	if isinstance(value, str):
		date = dateutil.parser.parse(value)
	else:
		date = value
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
	form = VenueForm()
	# =========Je recupere ce que recherche l'utilisateur
	search_term = request.form.get('search_term', '')
	# ====== << ilike >> pour retourner des resultats ne prenant pas en charge la casse
	venues = Venue.query.order_by(Venue.name).filter(Venue.name.ilike('%' + search_term + '%')).all()
	response = {
		"data": [],
		"count": 0
	}
	for venue in venues:
		response['data'].append({
			'id': venue.id,
			'name': venue.name
		})
		response['count'] += 1

	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''), form=form)

# ============== Pour afficher une venue unique =====================================

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# ===============Prendre la premiere venue dont l'id est donnee sinon retourne << none >>
	good_venue_id = Venue.query.get(venue_id)

	if not good_venue_id:
		abort(404)

	# J'essaye de recuperer les informations par rapport aux spectacles passer et a venir d'une venue. 
	# Etant donne la relation entre une venue et les artists, une jointure s'impose sur le modele artist pour avoir d'informations sur l(les)'artists
	# qui a un spectacle dans le lieu

	upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
	upcoming_shows = []
	for show in upcoming_shows_query:
		upcoming_shows.append({
		"artist_id": show.artist_id,
		"artist_name": show.artist.name,
		"artist_image_link": show.artist.image_link,
		"start_time": show.start_time
		})

	past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
	past_shows = []
	for show in past_shows_query:
		past_shows.append({
		"artist_id": show.artist_id,
		"artist_name": show.artist.name,
		"artist_image_link": show.artist.image_link,
		"start_time": show.start_time
		})

	data = {
		"id": good_venue_id.id,
		"name": good_venue_id.name,
		"address": good_venue_id.address,
		"city": good_venue_id.city,
		"state": good_venue_id.state,
		"phone": good_venue_id.phone,
		"genres": good_venue_id.genres,
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
	form = VenueForm()
	if form.validate_on_submit():
		try:
			venue = Venue(
				name=form.name.data,
				city=form.city.data,
				state=form.state.data,
				address=form.address.data,
				phone=form.phone.data,
				genres=form.genres.data,
				image_link=form.image_link.data,
				facebook_link=form.facebook_link.data,
				seeking_description=form.seeking_description.data,
				website_link=form.website_link.data
			)

			if form.seeking_talent.data:
				venue.seeking_talent=True

			db.session.add(venue)
			db.session.commit()

			# on successful db insert, flash success
			flash('Venue ' + form.name.data + ' was successfully listed!')
			return redirect(url_for('index'))
		except Exception as e:
			# on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
			print(str(e))
			db.session.rollback()
			return render_template('forms/new_venue.html', form=form)
		finally:
			db.session.close()
	else:
		flash(form.errors)
		return render_template('forms/new_venue.html', form=form)


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
	except Exception as e:
		db.session.rollback()
		print(str(e))
	finally:
		db.session.close()
	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return render_template('pages/venues.html')

# ================================================================== #
# --------------------------- ARTIST ---------------------------
# Les fonctionnalites sont presque pareilles, alors ici, je ne commenterai pas assez
# ================================================================== #

# --------------------------Obtenir l'id et le nom de tous les artistes--------------------------------------------#

@app.route('/artists')
def artists():
	form = ArtistForm()
	data = Artist.query.all()
	return render_template('pages/artists.html', artists=data, form=form)

# --------------------------Chercher des artistes avec non sensitive casse--------------------------------------------#

@app.route('/artists/search', methods=['POST'])
def search_artists():
	form = ArtistForm()
	search_term = request.form.get('search_term', '')
	artists = Artist.query.order_by(Artist.name).filter(Artist.name.ilike('%' + search_term + '%')).all()
	response = {
		"count": 0,
		"data": []
	}
	for artist in artists:
		response["count"] += 1
		response["data"].append({
			"id": artist.id,
			"name": artist.name
		})
	return render_template('pages/search_artists.html', results=response, search_term = request.form.get('search_term', ''), form=form)

# --------------------------Obtenir tous les details sur un artiste selon son id--------------------------------------------#

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	form = ArtistEditForm()
	good_artist_id = Artist.query.filter_by(id=artist_id).first()

	if not good_artist_id:
		abort(404)

	upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
	upcoming_shows = []
	for show in upcoming_shows_query:
		upcoming_shows.append({
		"venue_id": show.venue_id,
		"venue_name": show.venue.name,
		"venue_image_link": show.venue.image_link,
		"start_time": show.start_time
		})

	past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
	past_shows = []
	for show in past_shows_query:
		past_shows.append({
		"venue_id": show.venue_id,
		"venue_name": show.venue.name,
		"venue_image_link": show.venue.image_link,
		"start_time": show.start_time
		})

	data = {
		"id": good_artist_id.id,
		"name": good_artist_id.name,
		"genres": good_artist_id.genres,
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

	return render_template('pages/show_artist.html', artist=data, form=form)

# --------------------------Mettre a jour les informations d'un artiste--------------------------------------------#


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
		form = ArtistEditForm()
		artist = Artist.query.filter_by(id=artist_id).first()

		if not artist:
			abort(404)

		return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	form = ArtistEditForm()

	if form.validate_on_submit():
		try:
			artist = Artist.query.get(artist_id)

			if not artist:
				abort(404)

			artist.name=form.name.data,
			artist.city=form.city.data,
			artist.state=form.state.data,
			artist.phone=form.phone.data,
			artist.genres=form.genres.data,
			artist.image_link=form.image_link.data,
			artist.facebook_link=form.facebook_link.data,
			artist.seeking_description=form.seeking_description.data
			artist.website_link=form.website_link.data

			if form.seeking_venue.data:
				artist.seeking_venue=True

			db.session.commit()

			# on successful db update, flash success
			flash('Artist ' + artist.name + ' was successfully updated!')
			return redirect(url_for('show_artist', artist_id=artist_id))

		except Exception as e:
			db.session.rollback()
			# on unsuccessful db update, flash an error instead.
			flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
			print(str(e))
			return render_template('forms/edit_artist.html', form=form)
		finally:
			db.session.close()
	else:
		flash(form.errors)
		return render_template('forms/edit_artist.html', form=form)

# --------------------------Mettre a jour les informations d'une venue--------------------------------------------#

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
		form = VenueEditForm()
		venue = Venue.query.filter_by(id=venue_id).first()

		if not venue:
			abort(404)
		
		return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	form = VenueEditForm()
	if form.validate_on_submit():
		try:
			venue = Venue.query.get(venue_id)

			if not venue:
				abort(404)

			venue.name=form.name.data,
			venue.city=form.city.data,
			venue.state=form.state.data,
			venue.address=form.address.data,
			venue.phone=form.phone.data,
			venue.genres=form.genres.data,
			venue.image_link=form.image_link.data,
			venue.facebook_link=form.facebook_link.data,
			venue.website_link=form.website_link.data,
			venue.seeking_description=form.seeking_description.data

			if form.seeking_talent.data:
				venue.seeking_talent=True

			db.session.commit()
			flash('Venue ' + venue.name + ' was successfully updated')
			return redirect(url_for('show_venue', venue_id=venue_id))
		except Exception as e:
			flash('An error occured. Venue ' + request.form['name'] + ' could not be updated!')
			print(str(e))
			db.session.rollback()
			return render_template('forms/edit_venue.html', form=form)
		finally:
			db.session.close()
			
	else:	
		flash(form.errors)
		return render_template('forms/edit_venue.html', form=form)

# --------------------------Implementation de la creation d'un artiste--------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	form = ArtistForm()
	if form.validate_on_submit():

		try:

			artist = Artist(
				name=form.name.data,
				city=form.city.data,
				state=form.state.data,
				phone=form.phone.data,
				genres=form.genres.data,
				image_link=form.image_link.data,
				facebook_link=form.facebook_link.data,
				website_link=form.website_link.data,
				seeking_description=form.seeking_description.data
			)

			if form.seeking_venue.data:
				artist.seeking_venue=True

			db.session.add(artist)
			db.session.commit()

			# on successful db insert, flash success
			flash('Artist ' + request.form['name'] + ' was successfully listed!')
			return redirect(url_for("index"))
		except Exception as e:
			# on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
			print(str(e))
			db.session.rollback()
			return render_template('forms/new_artist.html', form=form)
		finally:
			db.session.close()
	else:
		flash(form.errors)
		return render_template('forms/new_artist.html', form=form)

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
	form = ShowForm()
	if form.validate_on_submit():

		try:

			show = Show(
				venue_id=form.venue_id.data,
				artist_id=form.artist_id.data,
				start_time=form.start_time.data
			)

			db.session.add(show)
			db.session.commit()

			# on successful db insert, flash success
			flash('Show was successfully listed!')
			return redirect(url_for("index"))
		except Exception as e:
			db.session.rollback()

			# on unsuccessful db insert, flash an error instead.
			flash('An error occurred. Show could not be listed.')
			print(str(e))
			return render_template('forms/new_show.html', form=form)
		finally:
			db.session.close()
	else:
		flash(form.errors)
		return render_template('forms/new_show.html', form=form)


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
