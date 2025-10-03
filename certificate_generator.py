"""
Certificate Generator with QR Codes and PDF Export
Essential feature for Academic Authenticity Validator
"""

import qrcode
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
from typing import Dict, Any, Optional

class CertificateGenerator:
    """Generate certificates with QR codes and PDF export"""
    
    def __init__(self):
        self.output_dir = "generated_certificates"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_qr_code(self, verification_code: str, verification_url: str = None) -> str:
        """Generate QR code for certificate verification"""
        if not verification_url:
            verification_url = f"http://localhost:5000/?verify={verification_code}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_base64
    
    def generate_certificate_pdf(self, certificate_data: Dict[str, Any], verification_code: str) -> str:
        """Generate a professional PDF certificate"""
        filename = f"certificate_{verification_code}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Safely get values with proper null handling
        student_name = certificate_data.get('student_name', 'N/A') or 'N/A'
        student_id = certificate_data.get('student_id', 'N/A') or 'N/A'
        institution_name = certificate_data.get('institution_name', 'N/A') or 'N/A'
        degree_type = certificate_data.get('degree_type', 'N/A') or 'N/A'
        field_of_study = certificate_data.get('field_of_study', 'N/A') or 'N/A'
        graduation_date = certificate_data.get('graduation_date', 'N/A') or 'N/A'
        issue_date = certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d')) or datetime.now().strftime('%Y-%m-%d')
        certificate_id = certificate_data.get('certificate_id', 'N/A') or 'N/A'
        blockchain_hash = certificate_data.get('blockchain_hash', 'N/A') or 'N/A'
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1e3a8a')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#3b82f6')
        )
        
        content_style = ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Header
        story.append(Paragraph("🎓 ACADEMIC AUTHENTICITY VALIDATOR", title_style))
        story.append(Paragraph("Certificate of Academic Achievement", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Certificate content
        story.append(Paragraph("This is to certify that", content_style))
        story.append(Spacer(1, 10))
        
        # Student name (highlighted)
        name_style = ParagraphStyle(
            'StudentName',
            parent=styles['Normal'],
            fontSize=20,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor('#dc2626'),
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"<b>{student_name}</b>", name_style))
        
        # Degree information
        story.append(Paragraph("has successfully completed", content_style))
        story.append(Spacer(1, 10))
        
        degree_style = ParagraphStyle(
            'DegreeInfo',
            parent=styles['Normal'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor('#059669'),
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"<b>{degree_type}</b>", degree_style))
        if field_of_study != 'N/A':
            story.append(Paragraph(f"in <b>{field_of_study}</b>", degree_style))
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("from", content_style))
        story.append(Spacer(1, 10))
        
        # Institution name
        institution_style = ParagraphStyle(
            'InstitutionName',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#7c3aed'),
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"<b>{institution_name}</b>", institution_style))
        
        # Dates
        story.append(Spacer(1, 20))
        date_info = [
            ['Graduation Date:', graduation_date],
            ['Issue Date:', issue_date],
            ['Student ID:', student_id],
            ['Certificate ID:', certificate_id]
        ]
        
        date_table = Table(date_info, colWidths=[2*inch, 3*inch])
        date_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(date_table)
        
        # QR Code section
        story.append(Spacer(1, 30))
        story.append(Paragraph("🔗 Blockchain Verification", subtitle_style))
        
        # Generate QR code
        qr_base64 = self.generate_qr_code(verification_code)
        qr_data = base64.b64decode(qr_base64)
        qr_image = Image(io.BytesIO(qr_data), width=1.5*inch, height=1.5*inch)
        
        # QR code table
        blockchain_display = blockchain_hash[:32] + "..." if blockchain_hash != 'N/A' else 'Pending'
        qr_info = [
            [qr_image, f"Verification Code: {verification_code}\n\nScan QR code or visit:\nlocalhost:5000/?verify={verification_code}\n\nBlockchain Hash:\n{blockchain_display}"]
        ]
        
        qr_table = Table(qr_info, colWidths=[2*inch, 4*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (1, 0), (1, 0), 9),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
        ]))
        story.append(qr_table)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#6b7280')
        )
        story.append(Paragraph("This certificate is secured by blockchain technology", footer_style))
        story.append(Paragraph("Smart India Hackathon 2024 - Academic Authenticity Validator", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_certificate_html(self, certificate_data: Dict[str, Any], verification_code: str) -> str:
        """Generate HTML certificate for web display with professional design"""
        qr_base64 = self.generate_qr_code(verification_code)
        
        # Safely get values with proper null handling
        student_name = certificate_data.get('student_name', 'N/A') or 'N/A'
        student_id = certificate_data.get('student_id', 'N/A') or 'N/A'
        institution_name = certificate_data.get('institution_name', 'N/A') or 'N/A'
        degree_type = certificate_data.get('degree_type', 'N/A') or 'N/A'
        field_of_study = certificate_data.get('field_of_study', 'N/A') or 'N/A'
        graduation_date = certificate_data.get('graduation_date', 'N/A') or 'N/A'
        issue_date = certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d')) or datetime.now().strftime('%Y-%m-%d')
        certificate_id = certificate_data.get('certificate_id', 'N/A') or 'N/A'
        blockchain_hash = certificate_data.get('blockchain_hash', 'N/A') or 'N/A'
        
        # Generate certificate number
        cert_number = f"CERT/{datetime.now().year}/{certificate_id[-6:]}"
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Academic Certificate - {student_name}</title>
            <style>
                body {{
                    background: #f4f2ec;
                    font-family: "Georgia", serif;
                    margin: 0;
                    padding: 30px;
                }}
                .certificate {{
                    width: 1000px;
                    height: auto;
                    padding: 60px;
                    margin: auto;
                    border: 12px solid #c9a94a;
                    background: #fff;
                    box-shadow: 0 0 20px rgba(0,0,0,0.2);
                    text-align: center;
                    position: relative;
                }}
                .certificate h1 {{
                    font-size: 40px;
                    margin: 10px 0;
                    text-transform: uppercase;
                    color: #a88423;
                    letter-spacing: 2px;
                }}
                .college-name {{
                    font-size: 26px;
                    font-weight: bold;
                    color: #333;
                }}
                .subtitle {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                }}
                .cert-number {{
                    font-size: 16px;
                    color: #888;
                    margin-bottom: 20px;
                }}
                .content {{
                    margin: 40px 70px;
                    font-size: 20px;
                    line-height: 1.8;
                    color: #222;
                    text-align: justify;
                }}
                .highlight {{
                    color: #a88423;
                    font-weight: bold;
                }}
                .date-place {{
                    margin-top: 40px;
                    font-size: 18px;
                    display: flex;
                    justify-content: space-between;
                    padding: 0 100px;
                }}
                .signatures {{
                    display: flex;
                    justify-content: space-around;
                    margin-top: 70px;
                }}
                .sign-box {{
                    text-align: center;
                    font-size: 16px;
                }}
                .sign-line {{
                    border-top: 2px solid #444;
                    width: 220px;
                    margin: 0 auto 8px auto;
                }}
                .seal {{
                    position: absolute;
                    bottom: 160px;
                    left: 50%;
                    transform: translateX(-50%);
                    font-size: 16px;
                    border: 4px solid #a88423;
                    border-radius: 50%;
                    width: 140px;
                    height: 140px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-weight: bold;
                    color: #a88423;
                    background: rgba(249, 244, 228, 0.8);
                }}
                .qr-section {{
                    position: absolute;
                    top: 60px;
                    right: 60px;
                    text-align: center;
                }}
                .qr-code {{
                    width: 100px;
                    height: 100px;
                    border: 2px solid #c9a94a;
                    padding: 5px;
                    background: white;
                }}
                .blockchain-info {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                    background: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                }}
                @media print {{
                    body {{ background: white; }}
                    .certificate {{ box-shadow: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="certificate">
                <!-- QR Code Section -->
                <div class="qr-section">
                    <img src="data:image/png;base64,{qr_base64}" alt="QR Code" class="qr-code">
                    <div style="font-size: 10px; margin-top: 5px; color: #666;">Scan to Verify</div>
                </div>

                <!-- Header -->
                <div class="college-name">{institution_name}</div>
                <div class="subtitle">(Affiliated to Anna University)</div>
                
                <h1>Certificate of Completion</h1>
                
                <div class="cert-number">Certificate No: {cert_number}</div>

                <!-- Main Content -->
                <div class="content">
                    This is to certify that <span class="highlight">{student_name}</span>, 
                    Roll No. <span class="highlight">{student_id}</span>, has successfully completed 
                    the <span class="highlight">{degree_type}</span> 
                    {f'in <span class="highlight">{field_of_study}</span>' if field_of_study != 'N/A' else ''} 
                    during the academic year <span class="highlight">2021–2025</span> at 
                    <span class="highlight">{institution_name}</span>.
                </div>

                <!-- Date and Place -->
                <div class="date-place">
                    <div>Date: {issue_date}</div>
                    <div>Place: Chennai</div>
                </div>

                <!-- Signatures -->
                <div class="signatures">
                    <div class="sign-box">
                        <div class="sign-line"></div>
                        <p>Head of Department</p>
                    </div>
                    <div class="sign-box">
                        <div class="sign-line"></div>
                        <p>Principal / Dean</p>
                    </div>
                    <div class="sign-box">
                        <div class="sign-line"></div>
                        <p>Registrar / COE</p>
                    </div>
                </div>

                <!-- Official Seal -->
                <div class="seal">Official<br>Seal</div>
                
                <!-- Blockchain Info -->
                <div class="blockchain-info">
                    <strong>Blockchain Verification:</strong><br>
                    Verification Code: {verification_code}<br>
                    Blockchain Hash: {blockchain_hash[:32] if blockchain_hash != 'N/A' else 'Pending'}...<br>
                    Certificate ID: {certificate_id}<br>
                    <em>This certificate is secured by blockchain technology - Smart India Hackathon 2024</em>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template

# Global certificate generator instance
certificate_generator = CertificateGenerator()
