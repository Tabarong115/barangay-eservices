"""Generate print-ready local-pilot certificates for the Barangay e-Services Portal."""

from pathlib import Path
from urllib.request import urlopen
from io import BytesIO

import qrcode

from config import Config
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


def _generate_qr_code(certificate_number, tracking_number=None):
    """Generate a QR code image for certificate verification."""
    # Create verification URL with certificate number
    verify_data = f"cert={certificate_number}"
    if tracking_number:
        verify_data += f"&track={tracking_number}"
    
    # Get base URL from config for QR code generation
    config = Config()
    base_url = config.BASE_URL.rstrip('/')
    full_url = f"{base_url}/verify?{verify_data}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(full_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="#12335B", back_color="white")
    
    # Convert to BytesIO for ReportLab
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    return ImageReader(qr_buffer)


def _paragraph(pdf, text, x, y, width, style):
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, y - height)
    return y - height


def _add_enhanced_border(pdf):
    """Add professional double border with gold accent."""
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(2.5)
    pdf.rect(10 * mm, 10 * mm, PAGE_WIDTH - 20 * mm, PAGE_HEIGHT - 20 * mm, stroke=1, fill=0)
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1)
    pdf.rect(12 * mm, 12 * mm, PAGE_WIDTH - 24 * mm, PAGE_HEIGHT - 24 * mm, stroke=1, fill=0)
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(0.5)
    pdf.rect(13 * mm, 13 * mm, PAGE_WIDTH - 26 * mm, PAGE_HEIGHT - 26 * mm, stroke=1, fill=0)


def _add_watermark_background(pdf):
    """Add subtle watermark background."""
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.rect(14 * mm, 14 * mm, PAGE_WIDTH - 28 * mm, PAGE_HEIGHT - 28 * mm, stroke=0, fill=1)


def _add_enhanced_header(pdf, request_data, margin, title):
    """Add professional header with logo and government info."""
    if request_data.get("logo_path"):
        image_reader = _load_image(request_data["logo_path"])
        if image_reader:
            logo_width = 45 * mm
            logo_height = 45 * mm
            logo_x = (PAGE_WIDTH - logo_width) / 2
            logo_y = PAGE_HEIGHT - 65 * mm
            pdf.drawImage(image_reader, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask="auto")
    else:
        # Enhanced default logo design
        pdf.setFillColor(NAVY)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 50 * mm, 14 * mm, fill=1, stroke=0)
        pdf.setStrokeColor(GOLD)
        pdf.setLineWidth(2)
        pdf.circle(PAGE_WIDTH / 2, PAGE_HEIGHT - 50 * mm, 11 * mm, fill=0, stroke=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 54 * mm, "B7")

    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 72 * mm, "REPUBLIC OF THE PHILIPPINES")
    pdf.setFont("Helvetica", 9)
    for offset, text in [(78, "Province of Eastern Samar"), (84, "Municipality of Salcedo")]:
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - offset * mm, text)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(NAVY)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 92 * mm, "BARANGAY 7, POBLACION")
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(2)
    pdf.line(margin, PAGE_HEIGHT - 98 * mm, PAGE_WIDTH - margin, PAGE_HEIGHT - 98 * mm)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 115 * mm, title)


