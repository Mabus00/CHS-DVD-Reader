from reportlab.lib.pagesizes import letter
from  reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from  reportlab.platypus.frames import Frame
from  reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import os

class PDFReport(BaseDocTemplate):
    def __init__(self, path, **kw):
        self.path = path
        self.elements = []
        # define document page template
        self.allowSplitting = 0
        super().__init__(self.path, **kw)
        # set template for document
        template = PageTemplate('normal', [Frame(1.5*cm, 1.5*cm, 15*cm, 25*cm, id='F1')])
        self.addPageTemplates(template)

        # set styles for document
        self.styles = [
            PS(fontSize=20, name='Title', spaceAfter=20, leading=12),
            PS(fontSize=14, name='Normal', spaceAfter=5, leading=12),
        ]

        self.toc = TableOfContents()

        # set styles for toc
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            PS(fontName='Times-Bold', fontSize=20, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=16),
            PS(fontSize=18, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=5, leading=12),
        ]

    # def afterFlowable(self, flowable):
    #     "Registers TOC entries."
    #     if flowable.__class__.__name__ == 'Paragraph':
    #         text = flowable.getPlainText()
    #         style = flowable.style.name
    #         if style == 'Heading1':
    #             self.notify('TOCEntry', (0, text, self.page))
    #         if style == 'Heading2':
    #             self.notify('TOCEntry', (1, text, self.page))

    def add_toc(self, title):
        self.elements.append(self.toc)
        self.elements.append(Paragraph(title, self.toc.levelStyles[0]))

    def add_title(self, title_text):
        title = Paragraph(title_text, self.styles[0])
        self.elements.append(title)

    def add_paragraph(self, content):
        paragraph = Paragraph(content,self.styles[1])
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
        pdf_report = PDFReport(self.path, pagesize=letter)
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
            c.drawString(1.7 * cm, 1.2 * cm, f"Page {i + 1} of {total_pages}")
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
