'''
Creates the .pdf report.

'''

from reportlab.lib.pagesizes import letter, landscape
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
import glob

class CreatePDFReport(BaseDocTemplate):
    def __init__(self, run_checker_textbox, **kw):

        self.kw = kw
        self.run_checker_textbox = run_checker_textbox

        self.master_yyyymmdd = None
        self.current_yyyymmdd = None
        self.current_database_folder = None
        self.path = None
        self.report_title = None

        self.pageSize = landscape(letter) # Default to letter if not provided
        
        # these files are pre-formatted versions of the above files; used for the gui windows and pdf report
        self.csv_mod_files = [
            "misc_findings_type1_mod.csv",
            "misc_findings_type2_mod.csv",
            "new_editions_mod.csv",
            "new_charts_mod.csv",
            "charts_withdrawn_mod.csv"
        ]

    # code that allows the addition of text/tables/content to the document after the creation of the document
    def afterFlowable(self, flowable):
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

    def add_report_title(self):
        title = Paragraph(self.report_title, self.styles[0])
        self.elements.append(title)

    def add_toc(self, toc_title):
        # Adding the TOC title to the TOC
        toc_title_paragraph = Paragraph(toc_title, self.styles[1])
        self.elements.append(toc_title_paragraph)
        # Adding the Table of Contents
        self.elements.append(self.toc)
        self.elements.append(PageBreak())

    # add content to TOC and make headings into hyperlinks
    def add_to_toc(self, text, style, message = ""):
        #create bookmarkname
        bn = sha1((message + text + style.name).encode()).hexdigest()
        #modify paragraph text to include an anchor point with name bn
        heading = Paragraph(text + '<a name="%s"/>' % bn, style)
        #store the bookmark name on the flowable so afterFlowable can see this
        heading._bookmarkName = bn
        self.elements.append(heading)

    def add_folder_data(self, content):
        paragraph = Paragraph(content, self.styles[3])
        self.elements.append(paragraph)

    def footer(self, canvas, doc): # canvas and doc are provided on creation of the pdf
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
        # Sort table_data by the first column using the custom sorting function
        try:
            sorted_table_data = sorted(table_data[1:], key=lambda row: (row[0].isdigit(), row[0]))
        except Exception as e:
            print(f"An error occurred during sorting: {e}")
        # Add the header row to the sorted data
        table_data = [block_data[0]] + sorted_table_data     
        # Width of letter-sized paper minus margins and paddings
        available_width = self.pageSize[0] - 50  # Subtracting 72 points as a margin
        # Adjusting column widths as needed
        # You can adjust the factors below as per your requirement
        col_widths = [available_width * 0.10, available_width * 0.10, available_width * 0.55, available_width * 0.20]
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
                # anything that is misc will need to be investigated and resolved, and once done, there will be nothing to include in the report.
                # should the issue not be resolved then it will remain in the report
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
        self.multiBuild(self.elements)

    def update_paths(self, master_yyyymmdd, current_yyyymmdd, current_database_folder):
        self.master_yyyymmdd = master_yyyymmdd
        self.current_yyyymmdd = current_yyyymmdd
        self.current_database_folder = current_database_folder
        # set report title
        self.report_title = f"{self.master_yyyymmdd}_VS_{self.current_yyyymmdd} CHS DVD Report"
        # establish the current folder as the folder within which to save the report
        self.path = os.path.join(self.current_database_folder, f"{self.report_title}.pdf")
        # Reinitialize the parent class with the updated path
        self.init_document()

    def init_document(self):
        # Create a canvas object
        self.canv = canvas.Canvas(self.path, pagesize=self.pageSize)
        
        # define document page template
        self.allowSplitting = 0
        
        # Initialize the BaseDocTemplate with the correct path
        super().__init__(self.path, **self.kw)

        # Set template for document
        self.elements = []
        frame_width, frame_height = self.pageSize[0] - 4*cm, self.pageSize[1] - 4*cm
        template = PageTemplate('normal', [Frame(2*cm, 2*cm, frame_width, frame_height, id='F1')], onPageEnd=self.footer)
        self.addPageTemplates(template)
        
        # Set styles, TOC, table styles, etc.
        self.styles = [
            PS(fontSize=20, name='Title', spaceAfter=40),
            PS(fontSize=16, name='TOC', spaceBefore = 10, spaceAfter=10),
            PS(fontSize=12, name='Folder Title', spaceBefore = 15, spaceAfter=20),
            PS(fontSize=10, name='Folder Data', spaceBefore = 10, spaceAfter=10, leftIndent = 10),
        ]
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            PS(fontSize=16, name='TOCHeading1', spaceBefore=5, spaceAfter=15),
            PS(fontSize=12, name='TOCHeading2', spaceBefore=5, spaceAfter=15),
        ]
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), 1),
        ])

    def create_pdf_report(self):
        # Add title to the report
        self.add_report_title()
        # Add toc to the report
        self.add_toc('Table of Contents')
        # Filter only the _mod.csv files; formatted csv for gui window and pdf report
        csv_files = glob.glob(self.current_database_folder + "/*_mod.csv") 
        # Create a set of filenames from csv_files for faster lookup
        csv_files_set = set(map(lambda x: x.split('\\')[-1], csv_files))
        # Filter out filenames from csv_files that are not in self.csv_mod_files; possible not all files were created (e.g., no misc findings so no misc files)
        csv_files_filtered = [filename for filename in csv_files_set if filename in self.csv_mod_files]
        # Sort csv_files_filtered to match the order of self.csv_mod_files
        csv_files_sorted = sorted(csv_files_filtered, key=lambda x: self.csv_mod_files.index(x))
        for file in csv_files_sorted:
            csv_file_path = os.path.join(self.current_database_folder, file)
            # Add the content as a table to the PDF report
            self.add_table(csv_file_path)
        # Save the report
        self.save_report()
        # Print a message to indicate that the checker has run
        self.run_checker_textbox.emit('\nThe .pdf report was created succesfully!')

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
