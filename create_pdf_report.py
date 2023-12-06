from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class PDFReport:
    def __init__(self, path):
        self.path = path
        self.elements = []
        self.page_count = 0  # Initialize page count

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

        # Separate content into folders
        folders = [list(filter(None, folder.split('\n'))) for folder in content.split('\n\n') if folder.strip()]

         # Add the message before the table
        message = folders[0][0]
        self.add_paragraph(message)

        for folder in folders[1:]:
            # Table title (Folder Name)
            folder_title = folder[0]
            #self.add_paragraph(folder_title)

            # Table column headers
            column_headers = folder[1].split('\t')
            # Table data for the folder
            folder_table_data = [column_headers]  # Add the column headers
            folder_table_data.extend([row.split('\t') for row in folder[2:]])  # Finally, add the data rows

            # Construct the table for the folder
            table_data = [[folder_title]]  # Include folder_title in the merged top row
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

        if len(self.elements) > 0:  # Check if there are any elements added
            self.elements.append(PageBreak())

    def save_report(self):
        doc = SimpleDocTemplate(self.path, pagesize=letter)

        # Create a page template for adding page numbers
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='test', frames=frame,
                                onPage=lambda canvas, doc: self.add_page_number(canvas, doc))
        doc.addPageTemplates([template])

        # Add your elements
        self.page_count = 0  # Reset page count
        doc.build(self.elements, onFirstPage=lambda canvas, doc: self.add_page_number(canvas, doc),
                  onLaterPages=lambda canvas, doc: self.add_page_number(canvas, doc, total_pages=True))

    def add_page_number(self, canvas, doc, total_pages=False):
        self.page_count += 1
        page_num = canvas.getPageNumber()
        text = "Page %s of %s" % (page_num if not total_pages else self.page_count, self.page_count)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(inch, 0.75 * inch, text)
