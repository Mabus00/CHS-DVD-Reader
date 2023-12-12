from reportlab.lib.pagesizes import letter
from  reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from  reportlab.platypus.frames import Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import os

class PDFReport(BaseDocTemplate):
    def __init__(self, path, **kw):
        self.path = path
        self.elements = []

        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, self.path, **kw)
        template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
        self.addPageTemplates(template)

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

        table_data = []

        # Separate content into folders
        folders = [list(filter(None, folder.split('\n'))) for folder in content.split('\n\n') if folder.strip()]

         # Add the message before the table
        message = folders[0][0]
        self.add_paragraph(message)
        folders[0] = folders[0][1:]

        for folder in folders:
            # Table title (Folder Name)
            folder_title = folder[0]

            # Commence construction of table for the folder
            table_data = [[folder_title]]  # Include folder_title in the merged top row

            if len(folder) > 1 and '\t' in folder[1]: # if there's more rows and the rows have columns; as opposed to single row messages (if more rows)
                # Table column headers
                column_headers = folder[1].split('\t')
                # Table data for the folder
                folder_table_data = [column_headers]  # Add the column headers
                folder_table_data.extend([row.split('\t') for row in folder[2:]])  # Finally, add the data rows
                table_data.extend(folder_table_data)  # Extend with the data

            table = Table(table_data, hAlign='LEFT', repeatRows=2)

            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # First row shading
                ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),       # Second row shading
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('WORDWRAP', (2, 0), (2, -1), 1),  # Enable word wrap for the third column
                ('SPAN', (0, 0), (-1, 0)),  # Merge cells for the first row
            ])

            table.setStyle(table_style)
            
            self.elements.append(table)
            self.elements.append(Spacer(1, 12))  # Add space after each table

        # if len(self.elements) > 0:  # Check if there are any elements added
        #     self.elements.append(PageBreak())

    def save_report(self):
        pdf_report = SimpleDocTemplate(self.path, pagesize=letter)
        pdf_report.build(self.elements)
        self.add_page_numbers()

    def add_page_numbers(self):
        input_pdf = self.path
        output_pdf = "temp.pdf"

        # Read the input PDF and get the total number of pages
        with open(input_pdf, "rb") as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)

        # Create a new PDF with page numbers added
        c = canvas.Canvas(output_pdf)
        for i in range(total_pages):
            c.saveState()
            c.setFont("Helvetica", 9)
            c.drawString(inch, 0.75 * inch, f"Page {i + 1} of {total_pages}")
            c.restoreState()
            c.showPage()

        c.save()

        # Merge the original PDF with the one containing page numbers
        merger = PdfWriter()
        original_pdf = PdfReader(input_pdf)
        temp_pdf = PdfReader(output_pdf)

        for pageNum in range(total_pages):
            page = original_pdf.pages[pageNum]
            overlay = temp_pdf.pages[pageNum]
            page.merge_page(overlay)
            merger.add_page(page)

        with open(self.path, "wb") as file:
            merger.write(file)

        # Clean up the temporary PDF
        os.remove(output_pdf)

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
