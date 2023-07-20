from fpdf import FPDF
from flask import Response
from .models import Tracking_ids
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# from . import db
#from.database import load_queue_from_db
from .amazonAPI import produce_pdf

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import Response
from io import BytesIO

def download_queue_and_inventory_change_data(user_id, refresh_token):
    response = produce_pdf(user_id, refresh_token)
    Quantity_of_SKUS = response[0]
    queue_to_increase = response[1]
    final_inventory = response[2]

    # # Create a new PDF document
    # pdf = SimpleDocTemplate("InventoryUpdate.pdf", pagesize=letter)

    # Create a BytesIO object as an in-memory buffer
    pdf_buffer = BytesIO()

    # Create a new PDF document
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Create a table with 4 columns
    table_data = [['SKU', 'Original Inventory', 'Inventory Change', 'Final Inventory']]
    for sku in queue_to_increase.keys():
        table_data.append([
            sku,
            Quantity_of_SKUS[sku],
            f' +{queue_to_increase[sku]}',
            str(final_inventory[sku])
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



# def download_queue_and_inventory_change_data(user_id, refresh_token):
#     response = produce_pdf(user_id, refresh_token)
#     Quantity_of_SKUS = response[0]
#     queue_to_increase =response[1]
#     final_inventory = response[2]
#     pdf = PDF()
#     return (pdf.generate_pdf( Quantity_of_SKUS, queue_to_increase, final_inventory))

# class PDF(FPDF):
#     def __init__(self):
#         super().__init__(format='A4')
#         self.alias_nb_pages()
#         self.add_page()
#         self.set_font('Arial', '', 12)
      
#     def header(self):
#         # Logo
#         # self.image('app/static/images/logo.jpg', 180, 8, 12)
#         self.set_font('Arial', 'B', 15)
#         # Move to the right
#         self.cell(80)
#         # Title
#         self.cell(50, 10, 'Queue Demo', 1, 0, 'C')
#         # Line break
#         self.ln(20)

#     def footer(self):
#         # Position at 1.5 cm from bottom
#         self.set_y(-15)
#         # Arial italic 8
#         self.set_font('Arial', '', 8)
#         self.set_text_color(128)
#         # Page number
#         self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

#     def table(self, Quantity_of_SKUS, queue_to_increase, final_inventory):
#         # Colors, line width and bold font
#         self.set_font('Arial', 'B', 10)
#         self.set_fill_color(255, 0, 0)
#         self.set_text_color(255)
#         self.set_draw_color(128, 0, 0)
#         self.set_line_width(.3)
#         self.set_font('', 'B')
#         # Header
#         self.cell(50, 10, 'SKU', 1, 0, 'C', 1)
#         self.cell(40, 10, 'Original Inventory', 1, 0, 'C', 1)
#         self.cell(40, 10, 'Inventory Change', 1, 0, 'C', 1)
#         self.cell(40, 10, 'Final Inventory', 1, 0, 'C', 1)
#         self.ln()
#         # Data
#         self.set_text_color(0)
#         self.set_font('Arial', '', 8)
#         for sku in queue_to_increase.keys():
#             self.cell(50, 10, sku, 1, 0, 'C')
#             self.cell(40, 10, Quantity_of_SKUS[sku], 1, 0, 'C')
#             self.cell(40, 10, f' +{queue_to_increase[sku]}', 1, 0, 'C')
#             self.cell(40, 10, str(final_inventory[sku]), 1, 1, 'C')
            
#         # Closing line
#         self.cell(0, 10, '', 0, 1)

#     def generate_pdf(self, Quantity_of_SKUS, queue_to_increase, final_inventory):
#         self.table(Quantity_of_SKUS, queue_to_increase,  final_inventory)
#         return( Response(self.output(dest='S'), mimetype='application/pdf'))
#         # self.output('website/static/files/InventoryUpdate.pdf', 'F')