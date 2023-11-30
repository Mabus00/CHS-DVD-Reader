from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph

class PDFReport:
    def __init__(self, path):
        # Initialize the PDFReport with the file path and an empty elements list.
        self.path = path
        self.elements = []

    def add_title(self, title):
        # Add a title to the PDF.
        styles = getSampleStyleSheet()
        self.elements.append(Paragraph(title, styles['Title']))

    def add_paragraph(self, content):
        # Add a paragraph to the PDF.
        styles = getSampleStyleSheet()
        self.elements.append(Paragraph(content, styles['Normal']))

    def add_table(self, content):
        # Add a table to the PDF using tab-separated content.
        # Split the content by tabs (\t) or multiple tabs (\t\t, \t\t\t, etc.)
        rows = [row.split('\t') for row in content.splitlines()]

        # Create a Table object
        table = Table(rows)

        # Define table styles
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row background color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Middle vertical alignment for all cells
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Table border
        ])

        # Apply table styles
        table.setStyle(table_style)

        # Add the table to the elements list
        self.elements.append(table)

    def save_report(self):
        # Save the PDF report with the added elements using ReportLab canvas.

        # Create a canvas object
        c = canvas.Canvas(self.path, pagesize=letter)

        # Set the starting y-position for drawing elements
        y = 750

        for element in self.elements:
            # Draw each element on the canvas
            if isinstance(element, Paragraph):
                # Draw Paragraph elements
                element.wrapOn(c, 500, 50)  # Set width and height limits for the paragraph
                element.drawOn(c, 50, y)
                y -= 20  # Adjust y-position after each paragraph
            elif isinstance(element, Table):
                # Draw Table elements
                table_width, table_height = element.wrap(0, 0)  # Get table dimensions
                element.drawOn(c, 50, y - table_height)
                y -= table_height + 20  # Adjust y-position after the table

        # Save the canvas
        c.save()
