from sp_api.api import Orders
from sp_api.base import SellingApiException
import os
#from dotenv import load_dotenv
#del os.environ['AWS_ENV']
import time
import xml.etree.ElementTree as ET
import csv
from io import StringIO
from sp_api.api import Feeds
from sp_api.base import SellingApiException


from datetime import datetime, timedelta, date
from sp_api.base import Marketplaces
from sp_api.api import Orders
from sp_api.util import throttle_retry, load_all_pages
import os
import sys

from .database import load_queue_from_db, delete_whole_tracking_id_queue, load_task_details_from_db, move_my_task_tracker_to_history
from .tasks import  _set_task_progress  #,app
from .models import User, Task, My_task_tracker
from . import db

from collections import defaultdict



# credentials = dict(
#     refresh_token=os.environ['REFRESH_TOKEN'],
#     lwa_app_id=os.environ['LWA_APP_ID'],
#     lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
#     aws_access_key=os.environ['AWS_ACCESS_KEY'],
#     aws_secret_key=os.environ['AWS_SECRET_KEY'],  
#     #role_arn="arn:aws:iam::108760843519:role/New_Role"
# )



from sp_api.api import Reports
from sp_api.api import Feeds
from sp_api.base.reportTypes import ReportType





def get_all_Returns_data(refresh_token):
        credentials = dict(
          refresh_token=refresh_token,
          lwa_app_id=os.environ['LWA_CLIENT_ID'],
          lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
          aws_access_key=os.environ['AWS_ACCESS_KEY'],
          aws_secret_key=os.environ['AWS_SECRET_KEY'],  
          #role_arn="arn:aws:iam::108760843519:role/New_Role"
      )
        import xml.etree.ElementTree as ET
        #report_types = ["GET_FLAT_FILE_OPEN_LISTINGS_DATA",]
        res = Reports(credentials=credentials).create_report(
            reportType="GET_XML_RETURNS_DATA_BY_RETURN_DATE",
            dataStartTime=(datetime.utcnow() - timedelta(days=100)).isoformat(),
            #**Looks like get an error (FATAL) if startTime is before account was opened or if bad example. I got error with year 2019 
            #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
            marketplaceIds=[
                "ATVPDKIKX0DER",   #US
                
            ])
        #print(res)
        #print(res.payload)
        res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
        #print(res.payload)
        report_id = res.payload.get("reportId")
        #print(res)
        #print(report_id)
        processing_status = res.payload.get("processingStatus")
        while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
                    # Wait for a short duration before checking again
                    time.sleep(2)
                    
                    # Get the updated report status
                    response = Reports(credentials=credentials).get_report(report_id)
                    processing_status = response.payload.get("processingStatus")
                    print(processing_status)
        if processing_status == "DONE":
                    # Once the processing is done, retrieve the report document
                    document_id = response.payload.get("reportDocumentId")
                    #print(response)
                    #print(document_id)
                    response = Reports(credentials=credentials).get_report_document(document_id, download=True)
                    # print('PRINTING')
                    # print(response.payload.get("document"))
                    
                    myroot =ET.fromstring(response.payload.get("document")) #If response is a string
                    # print('PRINTING TAG')
                    # print(myroot.tag)
                    Returns_info = []
                    for x in myroot.iter("return_details"): #can also use myroot.findall("")
                        new_return={}
                        for y in x.iter("label_details"):
                            for z in y.iter("tracking_id"):
                                  print(z.text)
                                #if z.text = trackingID_Scanned then get the 
                                # 1. Reason for return
                                # 2. Quantity returned
                                # 3. SKU and increase inventory
                                #Ex tracking id: "1Z0V2Y989048009061
                                  tracking_id = z.text
                                  reason_returned = []
                                  item_name = []
                                  sku = []
                                  return_quantity = []
                                  refund_amount = []
                                  asin = []
                                  
                                  print("Details for return order:")
                                  for a in x.iter("item_details"):
                                    # print(a.find("return_reason_code").text)
                                    
                                    reason_returned.append( a.find("return_reason_code").text)
                                    # print(a.find("item_name").text)
                                    item_name.append( a.find("item_name").text)
                                    # print(a.find("merchant_sku").text)
                                    sku.append( a.find("merchant_sku").text)
                                    # print(a.find("return_quantity").text)
                                    return_quantity.append( a.find("return_quantity").text)
                                    # print(a.find("refund_amount").text)
                                    refund_amount.append( a.find("refund_amount").text)
                                    # print(x.find("order_id").text)
                                    order_id = x.find("order_id").text
                                    # print(x.find("order_date").text)
                                    # print(x.find("a_to_z_claim").text)
                                    # print(x.find("order_quantity").text)
                                    order_quantity = x.find("order_quantity").text
                                    asin.append(a.find("asin").text)

                                  #convert lists to strings so can store in database  
                                  reason_returned = ', '.join(reason_returned)
                                  item_name = ', '.join(item_name)
                                  sku = ', '.join(sku)
                                  return_quantity = ', '.join(return_quantity)
                                  refund_amount = ', '.join(refund_amount)
                                  asin = ', '.join(asin) 
                                  new_return.update({
                                    'tracking_id': tracking_id,
                                    'item_name': item_name,
                                    'sku': sku,
                                    'return_quantity': return_quantity,
                                    'refund_amount': refund_amount,
                                    'order_id': order_id,
                                    'order_quantity': order_quantity,
                                    'asin': asin,
                                    'reason_returned': reason_returned,
                                    'Inventory': "No Data"
                                  })
                                  

                                  Returns_info.append(new_return)
                                  
          
                    # print(Returns_info)
                    output_data = Returns_info                
                        
        elif processing_status == "CANCELLED":
            print("Report processing was cancelled.")
            output_data= "CANCELLED"
        elif processing_status == "FATAL":
            print("An error occurred during report processing. (FATAL)")  
            output_data= "FATAL"
        
        return output_data



