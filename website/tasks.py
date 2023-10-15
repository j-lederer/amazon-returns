from rq import get_current_job
from . import db
from .models import Task
import time

# from celery import shared_task
# from celery.contrib.abortable import AbortableTask


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



# @shared_task(bind=True, base=AbortableTask)
# def print_numbers(self, seconds):
#     print("Starting num task")
#     for num in range(seconds):
#         print(num)
#         time.sleep(1)
#         if(self.is_aborted()):
#           print("Aborted")
#           return "TASK STOPPED!"
#     print("Task to print_numbers completed")
#     return "DONE!"


#Celery:


# @shared_task(bind=True, base=AbortableTask)
# def increase_inventory_task(self):
#   Quantity_of_SKUS = checkInventory( current_user.refresh_token)
#   result = increaseInventory(Quantity_of_SKUS, current_user.id,  current_user.refresh_token)
#   print("RESULT:")
#   print(type(result))
#   print(result)
#   # print(result[1])
#   if result[0] == 'SUCCESS' :
#       flash('Inventory Feed Submitted Successfully! It may take up to 2 hours to load on AmazonSellerCentral.', category='success')
#   elif result[0] == None:
#     flash (f'error. The queue was probably empty: {result} ', category='error')
#   else:
#     flash (f'error: {result} ', category='error')
#   # result = checkInventoryIncrease(Quantity_of_SKUS, result[1], current_user.refresh_token)
#   # print(result)
#   # if result == "Inventory Increased Successfully":
#   delete_tracking_id_to_search(current_user.id)
#   delete_current_return_to_display_from_db(current_user.id)