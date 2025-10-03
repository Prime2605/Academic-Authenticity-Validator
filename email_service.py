"""
Email Notification Service for Academic Authenticity Validator
Sends automated emails for certificate issuance, verification, and notifications
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

class EmailService:
    """Email service for sending notifications and certificates"""
    
    def __init__(self):
        # Email configuration (using Gmail SMTP for demo)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Demo credentials (in production, use environment variables)
        self.sender_email = "academic.validator@hackathon.com"
        self.sender_password = "demo_password_2024"  # Use app password in production
        
        # Email templates directory
        self.templates_dir = "email_templates"
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
        
        self.create_email_templates()
    
    def create_email_templates(self):
        """Create professional email templates"""
        
        # Certificate Issued Template
        certificate_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .certificate-info { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }
                .verification-box { background: #e8f5e8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #666; }
                .btn { background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Academic Certificate Issued</h1>
                    <p>Your academic achievement has been verified and recorded on blockchain</p>
                </div>
                
                <div class="content">
                    <h2>Congratulations, {student_name}!</h2>
                    
                    <p>We are pleased to inform you that your academic certificate has been successfully issued and secured on our blockchain network.</p>
                    
                    <div class="certificate-info">
                        <h3>📜 Certificate Details</h3>
                        <p><strong>Student Name:</strong> {student_name}</p>
                        <p><strong>Student ID:</strong> {student_id}</p>
                        <p><strong>Institution:</strong> {institution_name}</p>
                        <p><strong>Degree:</strong> {degree_type}</p>
                        <p><strong>Field of Study:</strong> {field_of_study}</p>
                        <p><strong>Issue Date:</strong> {issue_date}</p>
                        <p><strong>Certificate ID:</strong> {certificate_id}</p>
                    </div>
                    
                    <div class="verification-box">
                        <h3>🔗 Blockchain Verification</h3>
                        <p><strong>Verification Code:</strong> <code>{verification_code}</code></p>
                        <p>Your certificate is secured by blockchain technology and can be verified instantly.</p>
                        
                        <a href="{verification_url}" class="btn">🔍 Verify Certificate</a>
                        <a href="{certificate_url}" class="btn">📄 View Certificate</a>
                    </div>
                    
                    <h3>📱 How to Share Your Certificate:</h3>
                    <ul>
                        <li><strong>Verification Code:</strong> Share code <code>{verification_code}</code> with employers</li>
                        <li><strong>QR Code:</strong> Generate QR code for instant verification</li>
                        <li><strong>PDF Download:</strong> Download professional certificate PDF</li>
                        <li><strong>Direct Link:</strong> Share certificate URL with anyone</li>
                    </ul>
                    
                    <p><strong>Important:</strong> This certificate is tamper-proof and permanently recorded on blockchain. Any attempt to modify it will be detected.</p>
                </div>
                
                <div class="footer">
                    <p>Academic Authenticity Validator - Smart India Hackathon 2024</p>
                    <p>Powered by Blockchain Technology | Secure • Transparent • Immutable</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Verification Notification Template
        verification_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .alert { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }
                .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Certificate Verification Alert</h1>
                    <p>Someone has verified a certificate from your institution</p>
                </div>
                
                <div class="content">
                    <div class="alert">
                        <h3>🔍 Verification Details</h3>
                        <p><strong>Certificate:</strong> {certificate_id}</p>
                        <p><strong>Student:</strong> {student_name}</p>
                        <p><strong>Verified At:</strong> {verification_time}</p>
                        <p><strong>Verification Code:</strong> {verification_code}</p>
                    </div>
                    
                    <p>This notification confirms that the above certificate was successfully verified using our blockchain system.</p>
                    
                    <p><strong>Verification Status:</strong> ✅ Valid & Authentic</p>
                    <p><strong>Blockchain Status:</strong> 🔗 Confirmed on Chain</p>
                </div>
                
                <div class="footer">
                    <p>Academic Authenticity Validator - Verification Alert System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save templates
        with open(os.path.join(self.templates_dir, "certificate_issued.html"), "w", encoding="utf-8") as f:
            f.write(certificate_template)
        
        with open(os.path.join(self.templates_dir, "verification_alert.html"), "w", encoding="utf-8") as f:
            f.write(verification_template)
    
    def send_certificate_notification(self, certificate_data: Dict[str, Any], verification_code: str, 
                                    recipient_email: str) -> Dict[str, Any]:
        """Send certificate issuance notification to student"""
        try:
            # Load template
            template_path = os.path.join(self.templates_dir, "certificate_issued.html")
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            # Format template with certificate data
            verification_url = f"http://localhost:5000/?verify={verification_code}"
            certificate_url = f"http://localhost:5000/certificate/{verification_code}"
            
            html_content = template.format(
                student_name=certificate_data.get('student_name', 'N/A'),
                student_id=certificate_data.get('student_id', 'N/A'),
                institution_name=certificate_data.get('institution_name', 'N/A'),
                degree_type=certificate_data.get('degree_type', 'N/A'),
                field_of_study=certificate_data.get('field_of_study', 'N/A'),
                issue_date=certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
                certificate_id=certificate_data.get('certificate_id', 'N/A'),
                verification_code=verification_code,
                verification_url=verification_url,
                certificate_url=certificate_url
            )
            
            # Create email
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🎓 Your Academic Certificate is Ready - {certificate_data.get('student_name', 'Student')}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email (simulated for demo)
            return self.simulate_email_send(message, recipient_email)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_verification_alert(self, certificate_data: Dict[str, Any], verification_code: str,
                              institution_email: str) -> Dict[str, Any]:
        """Send verification alert to institution"""
        try:
            # Load template
            template_path = os.path.join(self.templates_dir, "verification_alert.html")
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            # Format template
            html_content = template.format(
                certificate_id=certificate_data.get('certificate_id', 'N/A'),
                student_name=certificate_data.get('student_name', 'N/A'),
                verification_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                verification_code=verification_code
            )
            
            # Create email
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🔍 Certificate Verification Alert - {certificate_data.get('student_name', 'Student')}"
            message["From"] = self.sender_email
            message["To"] = institution_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email (simulated for demo)
            return self.simulate_email_send(message, institution_email)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_certificate_with_attachment(self, certificate_data: Dict[str, Any], verification_code: str,
                                       recipient_email: str, pdf_path: str) -> Dict[str, Any]:
        """Send certificate with PDF attachment"""
        try:
            # Create email with attachment
            message = MIMEMultipart()
            message["Subject"] = f"📄 Your Academic Certificate PDF - {certificate_data.get('student_name', 'Student')}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Email body
            body = f"""
            Dear {certificate_data.get('student_name', 'Student')},
            
            Please find your academic certificate attached as a PDF document.
            
            Certificate Details:
            - Student: {certificate_data.get('student_name', 'N/A')}
            - Institution: {certificate_data.get('institution_name', 'N/A')}
            - Degree: {certificate_data.get('degree_type', 'N/A')}
            - Verification Code: {verification_code}
            
            You can also verify your certificate online at:
            http://localhost:5000/?verify={verification_code}
            
            Best regards,
            Academic Authenticity Validator Team
            """
            
            message.attach(MIMEText(body, "plain"))
            
            # Add PDF attachment
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= certificate_{verification_code}.pdf'
                )
                message.attach(part)
            
            # Send email (simulated for demo)
            return self.simulate_email_send(message, recipient_email)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_email_send(self, message: MIMEMultipart, recipient: str) -> Dict[str, Any]:
        """Simulate email sending for demo purposes"""
        try:
            # In production, this would actually send the email:
            # context = ssl.create_default_context()
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls(context=context)
            #     server.login(self.sender_email, self.sender_password)
            #     server.sendmail(self.sender_email, recipient, message.as_string())
            
            # For demo, we'll log the email and save it to a file
            email_log = {
                'timestamp': datetime.now().isoformat(),
                'to': recipient,
                'subject': message.get('Subject'),
                'status': 'sent_simulated'
            }
            
            # Save email log
            log_file = "email_logs.json"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(email_log)
            
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
            
            # Save email content for demo viewing
            email_filename = f"sent_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{recipient.replace('@', '_at_')}.html"
            email_path = os.path.join(self.templates_dir, email_filename)
            
            # Extract HTML content
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    with open(email_path, "w", encoding="utf-8") as f:
                        f.write(part.get_payload())
                    break
            
            return {
                'success': True,
                'message': f'Email sent successfully to {recipient}',
                'email_file': email_path,
                'log_entry': email_log
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send email: {str(e)}'
            }
    
    def get_email_logs(self) -> List[Dict[str, Any]]:
        """Get email sending logs"""
        try:
            log_file = "email_logs.json"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def send_bulk_notifications(self, certificates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send bulk certificate notifications"""
        results = {
            'success_count': 0,
            'failed_count': 0,
            'results': []
        }
        
        for cert_data in certificates:
            try:
                # Generate email for each certificate
                student_email = cert_data.get('student_email', f"{cert_data.get('student_id', 'student')}@example.com")
                verification_code = cert_data.get('verification_code', 'DEMO123')
                
                result = self.send_certificate_notification(cert_data, verification_code, student_email)
                
                if result.get('success'):
                    results['success_count'] += 1
                else:
                    results['failed_count'] += 1
                
                results['results'].append({
                    'student': cert_data.get('student_name'),
                    'email': student_email,
                    'status': 'success' if result.get('success') else 'failed',
                    'error': result.get('error') if not result.get('success') else None
                })
                
            except Exception as e:
                results['failed_count'] += 1
                results['results'].append({
                    'student': cert_data.get('student_name', 'Unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results

# Global email service instance
email_service = EmailService()
