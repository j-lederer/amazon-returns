from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from datetime import timedelta
# from flask_login import LoginManager
from flask_migrate import Migrate
import os
# from sqlalchemy import URL
import sqlalchemy
import stripe
from flask_security import Security, hash_password, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from redis import Redis
import rq
import rq_dashboard

from .utils import make_celery
from celery.schedules import crontab

from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.pool import NullPool
import logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(message)s')

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)

  # @app.before_request
  # def log_session_info():
  #     # Log session ID and user-specific information
  #     session_id = session.get('_id', 'no-session-id')
  #     user_id = session.get('_user_id', 'anonymous')
  #     fresh = session.get('_fresh', 'no-fresh-session')
  #     logging.info(f"Current Session ID: {session_id}, User ID: {user_id}, Fresh: {fresh}")
  #     # logging.info(f"Whole session: {str(session)}")
  #     logging.info(f"Whole session: {dict(session)}")
  
  app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
  app.config['SESSION_COOKIE_NAME'] = os.environ['SESSION_COOKIE_NAME']
  app.config['SESSION_COOKIE_SECURE'] = True
  app.config['SESSION_COOKIE_HTTPONLY'] = True
  app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
  # app.config["WTF_CSRF_ENABLED"] = False
  # app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
  app.config['REMEMBER_COOKIE_HTTPONLYE'] = True
  app.config['REMEMBER_COOKIE_SECURE'] = True
  app.config['SESSION_LIFETIME'] = timedelta(days=14)
  app.config['REMEMBER_SESSION_LIFETIME'] = timedelta(days=365) 
 
  app.config["CELERY"] = {
     "broker_url": os.environ['REDIS_URL'], 
     "result_backend": os.environ['REDIS_URL'], 
     "timezone": 'US/Eastern', 
     "beat_schedule": {
      "every-day-at 12am" : {
          "task": "website.views.every_day",
        # 'schedule':20
          "schedule": crontab(hour=0, minute=0, day_of_week='0-6') #timezone is 4 hours ahead of est. It is UTC. So 4 will be 12am
          #"args": (1, 2) 
      },

      "worker_prefetch_multiplier": 1,
       "worker_max_tasks_per_child": 100,
       "worker_concurrency": 2,
       "broker_connection_retry_on_startup": True,
        #  "worker_cancel_long_running_tasks_on_connection_loss": True,
      "broker_transport_options": {"visibility_timeout": 3600},

  }}
  
  app.config['RQ_DASHBOARD_REDIS_URL'] =os.environ['REDIS_URL']
  app.config.from_object(rq_dashboard.default_settings)
  rq_dashboard.web.setup_rq_connection(app)
  app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
  # url_object = URL.create(
  # #sqlUrl = sqlalchemy.engine.url.URL(
  #   drivername="mysql+pymysql",
  #   username=os.getenv("DB_USER"),
  #   password=os.getenv("DB_PASSWORD"),
  #   host=os.getenv("DB_HOST"),
  #   database=os.getenv("DB_DATABASE"),
  #   query={
  #     "ssl_ca":"/etc/ssl/cert.pem"},
  # )
  app.config['SQLALCHEMY_DATABASE_URI'] =os.environ['RAILWAY_DB_CONNECTION_STRING']
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  # app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
  # app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
  app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True, "pool_use_lifo": True}
  # app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"poolclass": NullPool}
  # app.config['STRIPE_PUBLIC_KEY'] = os.environ['STRIPE_TEST_PUBLIC_KEY']
  app.config['STRIPE_PUBLIC_KEY'] = os.environ['STRIPE_PUBLIC_KEY']
  # app.config['STRIPE_SECRET_KEY'] = os.environ['STRIPE_TEST_SECRET_KEY'] 
  app.config['STRIPE_SECRET_KEY'] = os.environ['STRIPE_SECRET_KEY'] 
  app.redis = Redis.from_url(os.environ['REDIS_URL'])
  app.task_queue = rq.Queue('amazon-returns-task-queue', connection=app.redis)
  #os.environ[
  #   'DB2'] + '?ssl_ca=website/addedExtras/cacert-2023-05-30.pem'
  #/etc/ssl/cert.pem'
  # app.config['SQLALCHEMY_DATABASE_URI'] = url_object
  #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.init_app(app)
  migrate = Migrate(app, db)
  stripe.api_key = app.config['STRIPE_SECRET_KEY']
  from .views import views
  from .auth import auth
  from .stripePay import stripePay
  from .connectAmazon import connectAmazon

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')
  app.register_blueprint(stripePay, url_prefix='/')
  app.register_blueprint( connectAmazon, url_prefix='/')
  
  # celery = make_celery(app)
  # celery.set_default()

    
  from celery import Celery, Task
  def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

    
  app.config.from_prefixed_env()
  celery_init_app(app)

  
  from .models import User, Role

  with app.app_context():
    db.create_all()

  # login_manager = LoginManager()
  # login_manager.login_view = 'auth.login'
  # login_manager.init_app(app)

  # @login_manager.user_loader
  # def load_user(id):
  #   return User.query.get(int(id))

  from flask_mailman import Mail

  app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
  app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
  app.config["MAIL_USE_SSL"] = False
  app.config["MAIL_USE_TLS"] = True
  app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
  app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
  mail = Mail(app)

  
  app.config['USER_DATASTORE'] = SQLAlchemyUserDatastore(db, User, Role)

  #Setup Flask-Security
  app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")
  # Don't worry if email has findable domain
  app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}
  app.config["SECURITY_LOGIN_USER_TEMPLATE"] = "login.html"
  app.config["SECURITY_REGISTER_USER_TEMPLATE"] = "signup.html"
  app.config["SECURITY_REGISTERABLE"] = True
  app.config["SECURITY_POST_REGISTER_VIEW"] = "views.home"
  app.config["SECURITY_POST_LOGIN_VIEW"] = "views.home"

  # user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
  user_datastore = SQLAlchemyUserDatastore(db, User, Role)
  app.security = Security(app, user_datastore)


  # return app, celery
  return app
