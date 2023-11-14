from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFReport:
    def __init__(self, file_name):
        self.file_name = file_name
        self.pdf_canvas = canvas.Canvas(self.file_name, pagesize=letter)

    def add_title(self, x, y, title):
        self.pdf_canvas.setFont("Helvetica-Bold", 16)
        self.pdf_canvas.drawString(x, y, title)

    def add_paragraph(self, x, y, content):
        self.pdf_canvas.setFont("Helvetica", 12)
        self.pdf_canvas.drawString(x, y, content)

    def save_report(self):
        self.pdf_canvas.save()

