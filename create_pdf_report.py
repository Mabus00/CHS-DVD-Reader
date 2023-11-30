from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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
        self.elements.append(Spacer(1, 12))  # Add space after the paragraph

    def add_table(self, content):
        content_parts = content.split('\n')

        # Add the paragraph before the table
        paragraph = content_parts[0]
        self.add_paragraph(paragraph)

        # Separate content into folders
        folders = [list(filter(None, folder.split('\n'))) for folder in content.split('\n\n') if folder.strip()]

        for folder in folders:
            # Table title (Folder Name)
            folder_title = folder[0]
            self.add_title(folder_title)

            # Table column headers
            column_headers = folder[1].split('\t')

            # Table data for the folder
            folder_table_data = [row.split('\t') for row in folder[2:]]

            # Construct the table for the folder
            table = Table([column_headers] + folder_table_data)
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('WORDWRAP', (0, 2), (-1, -1), 1),  # Enable word wrap for the third column
            ])
            table.setStyle(table_style)

            self.elements.append(Paragraph(folder_title, self.elements[-1].style))  # Append folder title
            self.elements.append(table)
            self.elements.append(Spacer(1, 12))  # Add space after each table

    def save_report(self):
        pdf_report = SimpleDocTemplate(self.path, pagesize=letter)
        pdf_report.build(self.elements)
