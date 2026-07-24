import textwrap
from datetime import date
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from hotel.models import Inventario


def generar_contrato_pdf(request, response, contrato):
    inventario = Inventario.objects.filter(
        habitacion=contrato.habitacion)

    contexto = {"contrato": contrato, "inventario": inventario, "dia": timezone.localdate()}

    html_string = render_to_string(
        "hotel/contrato_pdf.html",
        contexto
    )

    HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf(response)

    return response




