def checkInventory(refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)

#To get Report of Inventories
  print("Inventory Report:")
  Quantity_of_SKUS = {}
  res = Reports(credentials=credentials).create_report(

    reportType="GET_FLAT_FILE_OPEN_LISTINGS_DATA",
  #dataStartTime=(datetime.utcnow() - timedelta(days=7)).isoformat(),
  #dataEndTime=(datetime.utcnow() - timedelta(days=1)).isoformat(), 
  #marketplaceIds=["ATVPDKIKX0DER",   #US]
  )
  res = Reports(credentials=credentials).get_report(res.payload.get("reportId"))
  report_id = res.payload.get("reportId")
  processing_status = res.payload.get("processingStatus")
  
  while processing_status not in ["DONE", "CANCELLED", "FATAL"]:
    # Wait for a short duration before checking again
    time.sleep(5)  
    
    #Get the updated report status
    response = Reports(credentials=credentials).get_report(report_id)
    processing_status = response.payload.get("processingStatus")
    print(processing_status)
    if processing_status == "DONE":
      # Once the processing is done, retrieve the report document
      document_id = response.payload.get("reportDocumentId")
      response = Reports(credentials=credentials).get_report_document(document_id, download=True)
    # print(response.payload.get("document"))
      s = response.payload.get("document")
      buff = StringIO(s)
      inventory_reader = csv.DictReader(buff, delimiter='\t' )
      #csv.reader                                    #next(inventory_reader) #skips the header
      for line in inventory_reader:
        #print("test")
        print(line['sku'], line['asin'], line['price'], line['quantity'])
        Quantity_of_SKUS[line['sku']]=line['quantity']
      print("Quantity left of skus is:")
      print(Quantity_of_SKUS)    
      return Quantity_of_SKUS
    
  Quantity_of_SKUS = processing_status
  return Quantity_of_SKUS
        

