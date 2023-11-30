from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class PDFReport:
    def __init__(self, path):
        self.path = path
        self.elements = []

    def add_title(self, title_text):
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title = Paragraph(title_text, title_style)
        self.elements.append(title)

    def add_paragraph(self, content):
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        paragraph = Paragraph(content, normal_style)
        self.elements.append(paragraph)

    def add_table(self, content):
        rows = [row.split('\t') for row in content.splitlines()]
        table = Table(rows)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(table_style)
        self.elements.append(table)

    def save_report(self):
        pdf_report = SimpleDocTemplate(self.path, pagesize=letter)

        pdf_report.build(self.elements)
