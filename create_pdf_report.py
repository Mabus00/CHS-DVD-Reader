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
            PS(fontSize=20, name='Title', spaceAfter=30, leading=12),
            PS(fontSize=14, name='Normal', spaceAfter=10, leading=12),
        ]
        # set styles for toc
        self.toc = TableOfContents()
        self.toc.levelStyles = [
            PS(fontName='Times-Bold', fontSize=20, name='TOCHeading1', spaceBefore=10, leading=16),
            PS(fontSize=12, name='TOCHeading2', spaceBefore=5, leading=12, leftIndent=20),
        ]
        # set style for tables
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # First row shading
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),       # Second row shading
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (2, 0), (2, -1), 1),  # Enable word wrap for the third column
            ('SPAN', (0, 0), (-1, 0)),  # Merge cells for the first row
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

    # turn toc headings into hyperlinks
    def doHeading(self, text, style):
        #create bookmarkname
        bn = sha1((text + style.name).encode()).hexdigest()
        #modify paragraph text to include an anchor point with name bn
        heading = Paragraph(text + '<a name="%s"/>' % bn, style)
        #store the bookmark name on the flowable so afterFlowable can see this
        heading._bookmarkName = bn
        self.elements.append(heading)

    def add_toc(self, toc_title):
        self.elements.append(Paragraph(toc_title, self.styles[1]))
        self.elements.append(self.toc)
        self.elements.append(PageBreak())

    def footer(self, canvas, doc):
        self.canv.saveState()
        self.canv.setFont('Times-Roman', 9)
        page_num = self.canv.getPageNumber()
        self.canv.drawString(1.5 * cm, 0.75 * cm, f"Page {page_num}")
        self.canv.restoreState()

    def add_title(self, title_text):
        title = Paragraph(title_text, self.styles[0])
        self.elements.append(title)

    def add_paragraph(self, content):
        self.doHeading(content, self.toc.levelStyles[0])
        self.elements.append(Spacer(1, 12))  # Add space after the paragraph

    def add_table(self, content):
        table_data = []
        # Separate content into folders
        folders = [list(filter(None, folder.split('\n'))) for folder in content.split('\n\n') if folder.strip()]
        # first line in all folders contains the message and the first folder title
        # Extract message and print before the table
        message = folders[0][0]
        self.add_paragraph(message)
        # now that message has been used move the folder title into the message position to match remainder of folder structure; only needs to be done once for all folders
        folders[0] = folders[0][1:]
        # process folder content
        for folder in folders:
            # Table title (Folder Name)
            folder_title = folder[0]
            self.doHeading(folder_title, self.toc.levelStyles[1])
            self.elements.append(Spacer(1, 12))  # Add space after each table
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
                table.setStyle(self.table_style)            
                self.elements.append(table)
                self.elements.append(Spacer(1, 12))  # Add space after each table
            else:
                self.add_paragraph("\n".join(folder))  # Treat single line as a paragraph

    def save_report(self):
        pdf_report = PDFReport(self.path, pagesize=letter)
        pdf_report.multiBuild(self.elements)

# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
