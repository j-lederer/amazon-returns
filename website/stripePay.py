from flask import Flask, render_template, url_for, request, abort, Blueprint, flash, redirect, current_app
# from flask_login import login_required, current_user
from flask_security import login_required, current_user


import stripe
from . import db
import os
from .models import User, Stripecustomer




stripePay = Blueprint('stripePay', __name__)



@stripePay.route('/stripeHome')
@login_required
def stripeHome():
  '''
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1GtKWtIdX0gthvYPm4fJgrOr',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('stripeHome', _external=True),
    )
    '''
  return render_template(
    'stripeHome.html',
    #checkout_session_id=session['id'],
    #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
  )


@stripePay.route('/stripe_pay_onetime')
@login_required
def stripe_pay():
  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      'price': 'price_1NQ4URGx5rHp5dcp9EAHb1bs',
      'quantity': 1,
    }],
    mode='payment',
    success_url=url_for('stripePay.thanks', _external=True) +
    '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('stripePay.stripeHome', _external=True),
    metadata={'user_id': current_user.id})
  return {
    'checkout_session_id': session['id'],
    # 'checkout_public_key': os.environ['STRIPE_TEST_PUBLIC_KEY']
    'checkout_public_key': os.environ['STRIPE_PUBLIC_KEY']
    #app.config['STRIPE_PUBLIC_KEY']
  }


@stripePay.route('/stripe_pay_monthly')
@login_required
def stripe_pay_monthly():
  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      # 'price': 'price_1NQ4V6Gx5rHp5dcpaILuI5Dy',
      'price': 'price_1NPoVnGx5rHp5dcp8DwBPxRL',
      'quantity': 1,
    }],
    mode='subscription',
    subscription_data={
    "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
    "trial_period_days": 30,
  },
    success_url=url_for('stripePay.thanks', _external=True) +
    '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('stripePay.stripeHome', _external=True),
    metadata={'user_id': current_user.id})
  return {
    'checkout_session_id': session['id'],
    # 'checkout_public_key': os.environ['STRIPE_TEST_PUBLIC_KEY']
    'checkout_public_key': os.environ['STRIPE_PUBLIC_KEY']
    #app.config['STRIPE_PUBLIC_KEY']
  }


@stripePay.route('/stripe_pay_yearly')
@login_required
def stripe_pay_yearly():
  session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
      # 'price': 'price_1NRHKaGx5rHp5dcpwwYXv0Uc',
      'price': 'price_1NPoUPGx5rHp5dcpFCz8MnLG',
      'quantity': 1,
    }],
    mode='subscription',
    subscription_data={
    "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
    "trial_period_days": 30,
  },
    success_url=url_for('stripePay.thanks', _external=True) +
    '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url=url_for('stripePay.stripeHome', _external=True),
    metadata={'user_id': current_user.id})
  return {
    'checkout_session_id': session['id'],
    # 'checkout_public_key': os.environ['STRIPE_TEST_PUBLIC_KEY']
    'checkout_public_key': os.environ['STRIPE_PUBLIC_KEY']
    #app.config['STRIPE_PUBLIC_KEY']
  }


@stripePay.route('/thanks')
def thanks():
  return render_template('thanks.html')
  
@stripePay.route('/paymentFailed')
def paymentFailed():
  return render_template('payementFailed.html')


@stripePay.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
  print('WEBHOOK CALLED')

  if request.content_length > 1024 * 1024:
    print('REQUEST TOO BIG')
    abort(400)
  payload = request.get_data()
  sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
  endpoint_secret = os.environ['STRIPE_ENDPOINT_SECRET']
  event = None

  try:
    event = stripe.Webhook.construct_event(payload, sig_header,
                                           endpoint_secret)
    print(event['type'])
    # print(event)
  except ValueError as e:
    # Invalid payload
    print('INVALID PAYLOAD')
    return {}, 400
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    print('INVALID SIGNATURE')
    return {}, 400

  # Handle the checkout.session.completed event
  if event['type'] == 'customer.subscription.deleted':
    session = event['data']['object']
    # print(session)
    
    stripecustomer = Stripecustomer.query.filter_by(stripeCustomerId=session['customer']).first()
    
    if stripecustomer:
      user_id= stripecustomer.user_id
      # print('USER ID')
      # print(user_id)
      Stripecustomer.query.filter_by(user_id=user_id).delete()
      db.session.commit()

  
  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']
    print(session)
    line_items = stripe.checkout.Session.list_line_items(session['id'],
                                                         limit=1)
    print(line_items['data'][0]['description'])
    print(line_items['data'][0])

    #Add stripeCustomer to database
    if (session['metadata']):
      user_id = session['metadata']['user_id']
    else:
      user_id = session['client_reference_id']
    sripecustomer_obj = Stripecustomer(
      user_id=user_id,
      stripeCustomerId=session['customer'],
      stripeSubscriptionId=session['subscription'])

    db.session.add(sripecustomer_obj)

    db.session.commit()
    print("Subscription was successful.")
  return {}


@stripePay.route('/create-customer-portal-session', methods=['POST'])
@login_required
def customer_portal():
  # Authenticate your user.
   customer = Stripecustomer.query.filter_by(user_id=current_user.id).order_by(Stripecustomer.id.desc()).first()
   if customer:
    stripeCustomerID = customer.stripeCustomerId
    session = stripe.billing_portal.Session.create(
    customer=stripeCustomerID,
    return_url=url_for('views.account', _external=True),
  )
    return redirect(session.url)