def increaseInventory(Quantity_of_SKUS, task_id, my_task_tracker_id, user_id, refresh_token):
  #set task status
  try:
    task = Task.query.get(task_id)
    my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
    task.status = 'Began'
    my_task_tracker.status='Began'
    my_task_tracker.time_task_associated_launched = datetime.now()
    db.session.commit()
  except:
    formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Began'
    print(formatted_string)
    #end of status update
    
  result ={}
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  #submitting feed to increase inventory   
  from io import BytesIO
  from sp_api.api import Feeds
  #from sp_api.auth import VendorCredentials
  import xml.etree.ElementTree as ET
  
  try:
    user = User.query.get(user_id)
    #set task status
    _set_task_progress(0)
    data = []
    task_progress_i = 0
    #end of statuts update
    
    queue = load_task_details_from_db(my_task_tracker_id, user_id)
    queue_to_increase= {}
    for track in queue:
        track_sku_list = track['SKU'].split(', ')
        track_return_quantity_list = track['return_quantity'].split(', ') 
        i = 0
        for individual_sku in track_sku_list:  
          is_duplicate = False
          for sku in queue_to_increase.keys():
            if sku == individual_sku:
              is_duplicate = True
          if is_duplicate:
            queue_to_increase[individual_sku] = int(queue_to_increase[individual_sku]) + int(track_return_quantity_list[i])
            i+=1
          else:
            queue_to_increase[individual_sku]= int(track_return_quantity_list[i])
            i+=1
    print (queue_to_increase)
          #return queue_to_increase
    result[0] = None

    #set task status
    try:
      task.status = 'Creating Feed'
      my_task_tracker.status='Creating Feed'
      db.session.commit()
    except:
      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Creating Feed'
      print(formatted_string)
    #end of statuts update
    
    for sku in queue_to_increase.keys():
      # Initialize the Feeds API client
      feeds = Feeds(credentials=credentials)
      # Define the inventory update feed message
      message = {
              "MessageType": "Inventory",
              "MessageID": "1",
              "Inventory": {
                  "SKU": sku,
                  "Quantity": (int(Quantity_of_SKUS[sku])+int(queue_to_increase[sku])),
                  "FulfillmentCenterID": "DEFAULT"
              },
              "Override": "false"
          }
  
      # Create the XML structure
      root = ET.Element("AmazonEnvelope")
      root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
      root.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
      header = ET.SubElement(root, "Header")
      document_version = ET.SubElement(header, "DocumentVersion")
      document_version.text = "1.02"
      merchant_identifier = ET.SubElement(header, "MerchantIdentifier")
      merchant_identifier.text = "A2RSMNCJSAU6P5"  #Have to update this to make it generic
  
      message_type = ET.SubElement(root, "MessageType")
      message_type.text = message["MessageType"]
  
      message_element = ET.SubElement(root, "Message")
      message_id = ET.SubElement(message_element, "MessageID")
      message_id.text = message["MessageID"]
  
      inventory = ET.SubElement(message_element, "Inventory")
      inventory_data = message["Inventory"]
      seller_sku = ET.SubElement(inventory, "SKU")
      seller_sku.text = inventory_data["SKU"]
      fulfillment_center_id = ET.SubElement(inventory, "FulfillmentCenterID")
      fulfillment_center_id.text = inventory_data["FulfillmentCenterID"]
  
      # Choice between Available, Quantity, or Lookup
      quantity = ET.SubElement(inventory, "Quantity")
      quantity.text = str(inventory_data["Quantity"])
  
      restock_date = ET.SubElement(inventory, "RestockDate")
      restock_date.text = "2023-05-26"  # Replace with a valid date
      fulfillment_latency = ET.SubElement(inventory, "FulfillmentLatency")
      fulfillment_latency.text = "1"  # Replace with a valid integer
      switch_fulfillment_to = ET.SubElement(inventory, "SwitchFulfillmentTo")   #I think can leave this and following line out
      switch_fulfillment_to.text = "MFN"  # Replace with either "MFN" or "AFN  
  
      # Convert the XML structure to a string
      xml_string = ET.tostring(root, encoding="utf-8", method="xml")
      #debug
      print(xml_string.decode("utf-8"))

      
      # Submit the feed
      feeds = Feeds(credentials=credentials)
      feed = BytesIO(xml_string)
      feed.seek(0)

      task_progress_i = 50
      
      # Submit the feed
      try:
        document_response, create_feed_response= feeds.submit_feed('POST_INVENTORY_AVAILABILITY_DATA', feed, 'text/xml')
        #print("RETURNED DOCUMENT RESOPONSE")
        #print(document_response)
        #print ("RETURNED CREATE FEED RESPONSE")
        #print(create_feed_response)
        response = create_feed_response
        print("Feed submitted...")

        #set task status
        try:
          task.status = 'Submitted Feed'
          my_task_tracker.status='Submitted Feed'
          db.session.commit()
        except:
          formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Submitted Feed'
          print(formatted_string)
        #end of statuts update
  
        #Check the processing status
        #print(response)
        feed_id = response.payload.get('feedId')   
        #print (feed_id)
          
        print("Inventory Feed Processing Status")
        while True:
            feed_response = feeds.get_feed(feed_id)
            #print(feed_response)
            processing_status = feed_response.payload.get('processingStatus')
            print(processing_status) 
            if processing_status in ["DONE", "IN_QUEUE", "IN_PROGRESS"]:
                #print(f"Processing status: {processing_status}")
                if processing_status in ["DONE", "DONE_NO_DATA"]:
                    print(feed_response)
                    print("Feed processing completed.")
                    
                    document_id = feed_response.payload.get("resultFeedDocumentId")
                    feed_response = Feeds(credentials=credentials).get_feed_document(document_id) #download=true
                    print(feed_response)
                    # return 'SUCCESS'
                    # delete_whole_tracking_id_queue(user_id)
                    result[0] = "SUCCESS"
                    result [1] = queue_to_increase        
                    #set task status
                    task_progress_i = 100
                    try:
                      task.status = 'SUCCESS'
                      task.complete = True
                      task.time_completed = datetime.now()
                      my_task_tracker.status='SUCCESS'
                      my_task_tracker.complete = True
                      my_task_tracker.time_completed = datetime.now()
                      db.session.commit()
                    except:
                      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: SUCCESS'
                      print(formatted_string)
                    #end of statuts update     
                    
                  
                    break
            else:
                print("Feed processing encountered a fatal error.")
                #set task status
                try:
                  task.status = 'Error. Feed Rejected. Try again.'
                  my_task_tracker.status='Error. Feed Rejected. Try again.'
                  db.session.commit()
                except:
                  formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Error. Feed Rejected. Try again.' 
                  print(formatted_string)
                  #End of status update
                result[0] = 'ERROR'
                break
            time.sleep(5)
  
      except Exception as e:
          print(f"Error submitting feed: {e}") 
          result[0] = e
          #set task status
          try:
            task.status = 'Error Submitting Feed. Try Again'
            my_task_tracker.status='Error Submitting Feed. Try Again'
            db.session.commit()
          except:
            formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Error Submitting Feed. Try Again.'
            print(formatted_string)
          #end of statuts update
        
    return result
  except:
    # app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    #set task status
    try:
      task.status = 'Unknown Error Code 1'
      my_task_tracker.status='Unknown Error Code 1'
      db.session.commit()
    except:
      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_id: {my_task_tracker_id} in increaseInventory call to: Unknown Error Code 1'
      print(formatted_string)
    #end of statuts update
  finally:
    _set_task_progress(100)

