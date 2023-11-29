from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class PDFReport:
    def __init__(self, file_name):
        """
        Initialize the PDFReport with the file name and an empty elements list.
        """
        self.file_name = file_name
        self.elements = []

    def add_title(self, title):
        """
        Add a title to the PDF.
        """
        styles = getSampleStyleSheet()
        self.elements.append(Paragraph(title, styles['Title']))

    def add_paragraph(self, content):
        """
        Add a paragraph to the PDF.
        """
        styles = getSampleStyleSheet()
        self.elements.append(Paragraph(content, styles['Normal']))

    def add_table(self, content):
        """
        Add a table to the PDF using tab-separated content.
        Adjust the table width to fit the specified page width.
        """
        # Split the content by tabs (\t) or multiple tabs (\t\t, \t\t\t, etc.)
        rows = [row.split('\t') for row in content.splitlines()]
        num_cols = len(rows[0])

        page_width = 612
        # Calculate the width for each column to fit the page width
        col_width = page_width / num_cols
        col_widths = [col_width] * num_cols

        # Create a Table object with adjusted column widths
        table = Table(rows, colWidths=col_widths)

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
        """
        Save the PDF report with the added elements.
        """
        pdf = SimpleDocTemplate(self.file_name, pagesize=letter)
        pdf.build(self.elements)


