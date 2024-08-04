from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from .database import engine, load_queue_from_db, load_all_return_details_from_db, load_tracking_id_to_search, delete_trackingID_from_queue_db, add_tracking_id_to_queue, refresh_all_return_data_in_db, load_current_return_to_display_from_db, add_current_return_to_display_to_db, delete_whole_tracking_id_queue, delete_current_return_to_display_from_db, delete_tracking_id_to_search, add_tracking_id_to_search, check_if_track_in_queue, delete_current_return_to_display_from_db, refresh_addresses_in_db, load_address_from_db, load_users_from_db, load_deleted_users_from_db, delete_user_from_db, delete_deleted_user_from_db, clear_all_users_from_db, clear_all_deleted_users_from_db, add_refresh_token, get_refresh_token, load_restricted, add_request_to_delete_user, load_all_stripe_customers, add_suggestion, delete_refresh_token_and_expiration, load_jobs_from_db, load_history_from_db_descending_order, add_queue_to_task_details, load_my_task_trackers_from_db, delete_job_db, get_info_job_from_db, load_task_details_from_db, move_my_task_tracker_to_history, delete_from_history_db, load_saved_for_later_from_db, move_my_task_trackers_to_history, move_history_to_jobs, delete_whole_history_db, load_my_task_tracker_from_db, refresh_return_data_in_db, refresh_inventory_data_in_db

from .models import User, Notification, Stripecustomer, Task, My_task_tracker, My_refresh_returns_tracker
from website.amazonAPI import get_all_Returns_data, increaseInventory_single_job, checkInventory, checkInventoryIncrease, get_addresses_from_GetOrders, increaseInventory_all_jobs

from flask import Blueprint, render_template, request, flash, jsonify, send_file, make_response, current_app
# from flask_login import login_required, current_user
from flask_security import auth_required, current_user, login_required
import stripe
from . import db
import json
from io import BytesIO
import os
from collections import Counter
from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo
import pytz
import re

from .download_pdf_queue import download_queue_data
from .download_pdf_inventoryChange import download_queue_and_inventory_change_data
from .download_inventory_to_change import download_inventory_change

# from .tasks import print_numbers, increase_inventory_task

from celery import shared_task
from celery.contrib.abortable import AbortableTask
from celery.result import AsyncResult

from sqlalchemy.exc import PendingRollbackError, OperationalError
import logging




@shared_task(bind=True, base=AbortableTask, max_retries=3)
def increase_inventory_single_task(self, my_task_tracker_id, refresh_token,
                            current_user_id):
    #Check if there are tasks with the same id and let the user know the pevious satuses of all of them
    skip = False
    try:
      task = Task.query.filter_by(id=self.request.id,
                                  user_id=current_user_id).all()
      # print("CHECK OUT THESE TASKSKSKSKSKSKKSKSKSKSK: (should be empty)")
      # print(task)
      if len(task) > 1:
        print("BIIIIIIIIGGGGGG ERROR. MULTIPLE TASKS WITH SAME ID")
        return -1
      elif task:
        task = task[0]
      elif not task:
        task = Task(id=self.request.id,
                    name=f'Increase Inventory {self.request.id}',
                    description='Increasing Inventory...',
                    time_created=datetime.now(pytz.timezone('America/New_York')),
                    user_id=current_user_id,
                    my_task_tracker=my_task_tracker_id)
        db.session.add(task)
        db.session.commit()
      print(f'Added Task to database with task id: {self.request.id}')
      try:
            my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
            if my_task_tracker.status == 'SUCCESS':
              skip = True
            if my_task_tracker.status=='SENT REQUEST: PARTIAL' and skip==False:
              my_task_tracker.status = 'REDOING PARTIAL'

              my_task_tracker.time_task_associated_launched = datetime.now(pytz.timezone('America/New_York'))

            elif skip==False:
              my_task_tracker.status='Began'
              my_task_tracker.time_task_associated_launched = datetime.now(pytz.timezone('America/New_York'))
            db.session.commit()
      except:
          formatted_string = f'Error updating status of my_task_tracker_id: {my_task_tracker_id} in increaseInventory_all_jobs call to: Began or Redoing Partial.'
          print(formatted_string)
      if skip==False:
        print('Running checkInventory')
        Quantity_of_SKUS = checkInventory(refresh_token)
        if Quantity_of_SKUS == 'FATAL' or Quantity_of_SKUS == 'CANCELLED' or Quantity_of_SKUS == 'UNKNOWN ERROR':
          print("ERROR with checkInventory")
          if my_task_tracker.status=='PARTIAL':
            my_task_tracker.status='Error with checkInventory when redoing partial'
          else:
            my_task_tracker.status='Error with checkInventory'
          db.session.commit()

        else:
          print("Running increase_inventory_single_job ")
          result = increaseInventory_single_job(Quantity_of_SKUS, task.id, my_task_tracker_id,
                                     current_user_id, refresh_token)
          print("RESULT of increaseInventory():")
          print(type(result))
          print(result)
          # print(result[1])
          if result[0] == 'SUCCESS':
            move_my_task_tracker_to_history(my_task_tracker_id, task.id,
                                            current_user_id)
            print('Done with trying to move my task tracker to history')
            # flash('Inventory Feed Submitted Successfully! It may take up to 2 hours to load on AmazonSellerCentral.', category='success')
          elif result[0] == None:
            # flash (f'error. The queue was probably empty: {result} ', category='error')
            print(f'error. The queue was probably empty: {result} ')
          else:
            # flash (f'error: {result} ', category='error')
            print(f'error: {result} ')
          # result = checkInventoryIncrease(Quantity_of_SKUS, result[1], current_user.refresh_token)
          # print(result)
          # if result == "Inventory Increased Successfully":

    except Exception as e:
      # Handle exceptions, log them, and roll back the transaction
      db.session.rollback()
      try:
        my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
        if my_task_tracker.status == 'SUCCESS':
          skip = True
        if my_task_tracker.status=='SENT REQUEST: PARTIAL' and skip==False:
          my_task_tracker.status = 'REDOING PARTIAL'
          my_task_tracker.complete=-1
          db.session.commit()
      except:
        db.session.rollback()

      self.retry(exc=e, countdown=5) 
      #for automatic retries. Also have to add the arguments above