def increaseInventory_all_jobs(Quantity_of_SKUS, task_id, my_task_trackers_ids_array, user_id, refresh_token):
  #set task status
  print("I am in increaseInventory_all_jobs()  AMAZONAPI     !!!!!!!")
  try:
    task = Task.query.get(task_id)
    task.status = 'Began'
    for my_task_tracker_id in my_task_trackers_ids_array:
      my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
      my_task_tracker.status='Began'
      my_task_tracker.time_task_associated_launched = datetime.now()
    db.session.commit()
  except:
    formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Began'
    print(formatted_string)
    #end of status update
  print('CHECKPOINT 1')
  result ={}
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  #submitting feed to increase inventory   
  from io import BytesIO
  from sp_api.api import Feeds
  #from sp_api.auth import VendorCredentials
  import xml.etree.ElementTree as ET
  print('CHECKPOINT 2')
  try:
    user = User.query.get(user_id)
    #set task status
    _set_task_progress(0)
    data = []
    task_progress_i = 0
    #end of statuts update
    print('CHECKPOINT 3')
    queue = []
    print('CHECKPOINT 4')
    for my_task_tracker_id in my_task_trackers_ids_array:
        task_details_list = load_task_details_from_db(my_task_tracker_id, user_id)
        queue.extend(task_details_list)
    print('CHECKPOINT 5')
    queue_to_increase= {}
    print('QUEUE: ', queue)
    for track in queue:
        print('TRACK: ', track['tracking'])
        track_sku_list = track['SKU'].split(', ')
        print('TRACK_SKU_LIST: ', track_sku_list)
        print('CHECKPOINT 5aa')
        track_return_quantity_list = track['return_quantity'].split(', ')
        print('CHECKPOINT 5bb')
        i = 0
        print('CHECKPOINT 5a')
        for individual_sku in track_sku_list:  
          is_duplicate = False
          print('CHECKPOINT 5b')
          for sku in queue_to_increase.keys():
            print('CHECKPOINT 5c')
            if sku == individual_sku:
              print('CHECKPOINT 5d')
              is_duplicate = True
          print('CHECKPOINT 5e')
          if is_duplicate:
            print('CHECKPOINT 5f')
            queue_to_increase[individual_sku] = int(queue_to_increase[individual_sku]) + int(track_return_quantity_list[i])
            i+=1
          else:
            queue_to_increase[individual_sku]= int(track_return_quantity_list[i])
            i+=1
    print (queue_to_increase)
          #return queue_to_increase
    result[0] = None
    print('CHECKPOINT 6')
    #set task status
    try:
      task.status = 'Creating Feed'
      for my_task_tracker_id in my_task_trackers_ids_array:
        my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
        my_task_tracker.status='Creating Feed'
      db.session.commit()
    except:
      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Creating Feed'
      print(formatted_string)
    #end of statuts update
    print('CHECKPOINT 7')
    for sku in queue_to_increase.keys():
      # Initialize the Feeds API client
      feeds = Feeds(credentials=credentials)
      # Define the inventory update feed message
      message = {
              "MessageType": "Inventory",
              "MessageID": "1",
              "Inventory": {
                  "SKU": sku,
                  "Quantity": (int(Quantity_of_SKUS[sku])+int(queue_to_increase[sku])),
                  "FulfillmentCenterID": "DEFAULT"
              },
              "Override": "false"
          }

      # Create the XML structure
      root = ET.Element("AmazonEnvelope")
      root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
      root.set("xsi:noNamespaceSchemaLocation", "amzn-envelope.xsd")
      header = ET.SubElement(root, "Header")
      document_version = ET.SubElement(header, "DocumentVersion")
      document_version.text = "1.02"
      merchant_identifier = ET.SubElement(header, "MerchantIdentifier")
      merchant_identifier.text = "A2RSMNCJSAU6P5"  #Have to update this to make it generic

      message_type = ET.SubElement(root, "MessageType")
      message_type.text = message["MessageType"]

      message_element = ET.SubElement(root, "Message")
      message_id = ET.SubElement(message_element, "MessageID")
      message_id.text = message["MessageID"]

      inventory = ET.SubElement(message_element, "Inventory")
      inventory_data = message["Inventory"]
      seller_sku = ET.SubElement(inventory, "SKU")
      seller_sku.text = inventory_data["SKU"]
      fulfillment_center_id = ET.SubElement(inventory, "FulfillmentCenterID")
      fulfillment_center_id.text = inventory_data["FulfillmentCenterID"]

      # Choice between Available, Quantity, or Lookup
      quantity = ET.SubElement(inventory, "Quantity")
      quantity.text = str(inventory_data["Quantity"])

      restock_date = ET.SubElement(inventory, "RestockDate")
      restock_date.text = "2023-05-26"  # Replace with a valid date
      fulfillment_latency = ET.SubElement(inventory, "FulfillmentLatency")
      fulfillment_latency.text = "1"  # Replace with a valid integer
      switch_fulfillment_to = ET.SubElement(inventory, "SwitchFulfillmentTo")   #I think can leave this and following line out
      switch_fulfillment_to.text = "MFN"  # Replace with either "MFN" or "AFN  

      # Convert the XML structure to a string
      xml_string = ET.tostring(root, encoding="utf-8", method="xml")
      #debug
      print(xml_string.decode("utf-8"))


      # Submit the feed
      feeds = Feeds(credentials=credentials)
      feed = BytesIO(xml_string)
      feed.seek(0)

      task_progress_i = 50

      # Submit the feed
      try:
        document_response, create_feed_response= feeds.submit_feed('POST_INVENTORY_AVAILABILITY_DATA', feed, 'text/xml')
        #print("RETURNED DOCUMENT RESOPONSE")
        #print(document_response)
        #print ("RETURNED CREATE FEED RESPONSE")
        #print(create_feed_response)
        response = create_feed_response
        print("Feed submitted...")

        #set task status
        try:
          task.status = 'Submitted Feed'
          for my_task_tracker_id in my_task_trackers_ids_array:
            my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
            my_task_tracker.status='Submitted Feed'
          db.session.commit()
        except:
          formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Submitted Feed'
          print(formatted_string)
        #end of statuts update

        #Check the processing status
        #print(response)
        feed_id = response.payload.get('feedId')   
        #print (feed_id)

        print("Inventory Feed Processing Status")
        while True:
            feed_response = feeds.get_feed(feed_id)
            #print(feed_response)
            processing_status = feed_response.payload.get('processingStatus')
            print(processing_status) 
            if processing_status in ["DONE", "IN_QUEUE", "IN_PROGRESS"]:
                #print(f"Processing status: {processing_status}")
                if processing_status in ["DONE", "DONE_NO_DATA"]:
                    print(feed_response)
                    print("Feed processing completed.")

                    document_id = feed_response.payload.get("resultFeedDocumentId")
                    feed_response = Feeds(credentials=credentials).get_feed_document(document_id) #download=true
                    print(feed_response)
                    # return 'SUCCESS'
                    # delete_whole_tracking_id_queue(user_id)
                    result[0] = "SUCCESS"
                    result [1] = queue_to_increase        
                    #set task status
                    task_progress_i = 100
                    try:
                      task.status = 'SUCCESS'
                      task.complete = True
                      task.time_completed = datetime.now()
                      for my_task_tracker_id in my_task_trackers_ids_array:
                        my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
                        my_task_tracker.status='SUCCESS'
                        my_task_tracker.complete = True
                        my_task_tracker.time_completed = datetime.now()
                      db.session.commit()
                    except:
                      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: SUCCESS'
                      print(formatted_string)
                    #end of statuts update     


                    break
            else:
                print("Feed processing encountered a fatal error.")
                #set task status
                try:
                  task.status = 'Error. Feed Rejected. Try again.'
                  for my_task_tracker_id in my_task_trackers_ids_array:
                    my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
                    my_task_tracker.status='Error. Feed Rejected. Try again.'
                  db.session.commit()
                except:
                  formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Error. Feed Rejected. Try again.' 
                  print(formatted_string)
                  #End of status update
                result[0] = 'ERROR'
                break
            time.sleep(5)

      except Exception as e:
          print(f"Error submitting feed: {e}") 
          result[0] = e
          #set task status
          try:
            task.status = 'Error Submitting Feed. Try Again'
            for my_task_tracker_id in my_task_trackers_ids_array:
              my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
              my_task_tracker.status='Error Submitting Feed. Try Again'
            db.session.commit()
          except:
            formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Error Submitting Feed. Try Again.'
            print(formatted_string)
          #end of statuts update

    return result
  except Exception as e:
    print(e)
    # app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    #set task status
    try:
      task.status = 'Unknown Error Code 1'
      for my_task_tracker_id in my_task_trackers_ids_array:
        my_task_tracker = My_task_tracker.query.get(my_task_tracker_id)
        my_task_tracker.status='Unknown Error Code 1'
      db.session.commit()
    except:
      formatted_string = f'Error updating status of taskID: {task_id} and my_task_tracker_ids: {my_task_trackers_ids_array} in increaseInventory_all_jobs call to: Unknown Error Code 1'
      print(formatted_string)
    #end of statuts update
    result[0] = e
  finally:
    _set_task_progress(100)