def _add_enhanced_footer(pdf, request_data, margin):
    """Add professional footer with signatures and QR code."""
    # Punong Barangay signature section (right side)
    pb_y = 80 * mm
    pb_x = PAGE_WIDTH - margin - 55 * mm
    
    # 1. "Approved by" text
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(pb_x + 27.5 * mm, pb_y, "Approved by")
    
    # 2. Signature image (if available) - positioned to overlap printed name for authentic look
    if request_data.get("punong_barangay_signature_path"):
        image_reader = _load_image(request_data["punong_barangay_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, pb_x + 2.5 * mm, pb_y - 17 * mm, width=50 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    
    # 3. Printed Name
    pdf.setFont("Helvetica-Bold", 10)
    punong_name = request_data.get("punong_barangay_name", "")
    if punong_name:
        pdf.drawCentredString(pb_x + 27.5 * mm, pb_y - 20 * mm, punong_name)
    else:
        pdf.drawCentredString(pb_x + 27.5 * mm, pb_y - 20 * mm, "_____________________")
    
    # 4. Short Line
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(0.8)
    pdf.line(pb_x + 2.5 * mm, pb_y - 24 * mm, pb_x + 52.5 * mm, pb_y - 24 * mm)
    
    # 5. Position
    pdf.setFont("Helvetica", 8.5)
    pdf.drawCentredString(pb_x + 27.5 * mm, pb_y - 28 * mm, "Punong Barangay")
    
    # Secretary signature section (left side)
    sec_y = 80 * mm
    sec_x = margin
    
    # 1. "Attested by" text
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(sec_x + 27.5 * mm, sec_y, "Attested by")
    
    # 2. Signature image (if available) - positioned to overlap printed name for authentic look
    if request_data.get("secretary_signature_path"):
        image_reader = _load_image(request_data["secretary_signature_path"])
        if image_reader:
            pdf.drawImage(image_reader, sec_x + 2.5 * mm, sec_y - 19 * mm, width=50 * mm, height=18 * mm, preserveAspectRatio=True, mask="auto")
    
    # 3. Printed Name
    pdf.setFont("Helvetica-Bold", 10)
    secretary_name = request_data.get("secretary_name", "")
    if secretary_name:
        pdf.drawCentredString(sec_x + 27.5 * mm, sec_y - 20 * mm, secretary_name)
    else:
        pdf.drawCentredString(sec_x + 27.5 * mm, sec_y - 20 * mm, "_____________________")
    
    # 4. Short Line
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(0.8)
    pdf.line(sec_x + 2.5 * mm, sec_y - 22 * mm, sec_x + 52.5 * mm, sec_y - 22 * mm)
    
    # 5. Position
    pdf.setFont("Helvetica", 8.5)
    pdf.drawCentredString(sec_x + 27.5 * mm, sec_y - 26 * mm, "Barangay Secretary")
    
    # Enhanced footer design
    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.5)
    pdf.line(margin, 32 * mm, PAGE_WIDTH - margin, 32 * mm)
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 7)
    pdf.drawString(margin, 26 * mm, "Generated by Barangay 7 e-Services Portal - Local Pilot")
    
    # Add QR code for verification (positioned in bottom right corner)
    qr_code = _generate_qr_code(request_data['certificate_number'], request_data.get('tracking_number'))
    if qr_code:
        qr_size = 22 * mm
        qr_x = PAGE_WIDTH - margin - qr_size - 5 * mm
        qr_y = 35 * mm  # Positioned above footer line
        pdf.drawImage(qr_code, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask="auto")
        
        # Add QR code label
        pdf.setFillColor(colors.HexColor("#9CA3AF"))
        pdf.setFont("Helvetica", 6)
        pdf.drawCentredString(qr_x + qr_size / 2, qr_y - 2.5 * mm, "Scan to verify")
    else:
        # Fallback if QR code generation fails
        pdf.setFillColor(colors.HexColor("#9CA3AF"))
        pdf.setFont("Helvetica", 6.5)
        pdf.drawCentredString(PAGE_WIDTH / 2, 20 * mm, "QR verification available")


