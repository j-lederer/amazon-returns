from fpdf import FPDF
from flask import Response
from .models import Tracking_ids
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# from . import db
#from.database import load_queue_from_db
from .amazonAPI import produce_pdf_slim

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import Response
from io import BytesIO

def download_inventory_change(user_id, refresh_token):
    response = produce_pdf_slim(user_id, refresh_token)
    queue_to_increase = response
  
    # # Create a new PDF document
    # pdf = SimpleDocTemplate("InventoryUpdate.pdf", pagesize=letter)

    # Create a BytesIO object as an in-memory buffer
    pdf_buffer = BytesIO()

    # Create a new PDF document
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Create a table with 4 columns
    table_data = [['SKU',  'Inventory Change']]
    for sku in queue_to_increase.keys():
        table_data.append([
            sku,
            f' +{queue_to_increase[sku]}',
            
        ])

    # Apply table styles
    table = Table(table_data, colWidths=[1.5 * inch] * 4, rowHeights=[0.4 * inch] * len(table_data))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Build the PDF content
    pdf.build([table])

    # # Read the generated PDF and return it as a Flask Response
    # with open("InventoryUpdate.pdf", "rb") as f:
    #     pdf_buffer = f.read()

     # Move the buffer's pointer to the beginning for reading
    pdf_buffer.seek(0)


    return Response(pdf_buffer, mimetype='application/pdf')