def produce_pdf_full(user_id, refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  Quantity_of_SKUS = checkInventory(refresh_token)
  
  queue = load_queue_from_db(user_id)
  queue_to_increase= {}
  is_duplicate = False
  for track in queue:
      track_sku_list = track['SKU'].split(', ')
      track_return_quantity_list = track['return_quantity'].split(', ') 
      i = 0
      for individual_sku in track_sku_list:  
        for sku in queue_to_increase.keys():
          if sku == individual_sku:
            is_duplicate = True
        if is_duplicate:
          queue_to_increase[individual_sku] = int(queue_to_increase[individual_sku]) + int(track_return_quantity_list[i])
          i+=1
        else:
          queue_to_increase[individual_sku]= int(track_return_quantity_list[i])
          i+=1

  final_inventory={}
  for sku in queue_to_increase.keys():
    final_inventory[sku] =(int( Quantity_of_SKUS[sku]) + int( queue_to_increase[sku]) )

  return Quantity_of_SKUS, queue_to_increase, final_inventory
    
def produce_pdf_slim(user_id, refresh_token):
  queue = load_queue_from_db(user_id)
  queue_to_increase= {}
  is_duplicate = False
  for track in queue:
      track_sku_list = track['SKU'].split(', ')
      track_return_quantity_list = track['return_quantity'].split(', ') 
      i = 0
      for individual_sku in track_sku_list:  
        for sku in queue_to_increase.keys():
          if sku == individual_sku:
            is_duplicate = True
        if is_duplicate:
          queue_to_increase[individual_sku] = int(queue_to_increase[individual_sku]) + int(track_return_quantity_list[i])
          i+=1
        else:
          queue_to_increase[individual_sku]= int(track_return_quantity_list[i])
          i+=1

  return queue_to_increase



 #Must adjust this for the list items like did a few lines above 
def checkInventoryIncrease(Initial_quantity_of_skus, skus_and_increases, refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  #Test to see if inventory update   

  
  
  
  while True:
    # print(skus_and_increases)
    counter = int(0)
    Updated_Inventory_Reading = checkInventory(refresh_token)
    if(skus_and_increases):
      for sku in skus_and_increases.keys():
        Quantity_of_SKU = skus_and_increases[sku] 
  
        print("Quantity left of sku")
        print(sku)
        print("is")
        print(skus_and_increases[sku])
        
        Initial_quantity_of_sku= Initial_quantity_of_skus[sku]
        print(Updated_Inventory_Reading[sku])
        print(int(Initial_quantity_of_sku) + int(skus_and_increases[sku]))
        print(counter)
        print(len(skus_and_increases))
        if (int(Updated_Inventory_Reading[sku]) == (int(Initial_quantity_of_sku) + int(skus_and_increases[sku]))): 
          counter+=1
          if counter == len(skus_and_increases):
            print('breaking')
            return "Inventory Increased Successfully"
    
      time.sleep(60)
    else:
      return ("No returns in queue detected")
  return "Inventory Increase Not Detected" 



def get_addresses_from_GetOrders(refresh_token):
  credentials = dict(
    refresh_token=refresh_token,
    lwa_app_id=os.environ['LWA_CLIENT_ID'],
    lwa_client_secret=os.environ['LWA_CLIENT_SECRET'],
    aws_access_key=os.environ['AWS_ACCESS_KEY'],
    aws_secret_key=os.environ['AWS_SECRET_KEY'],  
    #role_arn="arn:aws:iam::108760843519:role/New_Role"
)
  res = Orders(credentials=credentials, marketplace=Marketplaces.US)
  try: 
    #result = res.get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())
    # result = res.get_orders(CreatedAfter='2023-04-20', CreatedBefore=date.today().isoformat()).payload
    result = res.get_orders(CreatedAfter='2023-04-20').payload
  #print(result)
    orders = result["Orders"]
  
    orders_Info = {}

    #print(orders)
    for order in orders:
      #print("PRINTING ORDER: ")
      #print(order)
      orderID = order["AmazonOrderId"]
      address = None
      for key in order.keys():
        if key=="ShippingAddress":
          address = order["ShippingAddress"]
      #print("PRINTING ORDERid AND ADDRESS:" )
      #print(orderID)
      #print(address)
      orders_Info[orderID] = address
      
    return orders_Info
  except SellingApiException as ex:
    print(ex)
    return 'EXCEPTION'






