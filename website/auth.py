from flask import Blueprint, render_template, request, flash, redirect, url_for
# from flask_security import Security, current_user, auth_required, hash_password, SQLAlchemySessionUserDatastore
from .models import User
# from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
# from flask_login import login_user, login_required, logout_user, current_user
from flask_security import login_user, login_required, logout_user, current_user, get_hmac, verify_password
from flask_security.utils import hash_password



auth = Blueprint('auth', __name__)

def init_user_datastore(user_datastore):
    # Initialize user_datastore here
    global _user_datastore
    _user_datastore = user_datastore


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if verify_password(password, user.password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            print(_user_datastore)
            new_user = _user_datastore.create_user(
                email= email,
                password = hash_password(password1),
                first_name = first_name
            )
            # new_user = User(email=email, first_name=first_name, password=generate_password_hash(
            #     password1, method='sha256'))
            # db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


from flask_security import password_reset
@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = _user_datastore.find_user(email=email)
        if user:
            _user_datastore.send_reset_password_instructions(user)
            flash('Password reset instructions sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Invalid email. Please try again.')
    return render_template('forgot_password.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = _user_datastore.get_user_reset_password_token(token)
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            _user_datastore.set_password(user, password)
            _user_datastore.commit()
            flash('Password has been reset successfully.')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please try again.')

    return render_template('reset_password.html', token=token)