def generate_barangay_clearance(request_data, output_path):
    """Create a formal Barangay Clearance PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Barangay Clearance - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "BARANGAY CLEARANCE")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 133 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    purpose = request_data.get("purpose", "any lawful purpose it may serve")
    template_data = dict(request_data)
    template_data["purpose"] = purpose
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar. This Barangay Clearance is issued upon the request of "
            "the above-named person for <b>{purpose}</b>.").format(**template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path


def generate_barangay_certification(request_data, output_path):
    """Create a formal Barangay Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Barangay Certification - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "BARANGAY CERTIFICATION")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 133 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    purpose = request_data.get("purpose", "any lawful purpose it may serve")
    template_data = dict(request_data)
    template_data["purpose"] = purpose
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar. This Barangay Certification is issued upon the request of "
            "the above-named person for <b>{purpose}</b>.").format(**template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path


def generate_certificate_of_residency(request_data, output_path):
    """Create a Certificate of Residency PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Certificate of Residency - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "CERTIFICATE OF RESIDENCY")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 133 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    # Support both field naming conventions for compatibility
    years = request_data.get('years_resided') or request_data.get('residency_years', '0')
    months = request_data.get('months_resided') or request_data.get('residency_months', '0')
    residency_text = f"{years} year(s) and {months} month(s)"
    purpose = request_data.get("purpose", "any lawful purpose it may serve")
    template_data = dict(request_data)
    template_data["purpose"] = purpose
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a bona fide resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, having resided at the above address for <b>{}</b>. "
            "This Certificate of Residency is issued upon the request of the above-named person for <b>{purpose}</b>.").format(residency_text, **template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path


def generate_certificate_of_indigency(request_data, output_path):
    """Create a Certificate of Indigency PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Certificate of Indigency - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "CERTIFICATE OF INDIGENCY")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 133 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    family_info = f"with a family size of {request_data.get('family_size', '0')} and a monthly household income of ₱{request_data.get('monthly_income', '0')}"
    purpose = request_data.get("purpose", "any lawful purpose it may serve")
    template_data = dict(request_data)
    template_data["purpose"] = purpose
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, {family_info}. This Certificate of Indigency is issued upon the request of "
            "the above-named person for <b>{purpose}</b>.").format(
                family_info=family_info, **template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path


def generate_business_closure_certification(request_data, output_path):
    """Create a Business Closure Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"Business Closure Certification - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "BUSINESS CLOSURE CERTIFICATION")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=20, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 133 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    closure_date = request_data.get("closure_date", "")
    if closure_date:
        try:
            from datetime import datetime
            closure_date = datetime.strptime(closure_date, "%Y-%m-%d").strftime("%B %d, %Y")
        except:
            pass
    
    template_data = dict(request_data)
    template_data["closure_date"] = closure_date
    text = ("This is to certify that the business known as <b>{business_name}</b>, located at <b>{business_address}</b>, "
            "operated as a <b>{business_type}</b> under the ownership of <b>{owner_name}</b>, "
            "has officially closed its operations effective <b>{closure_date}</b>. "
            "The reason for closure is stated as: <b>{reason}</b>. "
            "This Business Closure Certification is issued upon the request of the business owner.").format(**template_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path


def generate_first_time_job_seeker_certification(request_data, output_path):
    """Create a First Time Job Seeker Certification PDF from an approved pilot request."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle(f"First Time Job Seeker Certification - {request_data['certificate_number']}")
    margin = 20 * mm
    content_width = PAGE_WIDTH - 2 * margin
    
    # Apply enhanced design elements
    _add_enhanced_border(pdf)
    _add_watermark_background(pdf)
    _add_enhanced_header(pdf, request_data, margin, "FIRST TIME JOB SEEKER CERTIFICATION")
    
    pdf.setFillColor(colors.HexColor("#6B7280"))
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 125 * mm, f"Certificate No. {request_data['certificate_number']}")
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 132 * mm, "(Under Republic Act No. 11261 - First Time Jobseekers Assistance Act)")
    
    styles = getSampleStyleSheet()
    body = ParagraphStyle("CertificateBody", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=18, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6)
    heading = ParagraphStyle("CertificateHeading", parent=body, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=8)
    y = PAGE_HEIGHT - 140 * mm
    y = _paragraph(pdf, "<b>TO WHOM IT MAY CONCERN:</b>", margin, y, content_width, heading) - 6 * mm
    
    text = ("This is to certify that <b>{full_name}</b>, of <b>{address}</b>, is a resident of Barangay 7, "
            "Poblacion, Salcedo, Eastern Samar, and is a first-time job seeker. This certification is issued "
            "in accordance with Republic Act No. 11261 (First Time Jobseekers Assistance Act), which entitles the bearer "
            "to fee waivers for government-issued documents required for employment. The bearer has signed an Oath of Undertaking "
            "declaring that this is their first employment and that the documents obtained will be used for employment purposes only.").format(**request_data)
    y = _paragraph(pdf, text, margin, y, content_width, body) - 6 * mm
    y = _paragraph(pdf, "Issued this <b>{}</b> at Barangay 7, Poblacion, Salcedo, Eastern Samar, Philippines.".format(request_data["issued_at"].strftime("%d day of %B %Y")), margin, y, content_width, body)
    
    _add_enhanced_footer(pdf, request_data, margin)
    pdf.save()
    return output_path
