"""
Certificate Templates for Academic Authenticity Validator
Generates professional HTML certificates with QR codes and digital signatures
"""

import qrcode
import io
import base64
from typing import Dict, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import hashlib

class CertificateTemplates:
    """Generate various types of academic certificates"""
    
    @staticmethod
    def generate_digital_signature(certificate_data: str) -> str:
        """Generate a digital signature image for demonstration"""
        # Create signature hash
        signature_hash = hashlib.sha256(certificate_data.encode()).hexdigest()[:16].upper()
        
        # Create signature image
        img = Image.new('RGB', (400, 120), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw signature text (simulated handwritten style)
        try:
            # Try to use a cursive-like font if available
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 10)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw signature line
        draw.line([(20, 80), (380, 80)], fill='black', width=1)
        
        # Draw signature text (demo signature)
        draw.text((50, 30), "Authorized Signatory", fill='navy', font=font_large)
        draw.text((50, 85), f"Digital Signature: {signature_hash}", fill='gray', font=font_small)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        signature_b64 = base64.b64encode(buffer.getvalue()).decode()
        return signature_b64
    
    @staticmethod
    def generate_qr_code(data: str) -> str:
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def sslc_certificate(data: Dict[str, Any]) -> str:
        """Generate SSLC (10th Standard) Certificate"""
        qr_data = f"SSLC-{data.get('certificate_sl_no', '')}-{data.get('reg_no', '')}"
        qr_code = CertificateTemplates.generate_qr_code(qr_data)
        digital_signature = CertificateTemplates.generate_digital_signature(qr_data)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SSLC Certificate</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Merriweather:wght@300;400;700&family=Crimson+Text:wght@400;600&display=swap" rel="stylesheet">
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ 
            font-family: 'Merriweather', 'Georgia', serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        .certificate {{ 
            border: 12px double #2c5f8d; 
            border-image: linear-gradient(45deg, #2c5f8d, #1a3a5c) 1;
            padding: 50px; 
            width: 750px; 
            margin: auto; 
            background: linear-gradient(to bottom, #ffffff 0%, #f8f9fa 50%, #ffffff 100%);
            box-shadow: 0 10px 40px rgba(0,0,0,0.2), inset 0 0 30px rgba(44,95,141,0.05);
            position: relative;
            border-radius: 5px;
        }}
        .watermark {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            color: rgba(0,0,0,0.03);
            font-weight: bold;
            z-index: 0;
        }}
        .content {{ position: relative; z-index: 1; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 4px double #2c5f8d; 
            padding-bottom: 20px;
            background: linear-gradient(to bottom, rgba(44,95,141,0.05) 0%, transparent 100%);
            padding: 20px;
            border-radius: 5px;
        }}
        .header h2 {{ 
            font-family: 'Playfair Display', 'Georgia', serif;
            color: #1a3a5c; 
            margin: 8px 0; 
            font-size: 26px; 
            text-transform: uppercase; 
            font-weight: 700;
            letter-spacing: 2px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        .header h4 {{ 
            font-family: 'Crimson Text', serif;
            color: #2c5f8d; 
            margin: 12px 0; 
            font-size: 20px;
            font-weight: 600;
        }}
        .header p {{ 
            margin: 8px 0; 
            font-size: 14px; 
            color: #555;
            font-style: italic;
        }}
        .cert-number {{ 
            background: #2c5f8d; 
            color: white; 
            padding: 8px 15px; 
            display: inline-block; 
            border-radius: 5px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .section {{ margin-bottom: 20px; line-height: 1.8; }}
        .section strong {{ color: #1a3a5c; }}
        .subjects-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .subjects-table th {{ 
            background: #2c5f8d; 
            color: white; 
            padding: 12px; 
            text-align: center;
            font-size: 14px;
        }}
        .subjects-table td {{ 
            border: 1px solid #bbb; 
            padding: 10px; 
            text-align: center;
            background: white;
        }}
        .subjects-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .footer {{ 
            margin-top: 40px; 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-end;
            border-top: 2px solid #2c5f8d;
            padding-top: 20px;
        }}
        .signature-box {{
            text-align: center;
            width: 200px;
        }}
        .signature-line {{
            border-top: 2px solid #333;
            margin-top: 50px;
            padding-top: 5px;
            font-weight: bold;
            color: #1a3a5c;
        }}
        .seal {{
            width: 80px;
            height: 80px;
            border: 3px solid #c41e3a;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: #c41e3a;
            font-weight: bold;
            text-align: center;
            background: radial-gradient(circle, rgba(196,30,58,0.1) 0%, rgba(196,30,58,0.05) 100%);
        }}
        .qr-section {{
            position: absolute;
            bottom: 40px;
            right: 40px;
            text-align: center;
        }}
        .qr-section img {{ width: 80px; height: 80px; }}
        .qr-section p {{ font-size: 9px; margin: 5px 0; color: #666; }}
        .total-marks {{
            background: #ffd700;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            margin: 15px 0;
            border: 2px solid #daa520;
        }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="watermark">AUTHENTIC</div>
        <div class="content">
            <div class="header">
                <h2>🏛️ STATE BOARD OF SCHOOL EXAMINATIONS</h2>
                <h2>TAMIL NADU</h2>
                <div class="cert-number">Certificate S.No.: {data.get('certificate_sl_no', 'SSLC/2024/XXXXX')}</div>
                <h4>Secondary School Leaving Certificate (X Standard)</h4>
                <p><strong>Issued under the authority of the Government of Tamil Nadu</strong></p>
            </div>
            
            <div class="section">
                <strong>Name of Candidate:</strong> {data.get('candidate_name', '').upper()}<br>
                <strong>Father's Name:</strong> {data.get('father_name', '').upper()}<br>
                <strong>Mother's Name:</strong> {data.get('mother_name', '').upper()}<br>
                <strong>Date of Birth:</strong> {data.get('dob', '')}<br>
                <strong>Register Number:</strong> {data.get('reg_no', '')}<br>
                <strong>Month & Year of Examination:</strong> {data.get('exam_month_year', '')}<br>
                <strong>Roll Number:</strong> {data.get('roll_no', '')}
            </div>
            
            <div class="section">
                <table class="subjects-table">
                    <tr>
                        <th>Subject</th>
                        <th>Maximum Marks</th>
                        <th>Marks Obtained</th>
                        <th>Grade</th>
                    </tr>
                    <tr><td>TAMIL</td><td>100</td><td>{data.get('tamil_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('tamil_marks', 0)))}</td></tr>
                    <tr><td>ENGLISH</td><td>100</td><td>{data.get('english_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('english_marks', 0)))}</td></tr>
                    <tr><td>MATHEMATICS</td><td>100</td><td>{data.get('math_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('math_marks', 0)))}</td></tr>
                    <tr><td>SCIENCE</td><td>100</td><td>{data.get('science_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('science_marks', 0)))}</td></tr>
                    <tr><td>SOCIAL SCIENCE</td><td>100</td><td>{data.get('social_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('social_marks', 0)))}</td></tr>
                </table>
            </div>
            
            <div class="total-marks">
                <strong>TOTAL MARKS:</strong> {data.get('total_marks', '0')} / 500
            </div>
            
            <div class="section">
                <strong>School Name:</strong> {data.get('school_name', '')}<br>
                <strong>School Code:</strong> {data.get('school_code', '')}<br>
                <strong>Medium of Instruction:</strong> {data.get('medium', 'ENGLISH')}
            </div>
            
            <div class="footer">
                <div class="signature-box">
                    <p style="font-family: 'Brush Script MT', cursive; font-size: 24px; margin: 0; color: #1a3a5c;">{data.get('candidate_name', '')}</p>
                    <div class="signature-line">Candidate's Signature</div>
                </div>
                
                <div class="seal">
                    OFFICIAL<br>SEAL<br>TN BOARD
                </div>
                
                <div class="signature-box">
                    <img src="data:image/png;base64,{digital_signature}" alt="Digital Signature" style="max-width: 200px; margin-bottom: 5px;">
                    <div class="signature-line">Member Secretary<br>TN Board of Examinations</div>
                </div>
            </div>
            
            <div class="qr-section">
                <img src="data:image/png;base64,{qr_code}" alt="QR Code">
                <p>Scan to Verify</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    @staticmethod
    def get_grade(marks: int) -> str:
        """Calculate grade based on marks"""
        if marks >= 90: return 'A+'
        elif marks >= 80: return 'A'
        elif marks >= 70: return 'B+'
        elif marks >= 60: return 'B'
        elif marks >= 50: return 'C'
        elif marks >= 35: return 'D'
        else: return 'F'
    
    @staticmethod
    def hsc_first_year_certificate(data: Dict[str, Any]) -> str:
        """Generate Higher Secondary First Year Certificate"""
        qr_data = f"HSC1-{data.get('certificate_sl_no', '')}-{data.get('reg_no', '')}"
        qr_code = CertificateTemplates.generate_qr_code(qr_data)
        digital_signature = CertificateTemplates.generate_digital_signature(qr_data)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HS First Year Certificate</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Merriweather:wght@300;400;700&family=Crimson+Text:wght@400;600&display=swap" rel="stylesheet">
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ 
            font-family: 'Merriweather', 'Georgia', serif; 
            margin: 0; 
            padding: 40px;
            background: linear-gradient(135deg, #fef5f1 0%, #ffe4d6 100%);
        }}
        .certificate {{ 
            border: 8px double #c6716c; 
            padding: 40px; 
            width: 750px; 
            margin: auto; 
            background: linear-gradient(to bottom, #fefaf7 0%, #fdf5f0 100%);
            box-shadow: inset 0 0 20px rgba(198,113,108,0.1);
            position: relative;
        }}
        .watermark {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            color: rgba(198,113,108,0.03);
            font-weight: bold;
        }}
        .content {{ position: relative; z-index: 1; }}
        .header {{ text-align: center; margin-bottom: 25px; border-bottom: 3px solid #c6716c; padding-bottom: 15px; }}
        .header h2 {{ color: #8b4513; margin: 5px 0; font-size: 22px; }}
        .header h4 {{ color: #c6716c; margin: 10px 0; font-size: 18px; }}
        .cert-number {{ 
            background: #c6716c; 
            color: white; 
            padding: 8px 15px; 
            display: inline-block; 
            border-radius: 5px;
            font-weight: bold;
        }}
        .section {{ margin-bottom: 20px; line-height: 1.8; }}
        .section strong {{ color: #8b4513; }}
        .subjects-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .subjects-table th {{ background: #c6716c; color: white; padding: 12px; text-align: center; }}
        .subjects-table td {{ border: 1px solid #bbb; padding: 10px; text-align: center; background: white; }}
        .subjects-table tr:nth-child(even) {{ background: #fff5f0; }}
        .footer {{ margin-top: 40px; display: flex; justify-content: space-between; border-top: 2px solid #c6716c; padding-top: 20px; }}
        .signature-box {{ text-align: center; width: 200px; }}
        .signature-line {{ border-top: 2px solid #333; margin-top: 50px; padding-top: 5px; font-weight: bold; }}
        .seal {{ width: 80px; height: 80px; border: 3px solid #c6716c; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; background: radial-gradient(circle, rgba(198,113,108,0.1) 0%, rgba(198,113,108,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 40px; right: 40px; text-align: center; }}
        .qr-section img {{ width: 80px; height: 80px; }}
        .total-marks {{ background: #ffd700; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="watermark">AUTHENTIC</div>
        <div class="content">
            <div class="header">
                <h2>🏛️ STATE BOARD OF SCHOOL EXAMINATIONS, TAMIL NADU</h2>
                <div class="cert-number">Certificate S.No.: {data.get('certificate_sl_no', 'HSC1/2024/XXXXX')}</div>
                <h4>Higher Secondary Course - First Year Mark Certificate</h4>
                <p><strong>Issued under the authority of the Government of Tamil Nadu</strong></p>
            </div>
            
            <div class="section">
                <strong>Name of Candidate:</strong> {data.get('candidate_name', '').upper()}<br>
                <strong>Date of Birth:</strong> {data.get('dob', '')}<br>
                <strong>Permanent Register Number:</strong> {data.get('reg_no', '')}<br>
                <strong>Month & Year:</strong> {data.get('exam_month_year', '')}
            </div>
            
            <div class="section">
                <table class="subjects-table">
                    <tr>
                        <th>Subject</th>
                        <th>Maximum Marks</th>
                        <th>Marks Obtained</th>
                        <th>Grade</th>
                    </tr>
                    <tr><td>TAMIL</td><td>100</td><td>{data.get('tamil_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('tamil_marks', 0)))}</td></tr>
                    <tr><td>ENGLISH</td><td>100</td><td>{data.get('english_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('english_marks', 0)))}</td></tr>
                    <tr><td>PHYSICS</td><td>100</td><td>{data.get('physics_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('physics_marks', 0)))}</td></tr>
                    <tr><td>CHEMISTRY</td><td>100</td><td>{data.get('chemistry_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('chemistry_marks', 0)))}</td></tr>
                    <tr><td>BIOLOGY</td><td>100</td><td>{data.get('biology_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('biology_marks', 0)))}</td></tr>
                    <tr><td>MATHEMATICS</td><td>100</td><td>{data.get('math_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('math_marks', 0)))}</td></tr>
                </table>
            </div>
            
            <div class="total-marks">
                <strong>TOTAL MARKS:</strong> {data.get('total_marks', '0')} / 600
            </div>
            
            <div class="section">
                <strong>School Name:</strong> {data.get('school_name', '')}<br>
                <strong>Group Code & Name:</strong> {data.get('group_code_name', '')}<br>
                <strong>Medium of Instruction:</strong> {data.get('medium', 'ENGLISH')}
            </div>
            
            <div class="footer">
                <div class="signature-box">
                    <p style="font-family: 'Brush Script MT', cursive; font-size: 24px; margin: 0; color: #8b4513;">{data.get('candidate_name', '')}</p>
                    <div class="signature-line">Candidate's Signature</div>
                </div>
                <div class="seal">OFFICIAL<br>SEAL<br>TN BOARD</div>
                <div class="signature-box">
                    <img src="data:image/png;base64,{digital_signature}" alt="Digital Signature" style="max-width: 200px; margin-bottom: 5px;">
                    <div class="signature-line">Member Secretary</div>
                </div>
            </div>
            
            <div class="qr-section">
                <img src="data:image/png;base64,{qr_code}" alt="QR Code">
                <p style="font-size: 9px;">Scan to Verify</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    @staticmethod
    def hsc_second_year_certificate(data: Dict[str, Any]) -> str:
        """Generate Higher Secondary Second Year Certificate"""
        qr_data = f"HSC2-{data.get('certificate_sl_no', '')}-{data.get('reg_no', '')}"
        qr_code = CertificateTemplates.generate_qr_code(qr_data)
        digital_signature = CertificateTemplates.generate_digital_signature(qr_data)
        
        # Similar structure to first year but with blue theme
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HS Second Year Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: 'Times New Roman', serif; margin: 0; padding: 40px; }}
        .certificate {{ 
            border: 8px double #73B6E2; 
            padding: 40px; 
            width: 750px; 
            margin: auto; 
            background: linear-gradient(to bottom, #f4faff 0%, #e8f4ff 100%);
            box-shadow: inset 0 0 20px rgba(115,182,226,0.1);
            position: relative;
        }}
        .watermark {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 120px;
            color: rgba(115,182,226,0.03);
            font-weight: bold;
        }}
        .content {{ position: relative; z-index: 1; }}
        .header {{ text-align: center; margin-bottom: 25px; border-bottom: 3px solid #73B6E2; padding-bottom: 15px; }}
        .header h2 {{ color: #1e5a8e; margin: 5px 0; font-size: 22px; }}
        .header h4 {{ color: #73B6E2; margin: 10px 0; font-size: 18px; }}
        .cert-number {{ background: #73B6E2; color: white; padding: 8px 15px; display: inline-block; border-radius: 5px; font-weight: bold; }}
        .section {{ margin-bottom: 20px; line-height: 1.8; }}
        .section strong {{ color: #1e5a8e; }}
        .subjects-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .subjects-table th {{ background: #73B6E2; color: white; padding: 12px; text-align: center; }}
        .subjects-table td {{ border: 1px solid #bbb; padding: 10px; text-align: center; background: white; }}
        .subjects-table tr:nth-child(even) {{ background: #f0f8ff; }}
        .footer {{ margin-top: 40px; display: flex; justify-content: space-between; border-top: 2px solid #73B6E2; padding-top: 20px; }}
        .signature-box {{ text-align: center; width: 200px; }}
        .signature-line {{ border-top: 2px solid #333; margin-top: 50px; padding-top: 5px; font-weight: bold; }}
        .seal {{ width: 80px; height: 80px; border: 3px solid #73B6E2; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; background: radial-gradient(circle, rgba(115,182,226,0.1) 0%, rgba(115,182,226,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 40px; right: 40px; text-align: center; }}
        .qr-section img {{ width: 80px; height: 80px; }}
        .total-marks {{ background: #ffd700; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; margin: 15px 0; }}
        .result-box {{ background: #d4edda; border: 2px solid #28a745; padding: 15px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; color: #155724; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="watermark">AUTHENTIC</div>
        <div class="content">
            <div class="header">
                <h2>🏛️ STATE BOARD OF SCHOOL EXAMINATIONS, TAMIL NADU</h2>
                <div class="cert-number">Certificate S.No.: {data.get('certificate_sl_no', 'HSC2/2024/XXXXX')}</div>
                <h4>Higher Secondary Course - Second Year Mark Certificate</h4>
                <p><strong>Issued under the authority of the Government of Tamil Nadu</strong></p>
            </div>
            
            <div class="section">
                <strong>Name of Candidate:</strong> {data.get('candidate_name', '').upper()}<br>
                <strong>Date of Birth:</strong> {data.get('dob', '')}<br>
                <strong>Permanent Register Number:</strong> {data.get('reg_no', '')}<br>
                <strong>Month & Year:</strong> {data.get('exam_month_year', '')}
            </div>
            
            <div class="section">
                <table class="subjects-table">
                    <tr>
                        <th>Subject</th>
                        <th>Maximum Marks</th>
                        <th>Marks Obtained</th>
                        <th>Grade</th>
                    </tr>
                    <tr><td>TAMIL</td><td>100</td><td>{data.get('tamil_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('tamil_marks', 0)))}</td></tr>
                    <tr><td>ENGLISH</td><td>100</td><td>{data.get('english_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('english_marks', 0)))}</td></tr>
                    <tr><td>PHYSICS</td><td>100</td><td>{data.get('physics_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('physics_marks', 0)))}</td></tr>
                    <tr><td>CHEMISTRY</td><td>100</td><td>{data.get('chemistry_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('chemistry_marks', 0)))}</td></tr>
                    <tr><td>BIOLOGY</td><td>100</td><td>{data.get('biology_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('biology_marks', 0)))}</td></tr>
                    <tr><td>MATHEMATICS</td><td>100</td><td>{data.get('math_marks', '0')}</td><td>{CertificateTemplates.get_grade(int(data.get('math_marks', 0)))}</td></tr>
                </table>
            </div>
            
            <div class="total-marks">
                <strong>TOTAL MARKS:</strong> {data.get('total_marks', '0')} / 600
            </div>
            
            <div class="result-box">
                RESULT: {data.get('result', 'PASSED')}
            </div>
            
            <div class="section">
                <strong>School Name:</strong> {data.get('school_name', '')}<br>
                <strong>Group Code & Name:</strong> {data.get('group_code_name', '')}<br>
                <strong>Medium of Instruction:</strong> {data.get('medium', 'ENGLISH')}
            </div>
            
            <div class="footer">
                <div class="signature-box">
                    <p style="font-family: 'Brush Script MT', cursive; font-size: 24px; margin: 0; color: #1e5a8e;">{data.get('candidate_name', '')}</p>
                    <div class="signature-line">Candidate's Signature</div>
                </div>
                <div class="seal">OFFICIAL<br>SEAL<br>TN BOARD</div>
                <div class="signature-box">
                    <img src="data:image/png;base64,{digital_signature}" alt="Digital Signature" style="max-width: 200px; margin-bottom: 5px;">
                    <div class="signature-line">Member Secretary</div>
                </div>
            </div>
            
            <div class="qr-section">
                <img src="data:image/png;base64,{qr_code}" alt="QR Code">
                <p style="font-size: 9px;">Scan to Verify</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Initialize templates
certificate_templates = CertificateTemplates()
