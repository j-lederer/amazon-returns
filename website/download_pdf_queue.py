from fpdf import FPDF
from flask import Response
from .models import Tracking_ids
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask import Blueprint, render_template, request, flash, jsonify
# from flask_login import login_required, current_user
# from . import db
from.database import load_queue_from_db



from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from flask import Response
from io import BytesIO

def download_queue_data(user_id):
    tracking_ids = load_queue_from_db(user_id)

    # # Create a new PDF document
    # pdf = SimpleDocTemplate("queue.pdf", pagesize=letter)

    # Create a BytesIO object as an in-memory buffer
    pdf_buffer = BytesIO()

    # Create a new PDF document
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Create a table with 3 columns
    table_data = [['Tracking ID', 'SKU', 'Return Quantity']]
    for tracking_id in tracking_ids:
        table_data.append([
            tracking_id['tracking'],
            str(tracking_id['SKU']),
            tracking_id['return_quantity']
        ])

    # Apply table styles
    table = Table(table_data, colWidths=[1.5 * inch] * 3, rowHeights=[0.4 * inch] * len(table_data))
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
    # with open("queue.pdf", "rb") as f:
    #     pdf_buffer = f.read()

     # Move the buffer's pointer to the beginning for reading
    pdf_buffer.seek(0)


    return Response(pdf_buffer, mimetype='application/pdf')


# def download_queue_data(user_id):
#     tracking_ids = load_queue_from_db(user_id)
#     print(tracking_ids)
#     pdf =PDF()
#     return pdf.generate_pdf(tracking_ids)

# class PDF(FPDF):
#     def __init__(self):
#         super().__init__()
#         self.alias_nb_pages()
#         self.add_page()
#         self.set_font('Helvetica', '', 12)
      
#     def header(self):
#         # Logo
#         # self.image('app/static/images/logo.jpg', 180, 8, 12)
#         self.set_font('Helvetica', 'B', 15)
#         # Move to the right
#         self.cell(80)
#         # Title
#         self.cell(50, 10, 'Queue Demo', 1, 0, 'C')
#         # Line break
#         self.ln(20)

#     def footer(self):
#         # Position at 1.5 cm from bottom
#         self.set_y(-15)
#         # Helvetica italic 8
#         self.set_font('Helvetica', '', 8)
#         self.set_text_color(128)
#         # Page number
#         self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

#     def table(self, tracking_ids):
#         # Colors, line width and bold font
#         self.set_font('Helvetica', 'B', 10)
#         self.set_fill_color(255, 0, 0)
#         self.set_text_color(255)
#         self.set_draw_color(128, 0, 0)
#         self.set_line_width(.3)
#         self.set_font('', 'B')
#         # Header
#         self.cell(50, 10, 'Tracking ID', 1, 0, 'C', 1)
#         self.cell(50, 10, 'SKU', 1, 0, 'C', 1)
#         self.cell(50, 10, 'Return Quantity', 1, 0, 'C', 1)
        
#         self.ln()
#         # Data
#         self.set_text_color(0)
#         self.set_font('Helvetica', '', 8)
#         for tracking_id in tracking_ids:
#             # print("TRACKING_ID:")
#             # print (tracking_id)
#             # print("TRACKING_ID['tracking']:")
#             # print(tracking_id['tracking'])
#             self.cell(50, 10, tracking_id['tracking'], 1, 0, 'C')
#             self.cell(50, 10, str(tracking_id['SKU']), 1, 0, 'C')
#             self.cell(50, 10, tracking_id['return_quantity'], 1, 1, 'C')
#         # Closing line
#         self.cell(0, 10, '', 0, 1)

#     def generate_pdf(self, tracking_ids):
#         # print("Generating PDF...")
#         # print("Tracking IDs:", tracking_ids)
#         self.table(tracking_ids)
#         buffer = self.output(dest='S')
#         # print("PDF Generated Successfully.")
#         return Response(buffer, mimetype='application/pdf')
#     #     # self.output('website/static/files/queue.pdf', 'F')