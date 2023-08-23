from sqlalchemy import create_engine, text
import os
from .models import User, Addresses, All_return_details, Current_return_to_display, Tracking_id_to_search, Tracking_ids, Deleted_users, Stripecustomer, Suggestions
from . import db
from flask_sqlalchemy import SQLAlchemy
import datetime
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()
# Base.query = db_session.query_property()

db_connection_string = os.environ['RAILWAY_DB_CONNECTION_STRING']

engine = create_engine(db_connection_string)
                       # ,connect_args={"ssl": {
                       #   "ssl_ca": "/etc/ssl/cert.pem"
                       # }})


def load_queue_from_db(user_id):
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from tracking_ids"))
  #   queue = []

  #   for row in result.all():
  #     queue.append(dict(row._asdict()))  #dict(row) It is a LegacyRow
  #   #print(queue)
  #   return queue
  queue = Tracking_ids.query.filter_by(user_id=user_id).all()
  return [item.__dict__ for item in queue]

def check_if_track_in_queue(trackingID, user_id):
  queue = load_queue_from_db(user_id)
  for track in queue:
    if track['tracking'] == trackingID:
      return True
  return False


def delete_trackingID_from_queue_db(trackingID, user_id):
  # with engine.connect() as conn:
  #   query = text(
  #     "DELETE FROM tracking_ids WHERE tracking_ids.tracking = :tracking_id")

  #   #conn.execute(query, tracking_id=trackingID)
  #   conn.execute(query, {"tracking_id": trackingID})
  item = Tracking_ids.query.filter_by(tracking=trackingID, user_id=user_id).first()
  if item:
      db.session.delete(item)
      db.session.commit()


def delete_whole_tracking_id_queue(user_id):
  # with engine.connect() as conn:
  #   conn.execute(text("DELETE FROM tracking_ids"))
  Tracking_ids.query.filter_by(user_id=user_id).delete()
  db.session.commit()


def add_tracking_id_to_queue(trackingID, sku, quantity_of_return, user_id):
  # with engine.connect() as conn:
  #   query = text("INSERT INTO tracking_ids (tracking, SKU, return_quantity) VALUES (:tracking_id, :SKU, :return_quantity)")
  #   #conn.execute(query, tracking_id=trackingID)
  #   conn.execute(query, {"tracking_id": trackingID, "SKU":sku, "return_quantity":quantity_of_return})

  # Create an instance of the model
  tracking_id_obj = Tracking_ids(tracking=trackingID,
                                 SKU=sku,
                                 return_quantity=quantity_of_return, user_id = user_id)
  # Add the object to the session
  db.session.add(tracking_id_obj)
  # Commit the changes to the database
  db.session.commit()


def load_all_return_details_from_db(user_id):
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from all_return_details"))
  #   return_details = []
  #   column_names = result.keys()

  #   for row in result:
  #     row_dict = dict(zip(column_names, row))
  #     return_details.append(row_dict)
  #   #print(return_details)
  #   return return_details
  return_details = All_return_details.query.filter_by(user_id=user_id).all()
  column_names = All_return_details.__table__.columns.keys()
  return [dict(zip(column_names, row.__dict__)) for row in return_details]


def delete_current_return_to_display_from_db(user_id):
  # with engine.connect() as conn:
  #   conn.execute(text("DELETE FROM current_return_to_display"))
  Current_return_to_display.query.filter_by(user_id=user_id).delete()
  db.session.commit()


def add_current_return_to_display_to_db(trackingID, user_id):
  delete_current_return_to_display_from_db(user_id)
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from all_return_details"))
  #   returnDatas = []
  #   column_names = result.keys()
  #   for row in result:
  #     row_dict = dict(zip(column_names, row))
  #     if row_dict['tracking_id'] == trackingID:
  #       returnDatas.append(row_dict)
  #       for returnData in returnDatas:

  #         query = text(
  #           "INSERT INTO current_return_to_display (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned, Inventory, user_id) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned, :Inventory, :user_id)"
  #         )
  #         conn.execute(
  #           query, {
  #             "tracking_id": returnData['tracking_id'],
  #             "item_name": returnData['item_name'],
  #             "sku": returnData['sku'],
  #             "return_quantity": returnData['return_quantity'],
  #             "refund_amount": returnData['refund_amount'],
  #             "order_id": returnData['order_id'],
  #             "order_quantity": returnData['order_quantity'],
  #             "asin": returnData['asin'],
  #             "reason_returned": returnData['reason_returned'],
  #             "Inventory": returnData['Inventory'], "user_id":user_id
  #           })
  #   if (load_current_return_to_display_from_db(user_id) == None):
  #     query = text(
  #       "INSERT INTO current_return_to_display (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned, user_id) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned, :user_id)"
  #     )
  #     conn.execute(
  #       query, {
  #         "tracking_id": "Not Found",
  #         "item_name": "Not Found",
  #         "sku": "Not Found",
  #         "return_quantity": "Not Found",
  #         "refund_amount": "Not Found",
  #         "order_id": "Not Found",
  #         "order_quantity": "Not Found",
  #         "asin": "Not Found",
  #         "reason_returned": "Not Found", "user_id":user_id
  #       })
  return_data = All_return_details.query.filter_by(tracking_id=trackingID, user_id=user_id).first()
  if return_data:
        return_data_dict = return_data.__dict__
        return_data_dict.pop('_sa_instance_state', None)
        return_data_dict.pop('id', None)
        return_data_dict['user_id'] = user_id
        current_return = Current_return_to_display(**return_data_dict)
        db.session.add(current_return)
        db.session.commit()
  else:
        current_return = Current_return_to_display(
            tracking_id="Not Found",
            item_name="Not Found",
            sku="Not Found",
            return_quantity="Not Found",
            refund_amount="Not Found",
            order_id="Not Found",
            order_quantity="Not Found",
            asin="Not Found",
            reason_returned="Not Found",
            user_id=user_id
        )
        db.session.add(current_return)
        db.session.commit()


