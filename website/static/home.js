document.getElementById('clearSearchButton').addEventListener('click', function() {
    window.location.href = '/clearSearch';
});

document.getElementById('refreshButton').addEventListener('click', function() {
    window.location.href = '/refresh_returns_and_inventory';
});


document.getElementById('addToJobsButton').addEventListener('click', function() {
    if (confirm('Add the queue to your jobs. The increase inventory operation will execute at 12:00 am ET every night.')) {
        window.location.href = '/create_job';
    }
});

document.getElementById('clearQueueButton').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear the queue?')) {
        window.location.href = '/clearQueue';
    }
});

document.getElementById('downloadPdfButton').addEventListener('click', function() {
    var url = this.getAttribute('data-url');
    window.location.href = url;
});

document.getElementById('downloadSlimButton').addEventListener('click', function() {
    var url = this.getAttribute('data-url');
    window.location.href = url;
});


/*Adjusting line heights*/
 document.addEventListener('DOMContentLoaded', function() {
  var total_pixels_added=0;
     
     var intro_answers_address_divHeight = document.getElementById('intro_answers--address').offsetHeight;
      var intro_address_divHeight_before = document.getElementById('intro--address').offsetHeight;
      var intro_address = document.getElementById('intro--address');
        intro_address.style.height= intro_answers_address_divHeight + 'px'
       total_pixels_added += intro_answers_address_divHeight - intro_address_divHeight_before;
     
     var intro_answers_name_divHeight = document.getElementById('intro_answers--item_name').offsetHeight;
     var intro_name_divHeight_before = document.getElementById('intro--name').offsetHeight;
     var intro_name = document.getElementById('intro--name');
       intro_name.style.height= intro_answers_name_divHeight + 'px'
      total_pixels_added += intro_answers_name_divHeight - intro_name_divHeight_before;

     var intro_answers_sku_divHeight = document.getElementById('intro_answers--sku').offsetHeight;
       var intro_sku_divHeight_before = document.getElementById('intro--sku').offsetHeight;
       var intro_sku = document.getElementById('intro--sku');
         intro_sku.style.height= intro_answers_sku_divHeight + 'px'
        total_pixels_added += intro_answers_sku_divHeight - intro_sku_divHeight_before;

     var intro_answers_number_items_bought_divHeight = document.getElementById('intro_answers--order_quantity').offsetHeight;
       var intro_number_items_bought_divHeight_before = document.getElementById('intro--number_items_bought').offsetHeight;
       var intro_number_items_bought = document.getElementById('intro--number_items_bought');
         intro_number_items_bought.style.height= intro_answers_number_items_bought_divHeight + 'px'
        total_pixels_added += intro_answers_number_items_bought_divHeight - intro_number_items_bought_divHeight_before;

     var intro_answers_number_items_bought_divHeight = document.getElementById('intro_answers--order_quantity').offsetHeight;
        var intro_number_items_bought_divHeight_before = document.getElementById('intro--number_items_bought').offsetHeight;
        var intro_number_items_bought = document.getElementById('intro--number_items_bought');
          intro_number_items_bought.style.height= intro_answers_number_items_bought_divHeight + 'px'
         total_pixels_added += intro_answers_number_items_bought_divHeight - intro_number_items_bought_divHeight_before;

     var intro_answers_number_items_returned_divHeight = document.getElementById('intro_ansers--return_quantity').offsetHeight;
       var intro_number_items_returned_divHeight_before = document.getElementById('intro--number_items_returned').offsetHeight;
       var intro_number_items_returned = document.getElementById('intro--number_items_returned');
         intro_number_items_returned.style.height= intro_answers_number_items_returned_divHeight + 'px'
        total_pixels_added += intro_answers_number_items_returned_divHeight - intro_number_items_returned_divHeight_before;

     var intro_answers_inventory_divHeight = document.getElementById('intro_answers--inventory').offsetHeight;
       var intro_inventory_divHeight_before = document.getElementById('intro--inventory').offsetHeight;
       var intro_inventory = document.getElementById('intro--inventory');
         intro_inventory.style.height= intro_answers_inventory_divHeight + 'px'
        total_pixels_added += intro_answers_inventory_divHeight - intro_inventory_divHeight_before;
     
     var intro_answers_order_id_divHeight = document.getElementById('intro_answers--order_id').offsetHeight;
       var intro_order_id_divHeight_before = document.getElementById('intro--order_id').offsetHeight;
       var intro_order_id = document.getElementById('intro--order_id');
         intro_order_id.style.height= intro_answers_order_id_divHeight + 'px'
        total_pixels_added += intro_answers_order_id_divHeight - intro_order_id_divHeight_before;

     var intro_answers_refund_amount_divHeight = document.getElementById('intro_answers--refund_amount').offsetHeight;
       var intro_refund_amount_divHeight_before = document.getElementById('intro--refund_amount').offsetHeight;
       var intro_refund_amount = document.getElementById('intro--refund_amount');
         intro_refund_amount.style.height= intro_answers_refund_amount_divHeight + 'px'
        total_pixels_added += intro_answers_refund_amount_divHeight - intro_refund_amount_divHeight_before;
    

     


     
        console.log(`total pixels added: ${total_pixels_added}`);
      var intro_answers_div= document.getElementById('intro_answers');
      var top_position = parseFloat(window.getComputedStyle(intro_answers_div).getPropertyValue('top'));
     console.log(`top before: ${top_position}`);
     intro_answers_div.style.top = ( top_position - total_pixels_added) + 'px'  

     var top_after = window.getComputedStyle(intro_answers_div).getPropertyValue('top');
      console.log(`top after: ${top_after}`);
   
 });


