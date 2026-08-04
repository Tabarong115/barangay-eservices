"""Generate print-ready local-pilot certificates for the Barangay e-Services Portal."""

from pathlib import Path
from urllib.request import urlopen
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

NAVY = colors.HexColor("#12335B")
GOLD = colors.HexColor("#D4A72C")
INK = colors.HexColor("#1F2937")
PAGE_WIDTH, PAGE_HEIGHT = A4


def _load_image(image_source):
    """Load an image from a file path or URL for certificate generation."""
    if isinstance(image_source, str) and (image_source.startswith("http://") or image_source.startswith("https://")):
        # Load from URL (Supabase Storage)
        try:
            response = urlopen(image_source)
            image_data = BytesIO(response.read())
            return ImageReader(image_data)
        except Exception as e:
            print(f"Error loading image from URL: {e}")
            return None
    else:
        # Load from local file path
        try:
            image_path = Path(image_source)
            if image_path.exists():
                return ImageReader(str(image_path))
        except Exception as e:
            print(f"Error loading local image: {e}")
            return None
    return None


def _paragraph(pdf, text, x, y, width, style):
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, y - height)
    return y - height


def generate_barangay_clearance(request_data, output_path):
    """Create a formal Barangay Clearance PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Barangay Clearance - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "BARANGAY CLEARANCE")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 124 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar. This Barangay Clearance is issued upon the request of "
            "the above-named person for <b>{purpose}</b>, for any lawful purpose it may serve.").format(**request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path


def generate_barangay_certification(request_data, output_path):
    """Create a formal Barangay Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Barangay Certification - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "BARANGAY CERTIFICATION")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 124 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar. This Barangay Certification is issued upon the request of "
            "the above-named person for <b>{purpose}</b>, for any lawful purpose it may serve.").format(**request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path


def generate_certificate_of_residency(request_data, output_path):
    """Create a Certificate of Residency PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Certificate of Residency - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "CERTIFICATE OF RESIDENCY")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 124 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    
    residency_text = f"{request_data.get('residency_years', '0')} year(s) and {request_data.get('residency_months', '0')} month(s)"
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a bona fide resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, having resided at the above address for <b>{}</b>. "
            "This Certificate of Residency is issued upon the request of the above-named person for <b>{purpose}</b>, "
            "for any lawful purpose it may serve.").format(residency_text, **request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path


def generate_certificate_of_indigency(request_data, output_path):
    """Create a Certificate of Indigency PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Certificate of Indigency - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "CERTIFICATE OF INDIGENCY")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 124 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    
    family_info = f"with a family size of {request_data.get('family_size', '0')} and a monthly household income of ₱{request_data.get('monthly_income', '0')}"
    purpose = request_data.get("purpose") or "any lawful purpose"
    template_data = dict(request_data)
    template_data["purpose"] = purpose
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, {family_info}. This Certificate of Indigency is issued upon the request of "
            "the above-named person for <b>{purpose}</b>, for any lawful purpose it may serve.").format(
                family_info=family_info, **template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path


def generate_business_closure_certification(request_data, output_path):
    """Create a Business Closure Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Business Closure Certification - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "BUSINESS CLOSURE CERTIFICATION")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 124 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    
    closure_date = request_data.get("closure_date", "")
    if closure_date:
        try:
            from datetime import datetime
            closure_date = datetime.strptime(closure_date, "%Y-%m-%d").strftime("%B %d, %Y")
        except:
            pass
    
    text = ("This is to certify that the business known as <b>{business_name}</b>, located at <b>{business_address}</b>, "
            "operated as a <b>{business_type}</b> under the ownership of <b>{owner_name}</b>, "
            "has officially closed its operations effective <b>{closure_date}</b>. "
            "The reason for closure is stated as: <b>{reason}</b>. "
            "This Business Closure Certification is issued upon the request of the business owner.").format(
                closure_date=closure_date, **request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path


def generate_first_time_job_seeker_certification(request_data, output_path):
    """Create a First Time Job Seeker Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"First Time Job Seeker Certification - {request_data['certificate_number']}")
    margin = 22 * mm
    content_width = PAGE_WIDTH - 2 * margin
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(1.3)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)

    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
            pass
    else:
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 13 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(1.5)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 52 * mm, 10.5 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 56 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8.5)
    for offset, text in [(75, "REPUBLIC OF THE PHILIPPINES"), (80, "Province of Eastern Samar"), (85, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 97 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 97 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 112 * mm, "FIRST TIME JOB SEEKER CERTIFICATION")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 118 * mm, f"Certificate No. {request_data['certificate_number']}")
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 123 * mm, "(Under Republic Act No. 11261 - First Time Jobseekers Assistance Act)")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER)
    y = PAGE_HEIGHT - 129 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 11 * mm
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, and is a first-time job seeker. This certification is issued "
            "in accordance with Republic Act No. 11261 (First Time Jobseekers Assistance Act), which entitles the bearer "
            "to fee waivers for government-issued documents required for employment. The bearer has signed an Oath of Undertaking "
            "declaring that this is their first employment and that the documents obtained will be used for employment purposes only.").format(**request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 9 * mm
    _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    signature_y = 72 * mm
    signature_x = PAGE_WIDTH - margin - 55 * mm
    pdf.setStrokeColor(INK)
    pdf.setLineWidth(0.7)
    pdf.line(signature_x, signature_y, PAGE_WIDTH - margin, signature_y)
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, signature_x, signature_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 5 * mm, "PUNONG BARANGAY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(signature_x + 27.5 * mm, signature_y - 9 * mm, "Signature over printed name")
    secretary_y = 43 * mm
    pdf.line(margin, secretary_y, margin + 55 * mm, secretary_y)
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, margin, secretary_y + 2 * mm, width=45 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 5 * mm, "BARANGAY SECRETARY")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(margin + 27.5 * mm, secretary_y - 9 * mm, "Attested by")
    pdf.setStrokeColor(GOLD)
    pdf.line(margin, 27 * mm, PAGE_WIDTH - margin, 27 * mm)
    pdf.setFillColor(colors.HexColor("#4B5563"))
    pdf.setFont("Helvetica", 6.8)
    pdf.drawString(margin, 21 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    control = f"Control No. {request_data['certificate_number']}"
    pdf.drawString(PAGE_WIDTH - margin - stringWidth(control, "Helvetica", 6.8), 21 * mm, control)
    pdf.drawCentredString(PAGE_WIDTH / 2, 16 * mm, "QR verification will be added in the next Version 1 step.")
    pdf.save()
    return output_path