def load_current_return_to_display_from_db(user_id):
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from current_return_to_display"))

  #   column_names = result.keys()

  #   for row in result:
  #     row_dict = dict(zip(column_names, row))
  #     return row_dict
  result = Current_return_to_display.query.filter_by(user_id=user_id).first()
  if result is not None:
        return dict(result.__dict__)
  else:
        return None


def delete_tracking_id_to_search(user_id):
  Tracking_id_to_search.query.filter_by(user_id=user_id).delete()
  db.session.commit()
  #  with engine.connect() as conn:
  #    conn.execute("DELETE FROM tracking_id_to_search")

 


def add_tracking_id_to_search(trackingID, user_id):
  delete_tracking_id_to_search(user_id)
  # with engine.connect() as conn:
  #   query = text(
  #     "INSERT INTO tracking_id_to_search (tracking_id, user_id) VALUES (:tracking_id, :user_id)")
  #   conn.execute(query, {"tracking_id": trackingID, "user_id":user_id})
  tracking_id_obj = Tracking_id_to_search(tracking_id=trackingID, user_id = user_id)
  db.session.add(tracking_id_obj)
  db.session.commit()


def load_tracking_id_to_search(user_id):
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from tracking_id_to_search"))
  #   for row in result.all():
  #     trackingID = row._asdict()
  #     return trackingID['tracking_id']
  tracking_id = Tracking_id_to_search.query.filter_by(user_id=user_id).first()
  if tracking_id:
        return tracking_id.tracking_id
  return None


def refresh_all_return_data_in_db(all_return_data, inventory_data, user_id):
  # with engine.connect() as conn:
  #   #Delete all previous return data
  #   conn.execute(text("DELETE FROM all_return_details"))

  #   #Add all the new return data
  #   for return_details in all_return_data:
  #     print(return_details)
  #     query = text(
  #       "INSERT INTO all_return_details (tracking_id, item_name, sku, return_quantity, refund_amount, order_id, order_quantity, asin, reason_returned, Inventory, user_id) VALUES (:tracking_id, :item_name, :sku, :return_quantity, :refund_amount, :order_id, :order_quantity, :asin, :reason_returned, :Inventory, :user_id)"
  #     )
  #     conn.execute(
  #       query, {
  #         "tracking_id": return_details['tracking_id'],
  #         "item_name": return_details['item_name'],
  #         "sku": return_details['sku'],
  #         "return_quantity": return_details['return_quantity'],
  #         "refund_amount": return_details['refund_amount'],
  #         "order_id": return_details['order_id'],
  #         "order_quantity": return_details['order_quantity'],
  #         "asin": return_details['asin'],
  #         "reason_returned": return_details['reason_returned'],
  #         "Inventory": inventory_data[return_details['sku']], "user_id":user_id
  #       })
  All_return_details.query.filter_by(user_id=user_id).delete()
  db.session.commit()
  
  if (all_return_data != 'CANCELLED'):
    for return_details in all_return_data:
        if(return_details):
          if return_details['sku']:
            return_details['Inventory'] =[]
            return_details_sku_list = return_details['sku'].split(', ')
            for item_sku in return_details_sku_list:
              if item_sku in inventory_data.keys():
                return_details['Inventory'].append( inventory_data[item_sku])
              else:
                print("Could not find inventory_data[return_details['sku']]")
          else:
            print("Could not find return_details['sku']")
          return_details['user_id'] = user_id
          return_details['Inventory'] = ', '.join(return_details['Inventory'])
          return_data_obj = All_return_details(**return_details)
          db.session.add(return_data_obj)
  else: 
     print("An error occcurred while retreiveing info. The process was CANCELLED")
     return "An error occcurred while retreiveing info. The process was CANCELLED"
  db.session.commit()


