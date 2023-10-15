from rq import get_current_job
from . import db
from .models import Task
import time

from celery import shared_task
from celery.contrib.abotable import AbortableTask

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from .database import engine, load_queue_from_db, load_all_return_details_from_db, load_tracking_id_to_search, delete_trackingID_from_queue_db, add_tracking_id_to_queue, refresh_all_return_data_in_db, load_current_return_to_display_from_db, add_current_return_to_display_to_db, delete_whole_tracking_id_queue, delete_current_return_to_display_from_db, delete_tracking_id_to_search, add_tracking_id_to_search, check_if_track_in_queue, delete_current_return_to_display_from_db, refresh_addresses_in_db, load_address_from_db, load_users_from_db, load_deleted_users_from_db, delete_user_from_db, delete_deleted_user_from_db, clear_all_users_from_db, clear_all_deleted_users_from_db, add_refresh_token, get_refresh_token, load_restricted, add_request_to_delete_user, load_all_stripe_customers, add_suggestion, delete_refresh_token_and_expiration

from .models import User, Notification
from .amazonAPI import get_all_Returns_data, increaseInventory, checkInventory, checkInventoryIncrease, get_addresses_from_GetOrders

from flask import Blueprint, render_template, request, flash, jsonify, send_file, make_response, current_app
# from flask_login import login_required, current_user
from flask_security import login_required, current_user
from .models import Stripecustomer, Task
import stripe
from . import db
import json
from io import BytesIO
import os
from collections import Counter
import datetime
import re

from .download_pdf_queue import download_queue_data
from .download_pdf_inventoryChange import download_queue_and_inventory_change_data
from .download_inventory_to_change import download_inventory_change

# from . import create_app

# app = create_app()
# app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()



@shared_task(bind=True, base=AbortableTask)
def print_numbers(self, seconds):
    print("Starting num task")
    for num in range(seconds):
        print(num)
        time.sleep(1)
        if(self.is_aborted()):
          print("Aborted")
          return "TASK STOPPED!"
    print("Task to print_numbers completed")
    return "DONE!"


#Celery:


@shared_task(bind=True, base=AbortableTask)
def increase_inventory_task(self):
  Quantity_of_SKUS = checkInventory( current_user.refresh_token)
  result = increaseInventory(Quantity_of_SKUS, current_user.id,  current_user.refresh_token)
  print("RESULT:")
  print(type(result))
  print(result)
  # print(result[1])
  if result[0] == 'SUCCESS' :
      flash('Inventory Feed Submitted Successfully! It may take up to 2 hours to load on AmazonSellerCentral.', category='success')
  elif result[0] == None:
    flash (f'error. The queue was probably empty: {result} ', category='error')
  else:
    flash (f'error: {result} ', category='error')
  # result = checkInventoryIncrease(Quantity_of_SKUS, result[1], current_user.refresh_token)
  # print(result)
  # if result == "Inventory Increased Successfully":
  delete_tracking_id_to_search(current_user.id)
  delete_current_return_to_display_from_db(current_user.id)