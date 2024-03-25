from reportlab.lib.pagesizes import letter
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib import colors
from reportlab.lib.units import cm
from hashlib import sha1
import csv
import os

class PDFReport(BaseDocTemplate):
    def __init__(self, path, **kw):
        self.path = path
        self.elements = []

        # Create a canvas object
        self.canv = canvas.Canvas(path, pagesize=letter)

        # define document page template
        self.allowSplitting = 0
        super().__init__(self.path, **kw)
        # set template for document
        template = PageTemplate('normal', [Frame(1.5*cm, 1.5*cm, 15*cm, 25*cm, id='F1')], onPageEnd = self.footer)
        self.addPageTemplates(template)
        
        # set styles for document
        self.styles = [
            PS(fontSize=20, name='Title', spaceAfter=40),
            PS(fontSize=16, name='TOC', spaceBefore = 10, spaceAfter=10),
            PS(fontSize=12, name='Folder Title', spaceBefore = 15, spaceAfter=20),
            PS(fontSize=10, name='Folder Data', spaceBefore = 10, spaceAfter=10, leftIndent = 10),
        ]
        # set styles for toc
        self.toc = TableOfContents()

        self.toc.levelStyles = [
            PS(fontSize=16, name='TOCHeading1', spaceBefore=5),
            PS(fontSize=12, name='TOCHeading2', spaceBefore=5),
        ]
        
        # set style for tables
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # First row shading
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), 1),  # Enable word wrap for the third column
        ])

    def afterFlowable(self, flowable):
        print("""Registers TOC entries.""")
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            # Add entries to TOC based on styles
            if style == 'TOCHeading1':
                level = 0  # Define the level level for TOC entry
            elif style == 'TOCHeading2':
                level = 1  # Define the level level for TOC entry
            else:
                level = None  # If it's not a TOC heading, it won't be added to TOC
            E = [level, text, self.page]
            if level is not None:
                anchor = getattr(flowable, '_bookmarkName', None)  # Get the anchor point
                E.append(anchor)
                self.notify('TOCEntry', tuple(E))

    def add_report_title(self, title_text):
        title = Paragraph(title_text, self.styles[0])
        self.elements.append(title)

    def add_toc(self, toc_title):
        # Adding the TOC title to the TOC
        toc_title_paragraph = Paragraph(toc_title, self.styles[1])
        self.elements.append(toc_title_paragraph)
        # Adding the Table of Contents
        self.elements.append(self.toc)
        self.elements.append(PageBreak())

    # add to TOC and make headings into hyperlinks
    def add_to_toc(self, text, style, message = ""):
        #create bookmarkname
        bn = sha1((message + text + style.name).encode()).hexdigest()
        #modify paragraph text to include an anchor point with name bn
        heading = Paragraph(text + '<a name="%s"/>' % bn, style)
        #store the bookmark name on the flowable so afterFlowable can see this
        heading._bookmarkName = bn
        self.elements.append(heading)

    def add_folder_title(self, title_text):
        title = Paragraph(title_text, self.styles[2])
        self.elements.append(title)

    def add_folder_data(self, content):
        paragraph = Paragraph(content, self.styles[3])
        self.elements.append(paragraph)

    def footer(self, canvas, doc):
        self.canv.saveState()
        self.canv.setFont('Times-Roman', 9)
        page_num = self.canv.getPageNumber()
        self.canv.drawString(1.5 * cm, 0.75 * cm, f"Page {page_num}")
        self.canv.restoreState()

    def process_block_data(self, block_data):
        table_data = []
        # Process block data
        for data_row in block_data:
            table_data.extend([data_row])
        
        # Width of letter-sized paper minus margins and paddings
        available_width = letter[0] - 72  # Subtracting 72 points as a margin
        # Adjusting column widths as needed
        # You can adjust the factors below as per your requirement
        col_widths = [available_width * 0.12, available_width * 0.12, available_width * 0.46, available_width * 0.3]

        table = Table(table_data, colWidths=col_widths, hAlign='LEFT', style=self.table_style, repeatRows=1)           
        self.elements.append(table)
        self.elements.append(Spacer(1, 10))  # Add space after each table
        
    def add_table(self, csv_file_path):
        folder_title = None
        raster_block_data = []
        vector_block_data = []
        raster_column_headers = []
        vector_column_headers = []

        # Open the .csv file and read its content
        with open(csv_file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)

            if "misc" not in csv_file_path:
                # Extract the base name from the full path to add to TOC
                basename = os.path.basename(csv_file_path)
                # Remove the file extension
                filename_without_extension = os.path.splitext(basename)[0]
                filename =  filename_without_extension.replace('_', ' ').split()
                filename_title = ' '.join(word.capitalize() for word in filename[:2])
                self.add_to_toc(filename_title, self.toc.levelStyles[0])

                for row in csv_reader:
                    if not row:  # Check for blank line indicating the end of a data block
                        folder_title = None
                    elif len(row) == 1:  # Check if the row has only one column (folder title)
                        folder_title = ' '.join(row)
                        #self.add_folder_title(folder_title) # Add folder title to pdf doc
                    elif folder_title:  # Use folder title to confirm still within data block; add row of data for end-block processing 
                        row_with_title = row + [folder_title]
                        if "RM" in folder_title:
                            # Append folder_title as the fourth column to each row
                            if any(any(char.isdigit() for char in string) for string in row): # digits means it's a line of data; ignore headers
                                raster_block_data.append(row_with_title)
                            elif not raster_column_headers:
                                raster_column_headers = row
                                raster_block_data.insert(0, raster_column_headers)
                        else:
                             # Append folder_title as the fourth column to each row
                            if any(any(char.isdigit() for char in string) for string in row): # digits means it's a line of data; ignore headers
                                vector_block_data.append(row_with_title)
                            elif not vector_column_headers:
                                vector_column_headers = row
                                vector_block_data.insert(0, vector_column_headers)

            else:
                for i, row in enumerate(csv_reader):
                    if i == 0:
                        self.add_to_toc(row[0], self.toc.levelStyles[0])
                    else:
                        self.add_folder_data("\n".join(row))  # Treat each single line as a paragraph
                self.elements.append(Spacer(1, 12))  # Add space after each table

        # Process the last data block if any
        if raster_block_data:
            self.process_block_data(raster_block_data)
        
        if vector_block_data:
            self.process_block_data(vector_block_data)

    def save_report(self):
        pdf_report = PDFReport(self.path, pagesize=letter)
        pdf_report.multiBuild(self.elements)

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