def refresh_addresses_in_db(address_data, user_id):
  delete_addresses_from_db(user_id)
  # with engine.connect() as conn:
  #   for orderID in address_data:
  #     order_id = orderID
  #     address = address_data[orderID]
  #     if address == None:
  #       address_String = None
  #     else:
  #       address_String = address["City"] + " " + address[
  #         'StateOrRegion'] + ", " + address['CountryCode'] + " " + address[
  #           'PostalCode']
  #     query = text(
  #       "INSERT INTO addresses (orderID, Address, user_id) VALUES (:orderID, :Address, user_id)")
  #     conn.execute(query, {"orderID": order_id, "Address": address_String, "user_id":user_id})

  for orderID, address in address_data.items():
      if address is None:
          address_String = None
      else:
          address_String = address["City"] + " " + address['StateOrRegion'] + ", " + address['CountryCode'] + " " + address['PostalCode']
        
      address_obj = Addresses(OrderID=orderID, Address=address_String, user_id=user_id)
      db.session.add(address_obj)
  db.session.commit()



def load_address_from_db(user_id):
  # with engine.connect() as conn:
  #   result = conn.execute(text("select * from addresses"))
  #   Addresses = []

  #   for row in result.all():
  #     Addresses.append(dict(row._asdict()))  #dict(row) It is a LegacyRow

  #   return Addresses
  addresses = Addresses.query.filter_by(user_id=user_id).all()
  return [item.__dict__ for item in addresses]


def delete_addresses_from_db(user_id):
  # with engine.connect() as conn:
  #   conn.execute(text("DELETE FROM addresses"))
  Addresses.query.filter_by(user_id=user_id).delete()
  db.session.commit()

def load_users_from_db():
  users = User.query.all()
  print(users)
  return users
def load_deleted_users_from_db():
  deleted_users = Deleted_users.query.all()
  return deleted_users
def delete_user_from_db(userid, currentUser):
    user = User.query.filter(User.id==userid, User.email!='admin@admin675463.com').first()
    if user:
        #add to deleted users
        deleted_user = Deleted_users(id=user.id, email=user.email, password=user.password, first_name=user.first_name, date_joined=user.date_joined)
        db.session.add(deleted_user)
        db.session.delete(user)
        db.session.commit()
def delete_deleted_user_from_db(deleted_userid, currentUser):
  deleted_user = Deleted_users.query.filter_by(id=deleted_userid).first()
  if deleted_user:
    db.session.delete(deleted_user)
    db.session.commit()
  
def clear_all_users_from_db(currentUser):
  #add them to deleted users
  users = User.query.filter(User.email != 'admin@admin675463.com').all()
  for user in users:
    deleted_user = Deleted_users(id=user.id, email=user.email, password=user.password, first_name=user.first_name, date_joined=user.date_joined)
    db.session.add(deleted_user)
  User.query.filter(User.email != 'admin@admin675463.com').delete()
  db.session.commit()
def clear_all_deleted_users_from_db(currentUser):
  Deleted_users.query.delete()
  db.session.commit()


def add_refresh_token(user_id, refreshToken):
  user = User.query.get(user_id)
  if user:
    user.refresh_token = refreshToken
    db.session.commit()
    create_token_expiration(user_id)
  else:
    print("error with database call add_refresh_token")
def get_refresh_token(user_id):
  user = User.query.get(user_id)
  if user:
    refresh_token = user.refresh_token
    return refresh_token
  else:
    print("error with database call get_refresh_token")
def delete_refresh_token_and_expiration(user_id):
  user = User.query.get(user_id)
  user.refresh_token = None
  user.token_expiration = None
  db.session.commit()
  
def load_restricted(user_id):
  user = User.query.filter(User.id==user_id).first()
  if user:
    return user.restricted
  else:
    print("error with database call load_restricted")

def add_request_to_delete_user(user_id):
  user = User.query.filter(User.id==user_id).first()
  if user:
    user.delete_request = 'yes'
    db.session.commit()
  else:
    print("error with database call add_request_to_delete_user")

def load_all_stripe_customers():
  stripe_customers = Stripecustomer.query.all()
  return stripe_customers

def  add_suggestion(suggestion, user):
  print(user)
  if user.is_anonymous:
    suggestion = Suggestions(suggestion=suggestion, userid = 'anonymous')
  else:
    suggestion = Suggestions(suggestion=suggestion, userid = user.id)
  db.session.add(suggestion)
  db.session.commit()

def load_token_expiration(user_id):
  user = User.query.get(user_id)
  if user:
    token_expiration = user.token_expiration
    return token_expiration
  else:
    print("error with database call get_refresh_token")
    return'error'
def create_token_expiration(user_id):
  current_date = datetime.datetime.now()
  end_date = current_date + datetime.timedelta(days=364)
  user = User.query.get(user_id)
  if user:
    user.token_expiration = end_date
    db.session.commit()

  