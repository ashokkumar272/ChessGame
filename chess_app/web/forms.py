"""
Forms for the Flask web application.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from chess_app.db.mongo_db import get_user_by_username


class LoginForm(FlaskForm):
    """Form for user login."""
    
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for user registration."""
    
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate that the username is not already taken."""
        user = get_user_by_username(username.data)
        if user is not None:
            raise ValidationError('Please use a different username.')


class SaveGameForm(FlaskForm):
    """Form for saving a game state."""
    
    name = StringField('Game Name', validators=[DataRequired(), Length(max=64)])
    fen = StringField('FEN', validators=[DataRequired()])
    moves = FieldList(StringField('Move'))
    difficulty = SelectField('Difficulty', choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    submit = SubmitField('Save Game')