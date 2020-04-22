# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import sys
from datetime import datetime
from logging import Formatter, FileHandler

import babel.dates
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment

from forms import ShowForm, VenueForm, ArtistForm
from models.models import Show
from models.models import Venue
from models.models import Artist
from models.database import db

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# ✅ TODO: connect to a local postgresql database
db.init_app(app)

Migrate(app, db)


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


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
    territories = (
        Venue
            .query
            .with_entities(Venue.city, Venue.state)
            .group_by(Venue.city, Venue.state)
            .all()
    )

    territories_and_venues = []

    for territory in territories:
        territory_venues = (
            Venue
                .query
                .all()
        )

        territories_and_venues.append(
            {
                "city": territory.city,
                "state": territory.state,
                "venues": territory_venues,
            }
        )

    return render_template('pages/venues.html', areas=territories_and_venues)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # ✅ TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_input = request.form.get("search_term", None)

    formatted_input = "%{}%".format(search_input)

    fuzzy_matches = Venue.query.filter(
        Venue.name.ilike(formatted_input)
    ).all()

    fuzzy_matches_count = len(fuzzy_matches)

    response = {
        "count": fuzzy_matches_count,
        "data": fuzzy_matches
    }

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # ✅ TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

    # Render 404 page if the venue is not found, and flash the user to make them aware
    if venue is None:
        flash('ERROR: venue with ID ' + str(venue_id) + ' does not exist!')
        return render_template('errors/404.html'), 404

    # Otherwise continue to render the venue page and information
    else:
        shows = Show.query.filter(Show.venue_id == venue_id).all()

        past_show_data = []
        upcoming_show_data = []

        for show in shows:
            base_start_datetime = show.start_time.strftime("%d/%m/%Y%H:%M:%S")
            formatted_start_datetime = datetime.strptime(base_start_datetime, "%d/%m/%Y%H:%M:%S")
            is_upcoming_show = formatted_start_datetime > datetime.now()

            venues = Venue.query.filter(Venue.id == show.venue_id).all()

            for venue in venues:

                venue_data = {
                    "venue_id": venue.id,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
                }

                if is_upcoming_show:
                    upcoming_show_data.append(venue_data)
                else:
                    past_show_data.append(venue_data)

        venue_data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres.split(','),
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_show_data,
            "upcoming_shows": upcoming_show_data,
            "past_shows_count": len(past_show_data),
            "upcoming_shows_count": len(upcoming_show_data),
        }

    return render_template('pages/show_venue.html', venue=venue_data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # ✅ TODO: insert form data as a new Venue record in the db, instead
    # ✅ TODO: modify data to be the data object returned from db insertion
    venue_data = VenueForm(request.form)

    error = False
    try:
        # Create new db Venue record
        new_venue = Venue(
            name=venue_data.name.data,
            city=venue_data.city.data,
            state=venue_data.state.data,
            address=venue_data.address.data,
            phone=venue_data.phone.data,
            genres=','.join(venue_data.genres.data),
            website=venue_data.website.data,
            facebook_link=venue_data.facebook_link.data,
            image_link=venue_data.image_link.data,
            seeking_talent=venue_data.seeking_talent.data,
            seeking_description=venue_data.seeking_description.data,
        )

        db.session.add(new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            flash('Venue \'' + venue_data.name.data + '\' was successfully listed!')
        else:
            # ✅ TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue \'' + venue_data.name.data + '\' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    #   SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # 🌟 BONUS CHALLENGE: TODO: Implement a button to delete a Venue on a Venue Page, have it so that
    #                      clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # ✅ TODO: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    basic_artist_details = []

    for artist in all_artists:
        basic_artist_details.append(
            {
                "id": artist.id,
                "name": artist.name,
            }
        )

    return render_template('pages/artists.html', artists=basic_artist_details)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # ✅ TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_input = request.form.get("search_term", None)

    formatted_input = "%{}%".format(search_input)

    fuzzy_matches = Artist.query.filter(
        Artist.name.ilike(formatted_input)
    ).all()

    fuzzy_matches_count = len(fuzzy_matches)

    response = {
        "count": fuzzy_matches_count,
        "data": fuzzy_matches
    }

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # ✅ TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

    # Render 404 page if the artist is not found, and flash the user to make them aware.
    if artist is None:
        flash('ERROR: artist with ID ' + str(artist_id) + ' does not exist!')
        return render_template('errors/404.html'), 404

    # Otherwise continue to render the artist page and information.
    else:
        shows = Show.query.filter(Show.artist_id == artist_id).all()

        past_show_data = []
        upcoming_show_data = []

        for show in shows:
            base_start_datetime = show.start_time.strftime("%d/%m/%Y%H:%M:%S")
            formatted_start_datetime = datetime.strptime(base_start_datetime, "%d/%m/%Y%H:%M:%S")
            is_upcoming_show = formatted_start_datetime > datetime.now()

            venues = Venue.query.filter(Venue.id == show.venue_id).all()

            for venue in venues:

                venue_data = {
                    "venue_id": venue.id,
                    "venue_name": venue.name,
                    "venue_image_link": venue.image_link,
                    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
                }

                if is_upcoming_show:
                    upcoming_show_data.append(venue_data)
                else:
                    past_show_data.append(venue_data)

        artist_data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres.split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_show_data,
            "upcoming_shows": upcoming_show_data,
            "past_shows_count": len(past_show_data),
            "upcoming_shows_count": len(upcoming_show_data),
        }

    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # ✅ TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

    # Render 404 page if the artist is not found, and flash the user to make them aware
    if artist is None:
        flash('ERROR: artist with ID ' + str(artist) + ' does not exist!')
        return render_template('errors/404.html'), 404

    # Otherwise continue to render the artist edit form, populated with existing data
    else:
        existing_artist_data = {
            "id": artist.id,
            "name": artist.name,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "image_link": artist.image_link,
            "genres": ','.join(artist.genres),
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description
        }

        form = ArtistForm(data=existing_artist_data)

        return render_template('forms/edit_artist.html', form=form, artist=existing_artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # ✅ TODO: take values from the form submitted, and update existing
    #       artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter(Artist.id == artist_id).one()
    artist_data = ArtistForm(request.form)

    error = False
    try:
        # Update existing data with new form data
        artist.name = artist_data.name.data,
        artist.city = artist_data.city.data,
        artist.state = artist_data.state.data,
        artist.phone = artist_data.phone.data,
        artist.genres = ','.join(artist_data.genres.data),
        artist.website = artist_data.website.data,
        artist.facebook_link = artist_data.facebook_link.data,
        artist.image_link = artist_data.image_link.data,
        artist.seeking_venue = artist_data.seeking_venue.data,
        artist.seeking_description = artist_data.seeking_description.data,

        # Update db record data for artist with new form data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not error:
            flash('Artist ' + artist_data.name.data + ' was successfully updated!')
        else:
            # ✅ TODO: on unsuccessful db update, flash an error instead.
            flash('An error occurred. Artist ' + artist_data.name.data + ' could not be updated.')
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # ✅ TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

    # Render 404 page if the venue is not found, and flash the user to make them aware
    if venue is None:
        flash('ERROR: venue with ID ' + str(venue) + ' does not exist!')
        return render_template('errors/404.html'), 404

    # Otherwise continue to render the venue edit form, populated with existing data
    else:
        existing_venue_data = {
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "image_link": venue.image_link,
            "genres": ','.join(venue.genres),
            "address": venue.address,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description
        }

        form = VenueForm(data=existing_venue_data)

    return render_template('forms/edit_venue.html', form=form, venue=existing_venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # ✅ TODO: take values from the form submitted, and update existing
    #       venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter(Venue.id == venue_id).one()
    venue_data = VenueForm(request.form)

    error = False
    try:
        # Update existing data with new form data
        venue.name = venue_data.name.data,
        venue.city = venue_data.city.data,
        venue.state = venue_data.state.data,
        venue.phone = venue_data.phone.data,
        venue.genres = ','.join(venue_data.genres.data),
        venue.address = venue_data.address.data,
        venue.website = venue_data.website.data,
        venue.facebook_link = venue_data.facebook_link.data,
        venue.image_link = venue_data.image_link.data,
        venue.seeking_talent = venue_data.seeking_talent.data,
        venue.seeking_description = venue_data.seeking_description.data,

        # Update db record data for venue with new form data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not error:
            flash('Venue ' + venue_data.name.data + ' was successfully updated!')
        else:
            # ✅ TODO: on unsuccessful db update, flash an error instead.
            flash('An error occurred. Venue ' + venue_data.name.data + ' could not be updated.')
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # ✅ TODO: insert form data as a new Venue record in the db, instead
    # ✅ TODO: modify data to be the data object returned from db insertion
    artist_data = ArtistForm(request.form)

    error = False
    try:
        # Create new db Show record
        new_artist = Artist(
            name=artist_data.name.data,
            city=artist_data.city.data,
            state=artist_data.state.data,
            phone=artist_data.phone.data,
            image_link=artist_data.image_link.data,
            genres=','.join(artist_data.genres.data),
            website=artist_data.website.data,
            facebook_link=artist_data.facebook_link.data,
            seeking_venue=artist_data.seeking_venue.data,
            seeking_description=artist_data.seeking_description.data
        )

        db.session.add(new_artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not error:
            flash('Artist ' + artist_data.name.data + ' was successfully listed!')
        else:
            # ✅ TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' + artist_data.name.data + ' could not be listed.')
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # ✅ TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_shows = Show.query.order_by('start_time').all()
    upcoming_shows = []

    for show in all_shows:
        artist = Artist.query.filter(Artist.id == show.artist_id).one()
        venue = Venue.query.filter(Venue.id == show.venue_id).one()

        base_start_datetime = show.start_time.strftime("%d/%m/%Y%H:%M:%S")
        formatted_start_datetime = datetime.strptime(base_start_datetime, "%d/%m/%Y%H:%M:%S")
        is_upcoming_show = formatted_start_datetime > datetime.now()

        if is_upcoming_show:
            upcoming_shows.append(
                {
                    "id": show.id,
                    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
                    "venue_id": venue.id,
                    "venue_name": venue.name,
                    "artist_id": artist.id,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link
                }
            )

    return render_template('pages/shows.html', shows=upcoming_shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # ✅ TODO: insert form data as a new Show record in the db, instead
    show_data = ShowForm(request.form)

    error = False
    try:
        # Create new db Show record
        new_show = Show(
            artist_id=show_data.artist_id.data,
            venue_id=show_data.venue_id.data,
            start_time=show_data.start_time.data
        )

        db.session.add(new_show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not error:
            flash("Show was successfully listed!")
        else:
            # ✅ TODO: on unsuccessful db insert, flash an error instead.
            flash("An error occurred. Show could not be listed.")
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
