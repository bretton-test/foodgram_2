import io

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

w, h = A4
PAGE_HEIGHT = h
PAGE_WIDTH = w


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont('Times-Roman', 9)
        self.setLineWidth(0.1)
        self.setStrokeColor(Color(0, 0, 0, alpha=0.2))
        self.setFillColor(Color(0, 0, 0, alpha=0.4))
        self.line(cm, 1.5 * cm, A4[0] - cm, 1.5 * cm)
        self.drawRightString(
            A4[0] - cm,
            1.1 * cm,
            "Page %d of %d" % (self._pageNumber, page_count),
        )


def my_first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVuSerif', 15)
    canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 38, doc.title)
    doc.afterPage()
    canvas.restoreState()


def my_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVuSerif', 9)
    canvas.restoreState()


def get_shopping_list_text(
        ingredient__name, ingredient__measurement_unit__name, amount
):
    return (
        f'{ingredient__name}'
        f' ({ingredient__measurement_unit__name}) - {amount}'
    )


def create_pdf_from_queryset(queryset, username):
    pdf_file = io.BytesIO()
    ru_style = getSampleStyleSheet()['Normal']
    ru_style.fontName = 'DejaVuSerif'
    doc = SimpleDocTemplate(
        pdf_file,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
    doc.title = f'Список покупок для {username}'
    story = [Spacer(2.5, 0.75 * inch)]
    for items in queryset:
        story.append(Paragraph(get_shopping_list_text(**items), ru_style))

    story.append(PageBreak())
    doc.build(
        story,
        onFirstPage=my_first_page,
        onLaterPages=my_later_pages,
        canvasmaker=NumberedCanvas,
    )
    pdf_file.seek(0)
    return pdf_file
