from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, SubmitField, TelField
from wtforms.validators import DataRequired, URL, ValidationError
import re

state_available = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

genre_available =  [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]

def validate_genre(form, genre):
    genres = [
        'Alternative',
        'Blues',
        'Classical',
        'Country',
        'Electronic',
        'Folk',
        'Funk',
        'Hip-Hop',
        'Heavy Metal',
        'Instrumental',
        'Jazz',
        'Musical Theatre',
        'Pop',
        'Punk',
        'R&B',
        'Reggae',
        'Rock n Roll',
        'Soul',
        'Other',
    ]
    for genre in genre.data:
        if genre not in genres:
            raise ValidationError(
                'This genre is not allowed'
            )

# Fonction pour me rassurer de recevoir des entrees numeriques valides
def is_valid_id(form, id):
    if not str(id.data).isnumeric():
        raise ValidationError("Hey! This must be numeric")
    return True

# Implementation de la validation du numero de telephone

# ========================================================
#================Explanation: Only xxx-xxx-xxxx phone number will be accepted
# ========================================================

def phone_number_validation(form, phone):
    my_validate_phone = '^[0-9]{3}-[0-9]{3}-[0-9]{4}$'
    match = re.search(my_validate_phone, phone.data)
    if not match:
        raise ValidationError(
            "Error ! Phone number must be in format xxx-xxx-xxxx"
        )


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(), is_valid_id]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(), is_valid_id]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )
    submit = SubmitField("Create Show")

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_available
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = TelField(
        'phone',
        validators=[DataRequired(), phone_number_validation]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), validate_genre],
        choices=genre_available
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )
    seeking_talent = BooleanField( 'seeking_talent' )
    seeking_description = StringField(
        'seeking_description'
    )
    submit = SubmitField("Create Venue")

class VenueEditForm(VenueForm):
    submit = SubmitField("Edit Venue")

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_available
    )
    phone = TelField(
        'phone',
        # TODO implement validation logic for state
        validators=[phone_number_validation]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genre],
        choices=genre_available
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )
    website_link = StringField(
        'website_link'
     )
    seeking_venue = BooleanField( 'seeking_venue' )
    seeking_description = StringField(
        'seeking_description'
     )
    submit = SubmitField("Create Artist")

class ArtistEditForm(ArtistForm):
    submit = SubmitField("Edit Artist")
