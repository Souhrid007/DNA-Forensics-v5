from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src: str, context_dict: dict) -> bytes | None:
    """
    Render a Django template to PDF bytes using xhtml2pdf.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result)
    if not pdf.err:
        return result.getvalue()
    return None
