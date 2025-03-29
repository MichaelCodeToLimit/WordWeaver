import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    logger.debug("Processing login request")

    if form.validate_on_submit():
        logger.debug(f"Login form validated for email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            logger.info(f"User {user.email} logged in successfully")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password', 'error')
        logger.warning(f"Failed login attempt for email: {form.email.data}")
    elif request.method == 'POST':
        logger.warning("Login form validation failed")
        for field, errors in form.errors.items():
            for error in errors:
                logger.warning(f"Form error in {field}: {error}")

    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    logger.debug(f"Processing registration request. Method: {request.method}")

    if request.method == 'POST':
        logger.debug(f"Form data: email={form.email.data}, username={form.username.data}")
        logger.debug(f"Form validation: {form.validate()}")
        logger.debug(f"Form errors: {form.errors}")

    if form.validate_on_submit():
        logger.info(f"Form validated successfully for user: {form.username.data}")

        try:
            # Check if user already exists
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'error')
                return render_template('register.html', form=form)

            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )

            logger.debug("Attempting to add user to database")
            db.session.add(user)
            db.session.commit()
            logger.info(f"User registered successfully: {user.email}")

            # Log user in
            login_user(user)
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')

    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))