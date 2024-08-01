from flask import Flask, render_template, url_for, request, abort, Blueprint, flash, redirect
# from flask_login import login_required, current_user
from flask_security import auth_required, current_user #login_required
import requests

from . import db
import os
from .models import User
from .database import add_refresh_token


connectAmazon = Blueprint('connectAmazon', __name__)

@connectAmazon.route('/connect_amazon')
@auth_required()
#@auth_required("token") 
#@login_required
def connect_amazon():
   # Redirect the user to Amazon LWA authorization endpoint
    redirect_url_parameter= url_for('connectAmazon.callback',_external=True )
  
    final_redirect_url = (
      'https://sellercentral.amazon.com/apps/authorize/consent?'
        f'application_id=amzn1.sp.solution.eba8a784-ea8a-424b-8aa3-58cd53c36768&'
         f'state=stateexample&'
         f'{redirect_url_parameter}&'
         f'version=beta'
    )
    return redirect(final_redirect_url)


@connectAmazon.route('/callback')
@auth_required()
#@auth_required("token") 
#@login_required
def callback():
  try:
    state = request.args.get('state')
    selling_partner_id = request.args.get('selling_partner_id')
    spapi_oauth_code = request.args.get('spapi_oauth_code')
    redirect_url=url_for('views.account', _external=True)

    if(state == 'stateexample' ):
        token_url = 'https://api.amazon.com/auth/o2/token'
        data = {
            'grant_type': 'authorization_code',
            'code': spapi_oauth_code,
            'client_id': os.environ['LWA_CLIENT_ID'],
            'client_secret': os.environ['LWA_CLIENT_SECRET'],
            'redirect_uri': redirect_url
        }
        response = requests.post(token_url, data=data).json()
        print("Response:")
        print(response)
        if 'refresh_token' in response:
            refresh_token = response['refresh_token']
            add_refresh_token(current_user.id, refresh_token)
            print('Refresh Token:')
            print(refresh_token)
            flash( 'Amazon Connection successful! You can now make SP-API calls.', category = 'success')
            return redirect('/account')
        else:
            error = response.get('error_description', 'Login failed. Please try again.')
            flash( f'Login failed. Reason: {error}', category = 'error')
            return redirect('/account')
    else:
      flash( 'Login failed. Reason: State values do not match', category = 'error')
      return redirect('/account')

  except Exception as e:
    print("Error: " + str(e))
    db.session.rollback()
    return 'Error. Try refreshing the page or going to the home page.'
        
