from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
# from flask_security import Security, current_user, auth_required, hash_password, SQLAlchemySessionUserDatastore
from .models import User
# from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
# from flask_login import login_user, login_required, logout_user, current_user
from flask_security import login_user, auth_required, logout_user, current_user, get_hmac, verify_password, send_mail, ForgotPasswordForm, login_required, anonymous_user_required
from flask_security.utils import hash_password
import secrets
import urllib.parse
from datetime import datetime, timedelta
import pytz


auth = Blueprint('auth', __name__)


# def init_user_datastore(user_datastore):
#   # Initialize user_datastore here
#   global _user_datastore
#   _user_datastore = user_datastore
# Access in views or functions



@auth.route('/login', methods=['GET', 'POST'])
@anonymous_user_required
def login():
  try: 
    if request.method == 'POST':
      email = request.form.get('email')
      password = request.form.get('password')
  
      user = User.query.filter_by(email=email).first()
      if user:
        if verify_password(password, user.password):
          login_user(user, remember=False)
          flash('Logged in successfully!', category='success')
          return redirect(url_for('views.home'))
        else:
          flash('Incorrect credentials', category='error')
      else:
        flash('Incorrect credentials', category='error')
  
    return render_template("login.html", user=current_user)
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error. Try refreshing the page or going to the home page.'


@auth.route('/logout')
@auth_required()
#@auth_required("token") 
#@login_required
def logout():
  try: 
     if current_user.is_authenticated:
      logout_user()
      return redirect(url_for('views.landing'))
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error. Try refreshing the page or going to the home page.'


@auth.route('/sign-up', methods=['GET', 'POST'])
@anonymous_user_required
def sign_up():
  try:
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
        time = datetime.now(pytz.timezone('America/New_York'))
        _user_datastore = current_app.config['USER_DATASTORE']
        new_user = _user_datastore.create_user(email=email,
                                               password=hash_password(password1),
                                               first_name=first_name, date_joined = time)
        # new_user = User(email=email, first_name=first_name, password=generate_password_hash(
        #     password1, method='sha256'))
        # db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=False)
        print(f"New User Signed up! : userID-{current_user.id}   Email-{current_user.email}    Name-{current_user.first_name} ")
        flash('Account created!', category='success')
        return redirect(url_for('views.home'))
  
    return render_template("sign_up.html", user=current_user)
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error. Try refreshing the page or going to the home page.'

from flask_security import password_reset

from flask_security.signals import password_reset, reset_password_instructions_sent
from flask_security.utils import config_value, get_token_status, hash_data, hash_password, url_for_security, verify_hash


@auth.route('/forgot_password', methods=['GET', 'POST'])
@anonymous_user_required
def forgot_password():
  try:
    forgot_password_form = ForgotPasswordForm()
    if forgot_password_form.validate_on_submit():
      email = forgot_password_form.email.data
      print(f"Received email: {email}")
      _user_datastore = current_app.config['USER_DATASTORE']
      user = _user_datastore.find_user(email=email)
      if user:
        user = user
        security = current_app.security
        # reset_token = secrets.token_urlsafe(32)
        # encoded_reset_token = urllib.parse.quote(reset_token, safe='')
        reset_token = generate_reset_password_token(user)
        print("RESET TOKEN GENERATED")
        # print(reset_token)
        
        password_reset_link = f"https://amaze-software.com/reset_password?token={reset_token}"
        context = {
            'reset_link': password_reset_link,
            'reset_token': reset_token,
            'user': user,
            'security': security
        }
        send_mail("Password Reset", email, 'reset_instructions', **context)
        flash('Password reset instructions sent to your email.', category ='success')
        reset_password_instructions_sent.send(
        current_app._get_current_object(), user=user, token=reset_token
    )
        return redirect(url_for('auth.login'))
      # else:
        # flash('Invalid email. Please try again.')

    # Render the template and pass the form to the context
    return render_template('forgot_password.html', forgot_password_form=forgot_password_form)
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error. Try refreshing the page or going to the home page.'


from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import current_user, login_user, logout_user, send_mail, ForgotPasswordForm, ResetPasswordForm, login_required
import secrets
import urllib.parse


@auth.route('/reset_password', methods=['GET', 'POST'])
@anonymous_user_required
def reset_password():
  try:
    print('Test1')
    reset_password_form = ResetPasswordForm()
    print('Test2')
    reset_token = request.args.get('token')
    print('Test3')
    # reset_token = 'a'
    print("RECEIVED RESET_TOKEN:")
    print(reset_token)
    print('Test4')
    expired, invalid, user, data = reset_password_token_status(reset_token)
    print('Test5')
    print("TOKEN STATUS:")
    print("Expired_value: " + str(expired))
    print("invalid_value " + str(invalid))
    print("User_value:", user)
    print("Data:", data)


    if expired:
        flash('The password reset link has expired. Please request a new one.')
        return redirect(url_for('auth.forgot_password'))

    if invalid or not user:
        flash('Invalid password reset token.')
        return redirect(url_for('auth.forgot_password'))
  

    if request.method == 'POST':
      # print("FORM KEYS:")
      # print(request.form.keys())
      password = request.form['password']
      confirm_password = request.form['password_confirm']
      if password == confirm_password:
        new_password_hash = hash_password(password)
        user.password = new_password_hash
        db.session.commit()
        flash('Password has been reset successfully.')
        context={}
        send_mail( 'EMAIL_SUBJECT_PASSWORD_NOTICE', user.email, 'reset_notice', **context)
        password_reset.send (current_app._get_current_object(), user=user)
        return redirect(url_for('auth.login'))
      else:
        flash('Passwords do not match. Please try again.')

    reset_password_link = f"https://amaze-software.com/reset_password?token={reset_token}"
    return render_template('reset_password.html', reset_password_link=reset_password_link, reset_password_form=reset_password_form)
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error. Try refreshingthe pafe or going to the home page.'


def generate_reset_password_token(user):
    """Generates a unique reset password token for the specified user.

    :param user: The user to work with
    """
    password_hash = hash_data(user.password) if user.password else None
    data = [str(user.id), password_hash]
    return current_app.security.reset_serializer.dumps(data)

def reset_password_token_status(token):
  try:
    print('TestA')
    """Returns the expired status, invalid status, and user of a password reset
    token. For example::

        expired, invalid, user, data = reset_password_token_status('...')

    :param token: The password reset token
    """
    expired, invalid, user, data = get_token_status(
        token, 'reset', 'RESET_PASSWORD', return_data=True
    )
    print(get_token_status(token, 'reset', 'RESET_PASSWORD', return_data=True))
    print('TestB')
    userID= None
    if data:
      userID = data[0]
      user = User.query.filter_by(id=userID).first()
    if not invalid and userID:
        if user.password:
            if not verify_hash(data[1], user.password):
                invalid = True

    return expired, invalid, user, data
  except Exception as e:
    print('ERROR: ' + str(e))
    db.session.rollback()
    return 'Error: ' + str(e)

