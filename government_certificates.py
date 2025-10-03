"""
Government Certificate Templates
Income, Community, Nativity, Transfer, and First Graduate Certificates
"""

from datetime import datetime
import qrcode
import io
import base64
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
import hashlib

class GovernmentCertificates:
    """Generate various government certificates"""
    
    @staticmethod
    def generate_digital_signature(certificate_data: str) -> str:
        """Generate a digital signature image for demonstration"""
        signature_hash = hashlib.sha256(certificate_data.encode()).hexdigest()[:16].upper()
        img = Image.new('RGB', (400, 120), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 10)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        draw.line([(20, 80), (380, 80)], fill='black', width=1)
        draw.text((50, 30), "Authorized Signatory", fill='navy', font=font_large)
        draw.text((50, 85), f"Digital Signature: {signature_hash}", fill='gray', font=font_small)
        
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
    def income_certificate(data: Dict[str, Any]) -> str:
        """Generate Income Certificate"""
        qr_data = f"INCOME-{data.get('certificate_no', '')}-{data.get('applicant_name', '')}"
        qr_code = GovernmentCertificates.generate_qr_code(qr_data)
        
        family_rows = ""
        for idx, member in enumerate(data.get('family_members', []), 1):
            family_rows += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{member.get('name', '')}</td>
                    <td>{member.get('relationship', '')}</td>
                    <td>{member.get('occupation', '')}</td>
                    <td>₹ {member.get('income', '0')}</td>
                </tr>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Income Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: Arial, 'Noto Sans Tamil', sans-serif; background: #f7f9fc; padding: 44px; }}
        .certificate-box {{ 
            border: 3px solid #232e3b; 
            padding: 35px; 
            max-width: 860px; 
            margin: auto; 
            background: #fff; 
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
            position: relative;
        }}
        .govt-emblem {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #1e3a8a;
        }}
        .govt-emblem h3 {{ color: #1e3a8a; margin: 5px 0; font-size: 20px; }}
        .cert-header {{ display: flex; align-items: center; gap: 23px; margin-bottom: 13px; }}
        .cert-title {{ text-align: center; font-size: 1.67em; color: #253667; font-weight: bold; margin: 15px 0; }}
        .profile-photo {{ width: 58px; margin-left: auto; border: 2px solid #1e3a8a; background: #ececec; }}
        .cert-details {{ font-size: 1.15em; color: #222b39; margin-bottom: 13px; background: #f0f4f8; padding: 10px; border-left: 4px solid #1e3a8a; }}
        .main-text {{ font-size: 1.09em; color: #333; margin-bottom: 14px; line-height: 1.8; }}
        .table-label {{ font-size: 1.04em; color: #2b4b7c; font-weight: bold; margin: 11px 0 6px 0; }}
        table.info-table {{ border-collapse: collapse; width: 100%; margin-bottom: 19px; }}
        table.info-table th, table.info-table td {{ border: 1px solid #aaa; padding: 10px 8px; text-align: left; font-size: 0.98em; }}
        table.info-table th {{ background: #1e3a8a; color: white; text-align: center; }}
        table.info-table tr:nth-child(even) {{ background: #f9fafb; }}
        .total-income {{ background: #fef3c7; border: 2px solid #f59e0b; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 16px; text-align: center; margin: 20px 0; }}
        .remarks {{ font-size: 1em; color: #555; margin-top: 8px; background: #fef3c7; padding: 10px; border-radius: 5px; }}
        .sign-section {{ margin-top: 33px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .sign-box {{ text-align: center; }}
        .sign-label {{ font-weight: bold; color: #171a1b; font-size: 1em; margin-top: 50px; border-top: 2px solid #333; padding-top: 5px; }}
        .official-seal {{ width: 90px; height: 90px; border: 3px solid #dc2626; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; text-align: center; color: #dc2626; background: radial-gradient(circle, rgba(220,38,38,0.1) 0%, rgba(220,38,38,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 35px; right: 35px; text-align: center; }}
        .qr-img {{ width: 81px; height: 81px; }}
        .cert-footer {{ color: #555; font-size: 0.85em; margin-top: 5px; }}
    </style>
</head>
<body>
<div class="certificate-box">
    <div class="govt-emblem">
        <h3>🏛️ GOVERNMENT OF TAMIL NADU</h3>
        <h3>REVENUE DEPARTMENT</h3>
    </div>
    
    <div class="cert-title">INCOME CERTIFICATE</div>

    <div class="cert-details">
        <strong>Certificate No:</strong> {data.get('certificate_no', 'INC/2024/XXXXX')}<br>
        <strong>Date of Issue:</strong> {data.get('issue_date', datetime.now().strftime('%d/%m/%Y'))}
    </div>

    <div class="main-text">
        This is to certify that <b>{data.get('applicant_name', '').upper()}</b>, 
        son/daughter of <b>{data.get('parent_name', '').upper()}</b>, 
        residing at <b>{data.get('address', '')}</b>, 
        Taluk: <b>{data.get('taluk', '')}</b>, 
        District: <b>{data.get('district', '')}</b>, 
        State: <b>Tamil Nadu</b>.
    </div>

    <div class="table-label">Family Income Details:</div>
    <table class="info-table">
        <tr>
            <th>Sl. No</th>
            <th>Name of Family Member</th>
            <th>Relationship</th>
            <th>Occupation/Source</th>
            <th>Annual Income (₹)</th>
        </tr>
        {family_rows}
    </table>

    <div class="total-income">
        TOTAL ANNUAL FAMILY INCOME: ₹ {data.get('total_income', '0')}/-
    </div>

    <div class="remarks">
        <strong>Purpose:</strong> {data.get('purpose', 'Educational/Scholarship purposes')}<br>
        <strong>Validity:</strong> This certificate is valid for one year from the date of issue.<br>
        This certificate is digitally signed and does not require any seal or handwritten signature.
    </div>

    <div class="sign-section">
        <div class="official-seal">
            OFFICIAL<br>SEAL<br>REVENUE<br>DEPT
        </div>
        
        <div class="sign-box">
            <div class="sign-label">
                Tahsildar<br>
                {data.get('taluk', 'Taluk')} Taluk<br>
                {data.get('district', 'District')} District
            </div>
        </div>
    </div>

    <div class="qr-section">
        <img src="data:image/png;base64,{qr_code}" class="qr-img" alt="QR Code" />
        <div class="cert-footer">Scan to Verify</div>
    </div>
</div>
</body>
</html>
"""

    @staticmethod
    def community_certificate(data: Dict[str, Any]) -> str:
        """Generate Community Certificate"""
        qr_data = f"COMMUNITY-{data.get('certificate_no', '')}-{data.get('applicant_name', '')}"
        qr_code = GovernmentCertificates.generate_qr_code(qr_data)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Community Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: Arial, 'Noto Sans Tamil', sans-serif; background: #f7f9fc; padding: 44px; }}
        .certificate-box {{ border: 3px solid #059669; padding: 35px; max-width: 860px; margin: auto; background: #fff; box-shadow: 0 0 15px rgba(5,150,105,0.2); position: relative; }}
        .govt-emblem {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #059669; }}
        .govt-emblem h3 {{ color: #059669; margin: 5px 0; font-size: 20px; }}
        .cert-title {{ text-align: center; font-size: 1.67em; color: #059669; font-weight: bold; margin: 15px 0; }}
        .cert-details {{ font-size: 1.15em; color: #222b39; margin-bottom: 13px; background: #f0fdf4; padding: 10px; border-left: 4px solid #059669; }}
        .main-text {{ font-size: 1.09em; color: #333; margin-bottom: 14px; line-height: 1.8; }}
        .community-box {{ background: #dcfce7; border: 2px solid #059669; padding: 20px; border-radius: 5px; text-align: center; font-size: 20px; font-weight: bold; color: #065f46; margin: 25px 0; }}
        .remarks {{ font-size: 1em; color: #555; margin-top: 12px; background: #fef3c7; padding: 10px; border-radius: 5px; }}
        .sign-section {{ margin-top: 33px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .sign-box {{ text-align: center; }}
        .sign-label {{ font-weight: bold; color: #171a1b; font-size: 1em; margin-top: 50px; border-top: 2px solid #333; padding-top: 5px; }}
        .official-seal {{ width: 90px; height: 90px; border: 3px solid #059669; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; color: #059669; background: radial-gradient(circle, rgba(5,150,105,0.1) 0%, rgba(5,150,105,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 35px; right: 35px; text-align: center; }}
        .qr-img {{ width: 81px; height: 81px; }}
    </style>
</head>
<body>
<div class="certificate-box">
    <div class="govt-emblem">
        <h3>🏛️ GOVERNMENT OF TAMIL NADU</h3>
        <h3>REVENUE DEPARTMENT</h3>
    </div>
    
    <div class="cert-title">COMMUNITY CERTIFICATE</div>

    <div class="cert-details">
        <strong>Certificate No:</strong> {data.get('certificate_no', 'COM/2024/XXXXX')}<br>
        <strong>Date of Issue:</strong> {data.get('issue_date', datetime.now().strftime('%d/%m/%Y'))}
    </div>

    <div class="main-text">
        This is to certify that <b>{data.get('applicant_name', '').upper()}</b>, 
        son/daughter of <b>{data.get('parent_name', '').upper()}</b>, 
        Date of Birth: <b>{data.get('dob', '')}</b>,
        residing at <b>{data.get('address', '')}</b>, 
        Taluk: <b>{data.get('taluk', '')}</b>, 
        District: <b>{data.get('district', '')}</b>, 
        belongs to the following community:
    </div>

    <div class="community-box">
        COMMUNITY: {data.get('community', '').upper()}<br>
        <span style="font-size: 14px;">({data.get('community_code', '')})</span>
    </div>

    <div class="main-text">
        The above information has been verified from the records available in this office and found to be correct.
    </div>

    <div class="remarks">
        <strong>Purpose:</strong> {data.get('purpose', 'Educational/Employment purposes')}<br>
        <strong>Validity:</strong> This certificate is valid for one year from the date of issue.<br>
        <strong>Note:</strong> This certificate is digitally signed and does not require any seal or handwritten signature.
    </div>

    <div class="sign-section">
        <div class="official-seal">
            OFFICIAL<br>SEAL<br>REVENUE<br>DEPT
        </div>
        
        <div class="sign-box">
            <div class="sign-label">
                Tahsildar<br>
                {data.get('taluk', 'Taluk')} Taluk<br>
                {data.get('district', 'District')} District
            </div>
        </div>
    </div>

    <div class="qr-section">
        <img src="data:image/png;base64,{qr_code}" class="qr-img" alt="QR Code" />
        <div style="font-size: 9px; margin-top: 5px;">Scan to Verify</div>
    </div>
</div>
</body>
</html>
"""

    @staticmethod
    def nativity_certificate(data: Dict[str, Any]) -> str:
        """Generate Nativity Certificate"""
        qr_data = f"NATIVITY-{data.get('certificate_no', '')}-{data.get('applicant_name', '')}"
        qr_code = GovernmentCertificates.generate_qr_code(qr_data)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Nativity Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: Arial, 'Noto Sans Tamil', sans-serif; background: #f7f9fc; padding: 44px; }}
        .certificate-box {{ border: 3px solid #7c3aed; padding: 35px; max-width: 860px; margin: auto; background: #fff; box-shadow: 0 0 15px rgba(124,58,237,0.2); position: relative; }}
        .govt-emblem {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #7c3aed; }}
        .govt-emblem h3 {{ color: #7c3aed; margin: 5px 0; font-size: 20px; }}
        .cert-title {{ text-align: center; font-size: 1.67em; color: #7c3aed; font-weight: bold; margin: 15px 0; }}
        .cert-details {{ font-size: 1.15em; color: #222b39; margin-bottom: 13px; background: #faf5ff; padding: 10px; border-left: 4px solid #7c3aed; }}
        .main-text {{ font-size: 1.09em; color: #333; margin-bottom: 14px; line-height: 1.8; }}
        .nativity-box {{ background: #ede9fe; border: 2px solid #7c3aed; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; color: #5b21b6; margin: 25px 0; }}
        .remarks {{ font-size: 1em; color: #555; margin-top: 12px; background: #fef3c7; padding: 10px; border-radius: 5px; }}
        .sign-section {{ margin-top: 33px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .sign-box {{ text-align: center; }}
        .sign-label {{ font-weight: bold; color: #171a1b; font-size: 1em; margin-top: 50px; border-top: 2px solid #333; padding-top: 5px; }}
        .official-seal {{ width: 90px; height: 90px; border: 3px solid #7c3aed; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; color: #7c3aed; background: radial-gradient(circle, rgba(124,58,237,0.1) 0%, rgba(124,58,237,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 35px; right: 35px; text-align: center; }}
        .qr-img {{ width: 81px; height: 81px; }}
    </style>
</head>
<body>
<div class="certificate-box">
    <div class="govt-emblem">
        <h3>🏛️ GOVERNMENT OF TAMIL NADU</h3>
        <h3>REVENUE DEPARTMENT</h3>
    </div>
    
    <div class="cert-title">NATIVITY CERTIFICATE</div>

    <div class="cert-details">
        <strong>Certificate No:</strong> {data.get('certificate_no', 'NAT/2024/XXXXX')}<br>
        <strong>Date of Issue:</strong> {data.get('issue_date', datetime.now().strftime('%d/%m/%Y'))}
    </div>

    <div class="main-text">
        This is to certify that <b>{data.get('applicant_name', '').upper()}</b>, 
        son/daughter of <b>{data.get('parent_name', '').upper()}</b>, 
        Date of Birth: <b>{data.get('dob', '')}</b>,
        residing at <b>{data.get('address', '')}</b>, 
        is a native of:
    </div>

    <div class="nativity-box">
        VILLAGE/TOWN: {data.get('village', '').upper()}<br>
        TALUK: {data.get('taluk', '').upper()}<br>
        DISTRICT: {data.get('district', '').upper()}<br>
        STATE: TAMIL NADU
    </div>

    <div class="main-text">
        The family has been residing at the above address for the past <b>{data.get('years_of_residence', '0')} years</b>. 
        This information has been verified from the records available in this office.
    </div>

    <div class="remarks">
        <strong>Purpose:</strong> {data.get('purpose', 'Educational/Employment/Government purposes')}<br>
        <strong>Validity:</strong> This certificate is valid for one year from the date of issue.<br>
        <strong>Note:</strong> This certificate is digitally signed and authenticated.
    </div>

    <div class="sign-section">
        <div class="official-seal">
            OFFICIAL<br>SEAL<br>REVENUE<br>DEPT
        </div>
        
        <div class="sign-box">
            <div class="sign-label">
                Tahsildar<br>
                {data.get('taluk', 'Taluk')} Taluk<br>
                {data.get('district', 'District')} District
            </div>
        </div>
    </div>

    <div class="qr-section">
        <img src="data:image/png;base64,{qr_code}" class="qr-img" alt="QR Code" />
        <div style="font-size: 9px; margin-top: 5px;">Scan to Verify</div>
    </div>
</div>
</body>
</html>
"""

    @staticmethod
    def transfer_certificate(data: Dict[str, Any]) -> str:
        """Generate Transfer Certificate"""
        qr_data = f"TC-{data.get('certificate_no', '')}-{data.get('student_name', '')}"
        qr_code = GovernmentCertificates.generate_qr_code(qr_data)
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Transfer Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: Arial, 'Noto Sans Tamil', sans-serif; background: #f7f9fc; padding: 44px; }}
        .certificate-box {{ border: 3px solid #ea580c; padding: 35px; max-width: 860px; margin: auto; background: #fff; box-shadow: 0 0 15px rgba(234,88,12,0.2); position: relative; }}
        .school-header {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #ea580c; }}
        .school-header h3 {{ color: #ea580c; margin: 5px 0; font-size: 20px; }}
        .cert-title {{ text-align: center; font-size: 1.67em; color: #ea580c; font-weight: bold; margin: 15px 0; text-decoration: underline; }}
        .cert-details {{ font-size: 1.15em; color: #222b39; margin-bottom: 13px; background: #fff7ed; padding: 10px; border-left: 4px solid #ea580c; }}
        .main-text {{ font-size: 1.09em; color: #333; margin-bottom: 10px; line-height: 1.8; }}
        table.info-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        table.info-table th, table.info-table td {{ border: 1px solid #aaa; padding: 10px; text-align: left; font-size: 0.98em; }}
        table.info-table th {{ background: #ea580c; color: white; }}
        .remarks {{ font-size: 1em; color: #555; margin-top: 12px; background: #fef3c7; padding: 10px; border-radius: 5px; }}
        .sign-section {{ margin-top: 33px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .sign-box {{ text-align: center; }}
        .sign-label {{ font-weight: bold; color: #171a1b; font-size: 1em; margin-top: 50px; border-top: 2px solid #333; padding-top: 5px; }}
        .official-seal {{ width: 90px; height: 90px; border: 3px solid #ea580c; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; color: #ea580c; background: radial-gradient(circle, rgba(234,88,12,0.1) 0%, rgba(234,88,12,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 35px; right: 35px; text-align: center; }}
        .qr-img {{ width: 81px; height: 81px; }}
    </style>
</head>
<body>
<div class="certificate-box">
    <div class="school-header">
        <h3>{data.get('school_name', 'SCHOOL NAME').upper()}</h3>
        <p style="margin: 5px 0; font-size: 14px;">{data.get('school_address', '')}</p>
        <p style="margin: 5px 0; font-size: 14px;">School Code: {data.get('school_code', '')}</p>
    </div>
    
    <div class="cert-title">TRANSFER CERTIFICATE</div>

    <div class="cert-details">
        <strong>TC No:</strong> {data.get('certificate_no', 'TC/2024/XXXXX')}<br>
        <strong>Date of Issue:</strong> {data.get('issue_date', datetime.now().strftime('%d/%m/%Y'))}
    </div>

    <table class="info-table">
        <tr><th colspan="2" style="text-align: center;">STUDENT DETAILS</th></tr>
        <tr><td><strong>1. Name of Student</strong></td><td>{data.get('student_name', '').upper()}</td></tr>
        <tr><td><strong>2. Father's Name</strong></td><td>{data.get('father_name', '').upper()}</td></tr>
        <tr><td><strong>3. Mother's Name</strong></td><td>{data.get('mother_name', '').upper()}</td></tr>
        <tr><td><strong>4. Date of Birth</strong></td><td>{data.get('dob', '')}</td></tr>
        <tr><td><strong>5. Admission Number</strong></td><td>{data.get('admission_no', '')}</td></tr>
        <tr><td><strong>6. Date of Admission</strong></td><td>{data.get('admission_date', '')}</td></tr>
        <tr><td><strong>7. Class at the time of leaving</strong></td><td>{data.get('class_leaving', '')}</td></tr>
        <tr><td><strong>8. Date of Leaving</strong></td><td>{data.get('leaving_date', '')}</td></tr>
        <tr><td><strong>9. Reason for Leaving</strong></td><td>{data.get('reason', '')}</td></tr>
        <tr><td><strong>10. Conduct & Character</strong></td><td>{data.get('conduct', 'GOOD')}</td></tr>
        <tr><td><strong>11. Medium of Instruction</strong></td><td>{data.get('medium', 'ENGLISH')}</td></tr>
    </table>

    <div class="remarks">
        <strong>Remarks:</strong> {data.get('remarks', 'The student has completed the academic year successfully and is eligible for admission to higher classes.')}<br>
        <strong>Note:</strong> This certificate is digitally signed and authenticated.
    </div>

    <div class="sign-section">
        <div class="official-seal">
            SCHOOL<br>SEAL
        </div>
        
        <div class="sign-box">
            <div class="sign-label">
                Principal<br>
                {data.get('school_name', 'School Name')}
            </div>
        </div>
    </div>

    <div class="qr-section">
        <img src="data:image/png;base64,{qr_code}" class="qr-img" alt="QR Code" />
        <div style="font-size: 9px; margin-top: 5px;">Scan to Verify</div>
    </div>
</div>
</body>
</html>
"""

    @staticmethod
    def first_graduate_certificate(data: Dict[str, Any]) -> str:
        """Generate First Graduate Certificate"""
        qr_data = f"FIRSTGRAD-{data.get('certificate_no', '')}-{data.get('applicant_name', '')}"
        qr_code = GovernmentCertificates.generate_qr_code(qr_data)
        
        family_rows = ""
        for idx, member in enumerate(data.get('family_members', []), 1):
            family_rows += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{member.get('name', '')}</td>
                    <td>{member.get('relationship', '')}</td>
                    <td>{member.get('education', '')}</td>
                </tr>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>First Graduate Certificate</title>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ font-family: Arial, 'Noto Sans Tamil', sans-serif; background: #f7f9fc; padding: 44px; }}
        .certificate-box {{ border: 3px solid #0891b2; padding: 35px; max-width: 860px; margin: auto; background: #fff; box-shadow: 0 0 15px rgba(8,145,178,0.2); position: relative; }}
        .govt-emblem {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #0891b2; }}
        .govt-emblem h3 {{ color: #0891b2; margin: 5px 0; font-size: 20px; }}
        .cert-title {{ text-align: center; font-size: 1.67em; color: #0891b2; font-weight: bold; margin: 15px 0; }}
        .cert-details {{ font-size: 1.15em; color: #222b39; margin-bottom: 13px; background: #ecfeff; padding: 10px; border-left: 4px solid #0891b2; }}
        .main-text {{ font-size: 1.09em; color: #333; margin-bottom: 14px; line-height: 1.8; }}
        .table-label {{ font-size: 1.04em; color: #0891b2; font-weight: bold; margin: 15px 0 7px 0; }}
        table.info-table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
        table.info-table th, table.info-table td {{ border: 1px solid #aaa; padding: 10px 8px; text-align: left; font-size: 0.98em; }}
        table.info-table th {{ background: #0891b2; color: white; text-align: center; }}
        table.info-table tr:nth-child(even) {{ background: #f0fdff; }}
        .highlight-box {{ background: #cffafe; border: 2px solid #0891b2; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; color: #164e63; margin: 25px 0; }}
        .remarks {{ font-size: 1em; color: #555; margin-top: 12px; background: #fef3c7; padding: 10px; border-radius: 5px; }}
        .sign-section {{ margin-top: 33px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .sign-box {{ text-align: center; }}
        .sign-label {{ font-weight: bold; color: #171a1b; font-size: 1em; margin-top: 50px; border-top: 2px solid #333; padding-top: 5px; }}
        .official-seal {{ width: 90px; height: 90px; border: 3px solid #0891b2; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; text-align: center; color: #0891b2; background: radial-gradient(circle, rgba(8,145,178,0.1) 0%, rgba(8,145,178,0.05) 100%); }}
        .qr-section {{ position: absolute; bottom: 35px; right: 35px; text-align: center; }}
        .qr-img {{ width: 81px; height: 81px; }}
    </style>
</head>
<body>
<div class="certificate-box">
    <div class="govt-emblem">
        <h3>🏛️ GOVERNMENT OF TAMIL NADU</h3>
        <h3>HIGHER EDUCATION DEPARTMENT</h3>
    </div>
    
    <div class="cert-title">FIRST GRADUATE CERTIFICATE</div>

    <div class="cert-details">
        <strong>Certificate No:</strong> {data.get('certificate_no', 'FG/2024/XXXXX')}<br>
        <strong>Date of Issue:</strong> {data.get('issue_date', datetime.now().strftime('%d/%m/%Y'))}
    </div>

    <div class="main-text">
        This is to certify that <b>{data.get('applicant_name', '').upper()}</b>, 
        son/daughter of <b>{data.get('parent_name', '').upper()}</b>, 
        Date of Birth: <b>{data.get('dob', '')}</b>,
        residing at <b>{data.get('address', '')}</b>, 
        is the <b>FIRST GRADUATE</b> in their family.
    </div>

    <div class="highlight-box">
        🎓 FIRST GRADUATE IN THE FAMILY 🎓
    </div>

    <div class="table-label">Family Education Details:</div>
    <table class="info-table">
        <tr>
            <th>Sl. No</th>
            <th>Name of Family Member</th>
            <th>Relationship</th>
            <th>Educational Qualification</th>
        </tr>
        {family_rows}
    </table>

    <div class="main-text">
        <strong>Applicant's Qualification:</strong><br>
        Degree: <b>{data.get('degree', '')}</b><br>
        Institution: <b>{data.get('institution', '')}</b><br>
        Year of Passing: <b>{data.get('year_of_passing', '')}</b>
    </div>

    <div class="remarks">
        <strong>Purpose:</strong> {data.get('purpose', 'Educational/Scholarship purposes')}<br>
        <strong>Validity:</strong> This certificate is valid permanently.<br>
        <strong>Note:</strong> This certificate is digitally signed and authenticated.
    </div>

    <div class="sign-section">
        <div class="official-seal">
            OFFICIAL<br>SEAL<br>HIGHER<br>EDU
        </div>
        
        <div class="sign-box">
            <div class="sign-label">
                Principal<br>
                {data.get('institution', 'Institution Name')}
            </div>
        </div>
    </div>

    <div class="qr-section">
        <img src="data:image/png;base64,{qr_code}" class="qr-img" alt="QR Code" />
        <div style="font-size: 9px; margin-top: 5px;">Scan to Verify</div>
    </div>
</div>
</body>
</html>
"""

# Initialize government certificates
government_certificates = GovernmentCertificates()
