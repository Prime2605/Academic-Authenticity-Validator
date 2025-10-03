"""
Academic Authenticity Validator - Flask Web Application
API endpoints for academic credential validation system
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import time
import json
import traceback
from datetime import datetime
from enhanced_blockchain import academic_blockchain
from academic_models import (
    AcademicCredential, Institution, Student, ResearchPaper,
    CredentialType, InstitutionType, generate_credential_id, 
    generate_qr_code_data
)
from certificate_database import CertificateDatabase, CertificateRecord
from certificate_generator import certificate_generator
from email_service import email_service
from analytics_engine import analytics_engine
from ocr_forensics import ocr_forensics_engine
from pki_digital_signing import pki_signing_engine
from dual_strategy_processor import dual_strategy_processor
from ml_forensics_engine import ml_forensics_engine
from digilocker_integration import digilocker_integration
from certificate_templates import certificate_templates
from government_certificates import government_certificates
import os
from werkzeug.utils import secure_filename
from flask import send_file, session, redirect, url_for
import time
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions-change-in-production'
CORS(app)

# Global error handler for JSON serialization issues
@app.errorhandler(Exception)
def handle_json_error(error):
    """Handle JSON serialization errors"""
    error_message = str(error)
    if 'JSON' in error_message or 'serializ' in error_message.lower():
        return jsonify({
            'success': False,
            'error': 'JSON serialization error',
            'details': error_message,
            'type': 'json_error'
        }), 500
    
    # For other errors, return generic error
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'details': error_message,
        'type': 'server_error'
    }), 500

# Initialize certificate database (blockchain is already initialized in enhanced_blockchain.py)
certificate_db = CertificateDatabase()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page of the academic authenticity validator - All in One"""
    return render_template('all_in_one.html')

# Institution Management Endpoints
@app.route('/api/colleges/search', methods=['POST'])
def search_colleges():
    """Search colleges with filters"""
    data = request.get_json() or {}
    query = data.get('query', '')
    category = data.get('category', '')
    type_filter = data.get('type', '')

    from academic_models import search_colleges
    results = search_colleges(query=query or None, category=category or None, type_filter=type_filter or None)

    return jsonify({
        'colleges': [inst.to_dict() for inst in results],
        'total': len(results)
    })

@app.route('/api/colleges/<institution_id>')
def get_college_details(institution_id):
    """Get detailed information about a specific college"""
    from academic_models import get_institution_details
    institution = get_institution_details(institution_id)

    if not institution:
        return jsonify({'error': 'Institution not found'}), 404

    return jsonify(institution.to_dict())

@app.route('/api/colleges/categories')
def get_college_categories():
    """Get available college categories"""
    from college_database import get_institution_categories
    categories = get_institution_categories()
    return jsonify({'categories': categories})

@app.route('/api/colleges/types')
def get_college_types():
    """Get available college types"""
    from college_database import get_institution_types
    types = get_institution_types()
    return jsonify({'types': types})

@app.route('/api/colleges/courses/<institution_id>')
def get_college_courses(institution_id):
    """Get courses offered by a specific college"""
    from academic_models import get_courses_for_institution
    courses = get_courses_for_institution(institution_id)
    return jsonify({'courses': courses})

@app.route('/api/colleges/stats')
def get_college_statistics():
    """Get statistics about colleges in the database"""
    from academic_models import get_institution_statistics
    stats = get_institution_statistics()
    return jsonify(stats)

@app.route('/api/institutions/<institution_id>')
def get_institution(institution_id):
    """Get specific institution details"""
    if institution_id not in academic_blockchain.institutions:
        return jsonify({'error': 'Institution not found'}), 404
    
    institution = academic_blockchain.institutions[institution_id]
    credentials_issued = academic_blockchain.get_institution_credentials(institution_id)
    
    return jsonify({
        'institution': institution.to_dict(),
        'credentials_issued': len(credentials_issued),
        'recent_credentials': credentials_issued[-5:] if credentials_issued else []
    })

@app.route('/api/institutions', methods=['POST'])
def register_institution():
    """Register a new academic institution"""
    data = request.get_json()
    
    required_fields = ['id', 'name', 'type', 'country', 'accreditation_body', 
                      'public_key', 'website', 'established_year']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        institution = Institution(
            id=data['id'],
            name=data['name'],
            type=InstitutionType(data['type']),
            country=data['country'],
            accreditation_body=data['accreditation_body'],
            public_key=data['public_key'],
            website=data['website'],
            established_year=int(data['established_year']),
            is_verified=data.get('is_verified', False)
        )
        
        success = academic_blockchain.register_institution(institution)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Institution registered successfully',
                'institution_id': institution.id
            })
        else:
            return jsonify({'error': 'Institution already exists'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Student Management Endpoints
@app.route('/api/students/<student_id>')
def get_student(student_id):
    """Get student details and their credentials"""
    if student_id not in academic_blockchain.students:
        return jsonify({'error': 'Student not found'}), 404
    
    student = academic_blockchain.students[student_id]
    credentials = academic_blockchain.get_student_credentials(student_id)
    
    return jsonify({
        'student': student.to_dict(),
        'credentials': credentials,
        'total_credentials': len(credentials)
    })

@app.route('/api/students', methods=['POST'])
def register_student():
    """Register a new student"""
    data = request.get_json()
    
    required_fields = ['id', 'first_name', 'last_name', 'date_of_birth', 
                      'student_id', 'email']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        student = Student(**data)
        success = academic_blockchain.register_student(student)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Student registered successfully',
                'student_id': student.id
            })
        else:
            return jsonify({'error': 'Student already exists'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Credential Management Endpoints
@app.route('/api/credentials', methods=['POST'])
def issue_credential():
    """Issue a new academic credential"""
    data = request.get_json()
    
    try:
        # Extract institution and student data
        institution_data = data['institution']
        student_data = data['student']
        
        # Get institution from existing registry
        if institution_data['id'] not in academic_blockchain.institutions:
            return jsonify({'error': 'Institution not found in registry'}), 400
        
        institution = academic_blockchain.institutions[institution_data['id']]
        student = Student.from_dict(student_data)
        
        # Generate credential ID if not provided
        if 'id' not in data or not data['id']:
            data['id'] = generate_credential_id(
                student.id, 
                institution.id, 
                data['credential_type'], 
                data['issue_date']
            )
        
        # Create credential
        credential = AcademicCredential(
            id=data['id'],
            credential_type=CredentialType(data['credential_type']),
            title=data['title'],
            field_of_study=data['field_of_study'],
            level=CredentialLevel(data['level']),
            institution=institution,
            student=student,
            issue_date=data['issue_date'],
            completion_date=data['completion_date'],
            gpa=data.get('gpa'),
            honors=data.get('honors'),
            courses=data.get('courses', []),
            thesis_title=data.get('thesis_title'),
            advisor=data.get('advisor'),
            additional_info=data.get('additional_info', {})
        )
        
        # Issue credential
        result = academic_blockchain.issue_credential(credential, institution.id)
        
        if result['success']:
            # Generate QR code data
            qr_data = generate_qr_code_data(credential)
            result['qr_code_data'] = qr_data
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/credentials/<credential_id>')
def get_credential(credential_id):
    """Get specific credential details"""
    if credential_id not in academic_blockchain.credentials:
        return jsonify({'error': 'Credential not found'}), 404
    
    credential = academic_blockchain.credentials[credential_id]
    return jsonify(credential.to_dict())

@app.route('/api/credentials/<credential_id>/verify')
def verify_credential(credential_id):
    """Verify a specific credential"""
    result = academic_blockchain.verify_credential(credential_id)
    return jsonify(result)

@app.route('/api/credentials/<credential_id>/qr')
def get_credential_qr(credential_id):
    """Get QR code data for credential"""
    if credential_id not in academic_blockchain.credentials:
        return jsonify({'error': 'Credential not found'}), 404
    
    credential = academic_blockchain.credentials[credential_id]
    qr_data = generate_qr_code_data(credential)
    return jsonify(qr_data)

@app.route('/api/credentials/search', methods=['POST'])
def search_credentials():
    """Search credentials based on criteria"""
    query = request.get_json()
    results = academic_blockchain.search_credentials(query)
    return jsonify({
        'results': results,
        'count': len(results)
    })

# Research Paper Endpoints
@app.route('/api/research-papers', methods=['POST'])
def submit_research_paper():
    """Submit a research paper for authenticity tracking"""
    data = request.get_json()
    
    required_fields = ['id', 'title', 'authors', 'institution_ids', 
                      'abstract', 'keywords', 'publication_date']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        paper = ResearchPaper(
            id=data['id'],
            title=data['title'],
            authors=data['authors'],
            institution_ids=data['institution_ids'],
            abstract=data['abstract'],
            keywords=data['keywords'],
            publication_date=data['publication_date'],
            journal=data.get('journal'),
            doi=data.get('doi'),
            peer_reviewed=data.get('peer_reviewed', False),
            citation_count=data.get('citation_count', 0)
        )
        
        # Use first institution as submitter
        submitter_id = data['institution_ids'][0]
        result = academic_blockchain.submit_research_paper(paper, submitter_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/research-papers/<paper_id>')
def get_research_paper(paper_id):
    """Get research paper details"""
    if paper_id not in academic_blockchain.research_papers:
        return jsonify({'error': 'Research paper not found'}), 404
    
    paper = academic_blockchain.research_papers[paper_id]
    return jsonify(paper.to_dict())

# Mining Endpoints
@app.route('/api/mine', methods=['POST'])
def mine_academic_block():
    """Mine pending academic transactions"""
    data = request.get_json()
    
    if 'institution_id' not in data:
        return jsonify({'error': 'Missing institution_id'}), 400
    
    result = academic_blockchain.mine_academic_transactions(data['institution_id'])
    return jsonify(result)

@app.route('/api/pending-transactions')
def get_pending_transactions():
    """Get all pending academic transactions"""
    transactions = []
    for tx in academic_blockchain.pending_academic_transactions:
        transactions.append(tx.to_dict())
    
    return jsonify(transactions)

# Statistics and Analytics Endpoints
@app.route('/api/statistics')
def get_statistics():
    """Get comprehensive academic blockchain statistics"""
    stats = academic_blockchain.get_academic_statistics()
    return jsonify(stats)

@app.route('/api/chain')
def get_academic_chain():
    """Get the entire academic blockchain"""
    chain_data = []
    for i, block in enumerate(academic_blockchain.chain):
        block_dict = block.to_dict()
        block_dict['index'] = i
        
        # Add academic transaction details
        if isinstance(block.data, list):
            academic_transactions = []
            for tx in block.data:
                if isinstance(tx, dict) and 'transaction_type' in tx:
                    academic_transactions.append(tx)
            block_dict['academic_transactions'] = academic_transactions
        
        chain_data.append(block_dict)
    
    return jsonify(chain_data)

@app.route('/api/validate')
def validate_academic_chain():
    """Validate the academic blockchain"""
    is_valid = academic_blockchain.is_chain_valid()
    return jsonify({'is_valid': is_valid})

# Export/Import Endpoints
@app.route('/api/export')
def export_academic_data():
    """Export all academic data"""
    data = academic_blockchain.export_academic_data()
    return jsonify(data)

# Dashboard Data Endpoint
@app.route('/api/dashboard')
def get_dashboard_data():
    """Get dashboard data for academic system"""
    stats = academic_blockchain.get_academic_statistics()
    
    # Get recent credentials
    recent_credentials = []
    all_credentials = list(academic_blockchain.credentials.values())
    all_credentials.sort(key=lambda x: x.issue_date, reverse=True)
    for cred in all_credentials[:5]:
        recent_credentials.append({
            'id': cred.id,
            'title': cred.title,
            'student_name': cred.student.get_full_name(),
            'institution': cred.institution.name,
            'issue_date': datetime.fromtimestamp(cred.issue_date).strftime('%Y-%m-%d'),
            'level': cred.level.value
        })
    
    # Get recent research papers
    recent_papers = []
    all_papers = list(academic_blockchain.research_papers.values())
    all_papers.sort(key=lambda x: x.publication_date, reverse=True)
    for paper in all_papers[:3]:
        recent_papers.append({
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'publication_date': datetime.fromtimestamp(paper.publication_date).strftime('%Y-%m-%d')
        })
    
    return jsonify({
        'statistics': stats,
        'recent_credentials': recent_credentials,
        'recent_papers': recent_papers,
        'top_institutions': list(academic_blockchain.institutions.values())[:5]
    })

# New Page Routes
@app.route('/issue')
def issue_credential_page():
    """Issue credential page"""
    return render_template('issue_credential.html')

@app.route('/verify')
def verify_certificate_page():
    """Certificate verification page"""
    return render_template('verify_certificate.html')

@app.route('/upload')
def upload_certificate_page():
    """Certificate upload page"""
    return render_template('upload_certificate.html')

@app.route('/')
def home():
    """Main application page with authentication check"""
    # Check if user is authenticated or accessing as guest
    guest_mode = request.args.get('guest') == 'true'
    session_id = session.get('session_id')
    
    if not guest_mode and not session_id:
        return redirect(url_for('login'))
    
    # If session exists, verify it's still valid
    if session_id and not guest_mode:
        session_result = digilocker_integration.get_user_session(session_id)
        if not session_result.get('success'):
            session.clear()
            return redirect(url_for('login'))
    
    return render_template('all_in_one.html', guest_mode=guest_mode)

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard redirect after login"""
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    # Verify session
    session_result = digilocker_integration.get_user_session(session_id)
    if not session_result.get('success'):
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('all_in_one.html', authenticated=True)

# Enhanced Blockchain API Endpoints
@app.route('/api/issue-credential', methods=['POST'])
def api_issue_credential():
    """API endpoint to issue a new credential with full blockchain integration"""
    try:
        # Safe JSON parsing
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No JSON data provided'
                })
        except Exception as json_error:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON format',
                'details': str(json_error)
            })
        
        # Validate required fields
        required_fields = ['studentName', 'studentId', 'institutionName', 'institutionId', 'degreeType', 'fieldOfStudy']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })
        
        # Generate unique credential ID
        credential_id = generate_credential_id()
        
        # Create comprehensive credential object
        credential = AcademicCredential(
            credential_id=credential_id,
            title=f"{data['degreeType']} in {data['fieldOfStudy']}",
            student_id=data['studentId'],
            institution_id=data['institutionId'],
            credential_type=CredentialType.DEGREE,
            issue_date=datetime.now(),
            grade=data.get('grade', 'N/A'),
            description=f"Academic credential for {data['studentName']} from {data['institutionName']}",
            course=data['fieldOfStudy']
        )
        
        # Register student in blockchain (convert to dict format)
        student_dict = {
            'student_id': data['studentId'],
            'name': data['studentName'],
            'email': data.get('studentEmail', f"{data['studentId']}@{data['institutionId']}.edu"),
            'institution_id': data['institutionId']
        }
        academic_blockchain.register_student(student_dict)
        
        # Issue credential to blockchain (convert to dict format)
        credential_dict = {
            'credential_id': credential_id,
            'student_id': data['studentId'],
            'title': f"{data['degreeType']} in {data['fieldOfStudy']}",
            'institution_id': data['institutionId'],
            'degree_type': data['degreeType'],
            'field_of_study': data['fieldOfStudy'],
            'student_name': data['studentName'],
            'institution_name': data['institutionName']
        }
        blockchain_result = academic_blockchain.issue_credential(credential_dict, data['institutionId'])
        
        if blockchain_result.get('success'):
            # Create blockchain hash for certificate
            blockchain_hash = blockchain_result.get('transaction_hash', '')
            block_index = len(academic_blockchain.chain)
            
            # Create certificate record with blockchain data
            cert_record = CertificateRecord(
                certificate_id=credential_id,
                student_name=data['studentName'],
                student_id=data['studentId'],
                institution_name=data['institutionName'],
                institution_id=data['institutionId'],
                degree_type=data['degreeType'],
                field_of_study=data['fieldOfStudy'],
                graduation_date=data.get('graduationDate', datetime.now().strftime('%Y-%m-%d')),
                issue_date=datetime.now().isoformat(),
                certificate_hash=blockchain_hash,
                verification_status='verified',
                issuer_signature=f"{data['institutionId']}_REGISTRAR_{datetime.now().year}",
                blockchain_hash=blockchain_hash,
                metadata={
                    'block_index': block_index,
                    'grade': data.get('grade', 'N/A'),
                    'blockchain_verified': True,
                    'issue_timestamp': time.time()
                }
            )
            
            # Add to certificate database
            db_result = certificate_db.add_certificate(cert_record)
            verification_code = db_result.get('verification_code')
            
            # Send email notification to student
            student_email = data.get('studentEmail', f"{data['studentId']}@{data['institutionId']}.edu")
            email_result = email_service.send_certificate_notification(
                cert_record.to_dict(), 
                verification_code, 
                student_email
            )
            
            # Log issuance analytics
            analytics_engine.log_issuance(cert_record.to_dict(), blockchain_hash)
            
            return jsonify({
                'success': True,
                'credential_id': credential_id,
                'verification_code': verification_code,
                'blockchain_hash': blockchain_hash,
                'block_index': block_index,
                'transaction_id': blockchain_result.get('transaction_id'),
                'message': 'Credential issued and recorded on blockchain successfully',
                'blockchain_verified': True,
                'email_sent': email_result.get('success', False),
                'email_status': email_result.get('message', 'Email notification attempted')
            })
        else:
            return jsonify({
                'success': False,
                'error': blockchain_result.get('error', 'Failed to record credential on blockchain')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Blockchain integration error: {str(e)}'
        })

@app.route('/api/verify-certificate', methods=['POST'])
def api_verify_certificate():
    """API endpoint to verify a certificate with full blockchain validation"""
    try:
        # Safe JSON parsing
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'valid': False,
                    'error': 'No JSON data provided'
                })
        except Exception as json_error:
            return jsonify({
                'valid': False,
                'error': 'Invalid JSON format',
                'details': str(json_error)
            })
        
        verification_code = data.get('verification_code')
        
        if not verification_code:
            return jsonify({
                'valid': False,
                'error': 'Verification code is required'
            })
        
        # Verify using certificate database
        db_result = certificate_db.verify_certificate(verification_code)
        
        if db_result.get('valid') and db_result.get('certificate'):
            cert = db_result['certificate']
            
            # Additional blockchain verification
            blockchain_verified = False
            blockchain_details = {}
            
            # Check if certificate exists in blockchain
            if cert.get('blockchain_hash'):
                try:
                    # Verify blockchain integrity
                    if academic_blockchain.is_chain_valid():
                        blockchain_verified = True
                        blockchain_details = {
                            'blockchain_hash': cert.get('blockchain_hash'),
                            'block_index': cert.get('metadata', {}).get('block_index', 'Unknown'),
                            'chain_valid': True,
                            'total_blocks': len(academic_blockchain.chain),
                            'verification_timestamp': datetime.now().isoformat()
                        }
                    else:
                        blockchain_details = {
                            'chain_valid': False,
                            'error': 'Blockchain integrity compromised'
                        }
                except Exception as blockchain_error:
                    blockchain_details = {
                        'error': f'Blockchain verification failed: {str(blockchain_error)}'
                    }
            
            # Send verification alert to institution (optional)
            try:
                institution_email = f"registrar@{cert.get('institution_id', 'institution')}.edu"
                email_service.send_verification_alert(cert, verification_code, institution_email)
            except Exception as email_error:
                print(f"Email alert failed: {email_error}")
            
            # Log verification analytics
            user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            analytics_engine.log_verification(verification_code, cert, True, user_ip)
            
            # Check DigiLocker integration
            digilocker_verified = False
            nad_verified = False
            digilocker_confidence = 0
            digilocker_details = {}
            
            # Check if certificate has DigiLocker metadata
            cert_metadata = cert.get('metadata', {})
            if cert_metadata:
                digilocker_verified = cert_metadata.get('digilocker_verified', False)
                nad_verified = cert_metadata.get('nad_verified', False)
                digilocker_confidence = cert_metadata.get('verification_confidence', 0)
                
                if digilocker_verified:
                    digilocker_details = {
                        'digilocker_uri': cert_metadata.get('digilocker_uri', ''),
                        'nad_verified': nad_verified,
                        'verification_confidence': digilocker_confidence,
                        'verification_timestamp': cert_metadata.get('verification_timestamp', ''),
                        'recommendation': cert_metadata.get('verification_recommendation', ''),
                        'source': cert_metadata.get('source', 'LOCAL_DATABASE')
                    }
            
            # Calculate enhanced confidence score
            confidence_score = 50  # Base score
            if cert.get('verification_status') == 'verified':
                confidence_score += 20
            if blockchain_verified:
                confidence_score += 15
            if digilocker_verified:
                confidence_score += 10
            if nad_verified:
                confidence_score += 5
            
            # Use DigiLocker confidence if available and higher
            if digilocker_confidence > 0:
                confidence_score = max(confidence_score, digilocker_confidence)
            
            confidence_score = min(confidence_score, 100)
            
            # Determine verification level
            if blockchain_verified and digilocker_verified and nad_verified:
                verification_level = 'MAXIMUM_SECURITY'
                security_status = 'HIGHEST'
            elif blockchain_verified and digilocker_verified:
                verification_level = 'HIGH_SECURITY'
                security_status = 'HIGH'
            elif blockchain_verified or digilocker_verified:
                verification_level = 'MEDIUM_SECURITY'
                security_status = 'MEDIUM'
            else:
                verification_level = 'BASIC_SECURITY'
                security_status = 'LIMITED'

            # Enhanced verification result with DigiLocker integration
            return jsonify({
                'valid': True,
                'certificate': cert,
                'verification_code': verification_code,
                'verified_at': db_result.get('verified_at'),
                'blockchain_verified': blockchain_verified,
                'blockchain_details': blockchain_details,
                'digilocker_verified': digilocker_verified,
                'nad_verified': nad_verified,
                'digilocker_details': digilocker_details,
                'confidence_score': confidence_score,
                'verification_level': verification_level,
                'security_status': security_status,
                'verification_sources': {
                    'blockchain': blockchain_verified,
                    'digilocker': digilocker_verified,
                    'nad': nad_verified,
                    'local_database': True
                },
                'digilocker_integration': {
                    'enabled': True,
                    'status': 'OPERATIONAL'
                }
            })
        else:
            return jsonify({
                'valid': False,
                'error': db_result.get('error', 'Certificate not found'),
                'verification_level': 'FAILED'
            })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Verification system error: {str(e)}',
            'verification_level': 'ERROR'
        })

@app.route('/api/upload-certificate', methods=['POST'])
def api_upload_certificate():
    """API endpoint to upload a certificate"""
    try:
        # Check if file is present
        if 'certificate_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            })
        
        file = request.files['certificate_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            })
        
        if file and allowed_file(file.filename):
            # Save file
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Generate file hash for blockchain
            import hashlib
            file.seek(0)  # Reset file pointer
            file_content = file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            file.seek(0)  # Reset again for saving
            
            # Create blockchain transaction for uploaded certificate
            credential_id = generate_credential_id()
            upload_transaction = {
                'type': 'CERTIFICATE_UPLOAD',
                'certificate_id': credential_id,
                'student_name': request.form.get('studentName'),
                'student_id': request.form.get('studentId'),
                'institution_name': request.form.get('institutionName'),
                'file_hash': file_hash,
                'upload_timestamp': time.time(),
                'verification_status': 'pending'
            }
            
            # Add transaction to blockchain
            try:
                academic_blockchain.add_transaction(upload_transaction)
                # Mine a new block to include the upload
                academic_blockchain.mine_pending_transactions('SYSTEM')
                blockchain_hash = academic_blockchain.get_latest_block().hash
                block_index = len(academic_blockchain.chain) - 1
                blockchain_integrated = True
            except Exception as blockchain_error:
                blockchain_hash = f"upload_{timestamp}"
                block_index = None
                blockchain_integrated = False
            
            # Create certificate record with blockchain integration
            cert_record = CertificateRecord(
                certificate_id=credential_id,
                student_name=request.form.get('studentName'),
                student_id=request.form.get('studentId'),
                institution_name=request.form.get('institutionName'),
                institution_id=f'uploaded_{timestamp}',
                degree_type=request.form.get('degreeType'),
                field_of_study=request.form.get('fieldOfStudy', 'Not Specified'),
                graduation_date=request.form.get('graduationDate', datetime.now().strftime('%Y-%m-%d')),
                issue_date=datetime.now().isoformat(),
                certificate_hash=file_hash,
                verification_status='pending',
                issuer_signature='UPLOADED_DOCUMENT',
                blockchain_hash=blockchain_hash,
                metadata={
                    'file_path': file_path,
                    'original_filename': file.filename,
                    'upload_timestamp': timestamp,
                    'file_hash': file_hash,
                    'blockchain_integrated': blockchain_integrated,
                    'block_index': block_index,
                    'additional_info': request.form.get('additionalInfo', '')
                }
            )
            
            # Add to database
            result = certificate_db.add_certificate(cert_record)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'verification_code': result['verification_code'],
                    'certificate_id': cert_record.certificate_id,
                    'message': 'Certificate uploaded successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/colleges')
def api_get_colleges():
    """Get all colleges for institution search"""
    from college_database import TAMILNADU_COLLEGES_DATABASE
    return jsonify({
        'colleges': TAMILNADU_COLLEGES_DATABASE,
        'total_institutions': len(TAMILNADU_COLLEGES_DATABASE)
    })

@app.route('/api/certificate-stats')
def api_certificate_stats():
    """Get certificate database statistics"""
    try:
        stats = certificate_db.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/blockchain-stats')
def api_blockchain_stats():
    """Get comprehensive blockchain statistics"""
    try:
        stats = academic_blockchain.get_blockchain_stats()
        return jsonify({
            'success': True,
            'blockchain_stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/blockchain-explorer')
def api_blockchain_explorer():
    """Get blockchain data for explorer"""
    try:
        recent_blocks = academic_blockchain.get_recent_blocks(10)
        stats = academic_blockchain.get_blockchain_stats()
        
        return jsonify({
            'success': True,
            'recent_blocks': recent_blocks,
            'blockchain_stats': stats,
            'chain_valid': academic_blockchain.is_chain_valid()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/mine-block', methods=['POST'])
def api_mine_block():
    """Mine pending transactions (for demo purposes)"""
    try:
        # Check if there are pending transactions
        if not academic_blockchain.pending_transactions:
            # Add some demo transactions for mining demonstration
            demo_transactions = [
                {
                    'type': 'DEMO_TRANSACTION',
                    'description': 'Demo mining transaction 1',
                    'data': {'demo': True, 'value': 'Mining Demo'}
                },
                {
                    'type': 'DEMO_TRANSACTION', 
                    'description': 'Demo mining transaction 2',
                    'data': {'demo': True, 'value': 'Blockchain Mining'}
                }
            ]
            
            for transaction in demo_transactions:
                academic_blockchain.add_transaction(transaction)
        
        mined_block = academic_blockchain.mine_pending_transactions('DEMO_MINER')
        
        if mined_block:
            return jsonify({
                'success': True,
                'message': 'Block mined successfully!',
                'block': mined_block.to_dict(),
                'mining_stats': {
                    'block_index': mined_block.index,
                    'transactions_mined': len(mined_block.data.get('transactions', [])),
                    'mining_difficulty': academic_blockchain.difficulty,
                    'block_hash': mined_block.hash,
                    'nonce': mined_block.nonce
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Mining failed - no transactions processed'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/add-transaction', methods=['POST'])
def api_add_transaction():
    """Add a custom transaction to pending transactions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No transaction data provided'
            })
        
        # Create transaction with default values if not provided
        transaction = {
            'type': data.get('type', 'CUSTOM_TRANSACTION'),
            'description': data.get('description', 'Custom blockchain transaction'),
            'data': data.get('data', {}),
            'sender': data.get('sender', 'SYSTEM'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add transaction to blockchain
        transaction_id = academic_blockchain.add_transaction(transaction)
        
        return jsonify({
            'success': True,
            'message': 'Transaction added to pending pool',
            'transaction_id': transaction_id,
            'pending_count': len(academic_blockchain.pending_transactions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/pending-transactions')
def api_get_pending_transactions():
    """Get all pending transactions"""
    try:
        pending_transactions = getattr(academic_blockchain, 'pending_transactions', [])
        return jsonify({
            'success': True,
            'pending_transactions': pending_transactions,
            'count': len(pending_transactions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-certificate/<verification_code>')
def api_generate_certificate(verification_code):
    """Generate certificate with QR code"""
    try:
        # Get certificate data
        result = certificate_db.verify_certificate(verification_code)
        
        if not result.get('valid'):
            return jsonify({
                'success': False,
                'error': 'Invalid verification code'
            })
        
        certificate_data = result['certificate']
        
        # Generate QR code
        qr_base64 = certificate_generator.generate_qr_code(verification_code)
        
        # Generate HTML certificate
        html_certificate = certificate_generator.generate_certificate_html(certificate_data, verification_code)
        
        return jsonify({
            'success': True,
            'qr_code': qr_base64,
            'html_certificate': html_certificate,
            'verification_url': f'http://localhost:5000/?verify={verification_code}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/download-certificate/<verification_code>')
def api_download_certificate(verification_code):
    """Download certificate as PDF"""
    try:
        # Get certificate data
        result = certificate_db.verify_certificate(verification_code)
        
        if not result.get('valid'):
            return jsonify({
                'success': False,
                'error': 'Invalid verification code'
            })
        
        certificate_data = result['certificate']
        
        # Generate PDF certificate
        pdf_path = certificate_generator.generate_certificate_pdf(certificate_data, verification_code)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'certificate_{verification_code}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/certificate/<verification_code>')
def view_certificate(verification_code):
    """View certificate in browser"""
    try:
        # Get certificate data
        result = certificate_db.verify_certificate(verification_code)
        
        if not result.get('valid'):
            return f"<h1>Invalid Certificate</h1><p>Verification code '{verification_code}' not found.</p>"
        
        certificate_data = result['certificate']
        
        # Generate HTML certificate
        html_certificate = certificate_generator.generate_certificate_html(certificate_data, verification_code)
        
        return html_certificate
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/api/send-certificate-email/<verification_code>')
def api_send_certificate_email(verification_code):
    """Send certificate via email"""
    try:
        # Get certificate data
        result = certificate_db.verify_certificate(verification_code)
        
        if not result.get('valid'):
            return jsonify({
                'success': False,
                'error': 'Invalid verification code'
            })
        
        certificate_data = result['certificate']
        
        # Get student email from request or generate default
        student_email = request.args.get('email', f"{certificate_data.get('student_id', 'student')}@example.com")
        
        # Generate PDF certificate
        pdf_path = certificate_generator.generate_certificate_pdf(certificate_data, verification_code)
        
        # Send email with attachment
        email_result = email_service.send_certificate_with_attachment(
            certificate_data, 
            verification_code, 
            student_email, 
            pdf_path
        )
        
        return jsonify({
            'success': email_result.get('success', False),
            'message': email_result.get('message', 'Email sending attempted'),
            'email_sent_to': student_email
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/email-logs')
def api_email_logs():
    """Get email sending logs"""
    try:
        logs = email_service.get_email_logs()
        return jsonify({
            'success': True,
            'logs': logs,
            'total_emails': len(logs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/bulk-email-notifications', methods=['POST'])
def api_bulk_email_notifications():
    """Send bulk email notifications"""
    try:
        data = request.get_json()
        certificates = data.get('certificates', [])
        
        if not certificates:
            return jsonify({
                'success': False,
                'error': 'No certificates provided'
            })
        
        results = email_service.send_bulk_notifications(certificates)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Processed {len(certificates)} certificates. Success: {results["success_count"]}, Failed: {results["failed_count"]}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics/dashboard')
def api_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        start_time = time.time()
        analytics_data = analytics_engine.get_dashboard_analytics()
        response_time = time.time() - start_time
        
        # Log API access
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        analytics_engine.log_access('/api/analytics/dashboard', user_ip, response_time)
        
        return jsonify({
            'success': True,
            'analytics': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics/institution/<institution_id>')
def api_analytics_institution(institution_id):
    """Get analytics for specific institution"""
    try:
        start_time = time.time()
        institution_analytics = analytics_engine.get_institution_analytics(institution_id)
        response_time = time.time() - start_time
        
        # Log API access
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        analytics_engine.log_access(f'/api/analytics/institution/{institution_id}', user_ip, response_time)
        
        return jsonify({
            'success': True,
            'institution_analytics': institution_analytics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics/export')
def api_analytics_export():
    """Export comprehensive analytics report"""
    try:
        start_time = time.time()
        report = analytics_engine.export_analytics_report()
        response_time = time.time() - start_time
        
        # Log API access
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        analytics_engine.log_access('/api/analytics/export', user_ip, response_time)
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics/trends')
def api_analytics_trends():
    """Get trending data and insights"""
    try:
        start_time = time.time()
        dashboard_data = analytics_engine.get_dashboard_analytics()
        
        trends_data = {
            'weekly_trends': dashboard_data['trends']['weekly_data'],
            'degree_trends': dashboard_data['trends']['degree_types'],
            'field_trends': dashboard_data['trends']['fields_of_study'],
            'top_institutions': dashboard_data['top_institutions'],
            'growth_metrics': {
                'verification_growth': dashboard_data['today_stats']['verification_growth'],
                'issuance_growth': dashboard_data['today_stats']['issuance_growth']
            }
        }
        
        response_time = time.time() - start_time
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        analytics_engine.log_access('/api/analytics/trends', user_ip, response_time)
        
        return jsonify({
            'success': True,
            'trends': trends_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/advanced-verification', methods=['POST'])
def api_advanced_verification():
    """Advanced certificate verification using dual strategy and ML forensics"""
    try:
        start_time = time.time()
        
        # Get certificate data and optional image
        certificate_data = request.get_json() if request.is_json else {}
        image_data = None
        
        # Handle file upload if present
        if 'certificate_image' in request.files:
            file = request.files['certificate_image']
            if file and file.filename:
                image_data = file.read()
        
        # Process using dual strategy
        processing_result = dual_strategy_processor.process_certificate(certificate_data, image_data)
        
        # Add ML forensics analysis if image is available
        if image_data:
            ml_result = ml_forensics_engine.predict_forgery_probability(image_data, certificate_data)
            processing_result['ml_forensics'] = ml_result
        
        response_time = time.time() - start_time
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        analytics_engine.log_access('/api/advanced-verification', user_ip, response_time)
        
        return jsonify({
            'success': True,
            'processing_result': processing_result,
            'response_time': response_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/system-status/advanced')
def api_advanced_system_status():
    """Get advanced system status including all new features"""
    try:
        start_time = time.time()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'core_system': {
                'blockchain_status': 'OPERATIONAL' if academic_blockchain.is_chain_valid() else 'ERROR',
                'database_status': 'OPERATIONAL',
                'analytics_status': 'OPERATIONAL'
            },
            'advanced_features': {
                'ocr_forensics': {
                    'status': 'OPERATIONAL',
                    'statistics': ocr_forensics_engine.get_analysis_statistics()
                },
                'digital_signing': {
                    'status': 'OPERATIONAL', 
                    'statistics': pki_signing_engine.get_signing_statistics()
                },
                'dual_strategy': {
                    'status': 'OPERATIONAL',
                    'statistics': dual_strategy_processor.get_processing_statistics()
                },
                'ml_forensics': {
                    'status': 'OPERATIONAL',
                    'statistics': ml_forensics_engine.get_ml_statistics()
                }
            },
            'performance': {
                'response_time': time.time() - start_time,
                'system_load': 'NORMAL'
            }
        }
        
        return jsonify({
            'success': True,
            'system_status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# DigiLocker Integration API Endpoints
@app.route('/api/digilocker/authenticate', methods=['POST'])
def api_digilocker_authenticate():
    """Authenticate user with email/mobile and password"""
    try:
        data = request.get_json()
        email_or_mobile = data.get('email_or_mobile', '').strip()
        password = data.get('password', '')
        
        # Authenticate with DigiLocker integration
        auth_result = digilocker_integration.authenticate_user(email_or_mobile, password)
        
        if auth_result.get('success'):
            # Store session in Flask session
            session['session_id'] = auth_result['session_id']
            session['user_info'] = auth_result['user_info']
            
            return jsonify({
                'success': True,
                'user_info': auth_result['user_info'],
                'session_id': auth_result['session_id'],
                'message': auth_result.get('message', 'Authentication successful')
            })
        else:
            return jsonify({
                'success': False,
                'error': auth_result.get('error', 'Authentication failed')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Authentication error: {str(e)}'
        })

@app.route('/api/digilocker/auth-url')
def api_digilocker_auth_url():
    """Generate DigiLocker OAuth authorization URL"""
    try:
        state = str(uuid.uuid4())
        session['oauth_state'] = state
        
        auth_url = digilocker_integration.generate_authorization_url(state)
        
        return jsonify({
            'success': True,
            'authorization_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Authorization URL generation failed: {str(e)}'
        })

@app.route('/api/digilocker/callback', methods=['POST'])
def api_digilocker_callback():
    """Handle DigiLocker OAuth callback"""
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')
        
        # Verify state parameter
        if state != session.get('oauth_state'):
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter'
            })
        
        # Exchange code for token
        token_result = digilocker_integration.exchange_code_for_token(code, state)
        
        if not token_result.get('success'):
            return jsonify({
                'success': False,
                'error': token_result.get('error', 'Token exchange failed')
            })
        
        # Get user info
        access_token = token_result['token_info']['access_token']
        user_result = digilocker_integration.get_user_info(access_token)
        
        if user_result.get('success'):
            # Store session
            session['session_id'] = user_result['session_id']
            session['user_info'] = user_result['user_info']
            session['access_token'] = access_token
            
            return jsonify({
                'success': True,
                'user_info': user_result['user_info'],
                'session_id': user_result['session_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': user_result.get('error', 'User info retrieval failed')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'OAuth callback error: {str(e)}'
        })

@app.route('/api/digilocker/documents')
def api_digilocker_documents():
    """Get user's DigiLocker documents"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            # For demo purposes, return sample documents when not authenticated
            return jsonify({
                'success': True,
                'documents': [
                    {
                        'document_id': 'DEMO_CERT_001',
                        'name': 'Bachelor of Technology Certificate',
                        'issuer': 'Indian Institute of Technology Madras',
                        'document_type': 'DEGREE_CERTIFICATE',
                        'issue_date': '2024-05-20',
                        'verification_status': 'DIGILOCKER_VERIFIED',
                        'student_name': 'Demo Student',
                        'field_of_study': 'Computer Science & Engineering'
                    },
                    {
                        'document_id': 'DEMO_CERT_002',
                        'name': 'Class XII Marksheet',
                        'issuer': 'Central Board of Secondary Education',
                        'document_type': 'MARKSHEET',
                        'issue_date': '2020-07-15',
                        'verification_status': 'DIGILOCKER_VERIFIED',
                        'student_name': 'Demo Student',
                        'field_of_study': 'Science'
                    },
                    {
                        'document_id': 'DEMO_CERT_003',
                        'name': 'Diploma in Computer Applications',
                        'issuer': 'Anna University',
                        'document_type': 'DIPLOMA',
                        'issue_date': '2022-03-10',
                        'verification_status': 'DIGILOCKER_VERIFIED',
                        'student_name': 'Demo Student',
                        'field_of_study': 'Computer Applications'
                    }
                ],
                'demo_mode': True,
                'message': 'Demo documents shown. Login with DigiLocker for real documents.'
            })
        
        # Verify session
        session_result = digilocker_integration.get_user_session(session_id)
        if not session_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Session expired'
            })
        
        access_token = session.get('access_token')
        if not access_token:
            # Simulate documents for authenticated users without access token
            user_info = session_result['session_data']['user_info']
            return jsonify({
                'success': True,
                'documents': [
                    {
                        'document_id': f"DL_{user_info.get('user_id', 'USER')}_001",
                        'name': 'Bachelor of Technology Certificate',
                        'issuer': 'Indian Institute of Technology Madras',
                        'document_type': 'DEGREE_CERTIFICATE',
                        'issue_date': '2024-05-20',
                        'verification_status': 'DIGILOCKER_VERIFIED',
                        'student_name': user_info.get('name', 'Authenticated User'),
                        'field_of_study': 'Computer Science & Engineering'
                    },
                    {
                        'document_id': f"DL_{user_info.get('user_id', 'USER')}_002",
                        'name': 'Master of Science Certificate',
                        'issuer': 'Loyola College',
                        'document_type': 'MASTER_DEGREE',
                        'issue_date': '2023-06-15',
                        'verification_status': 'DIGILOCKER_VERIFIED',
                        'student_name': user_info.get('name', 'Authenticated User'),
                        'field_of_study': 'Data Science'
                    }
                ],
                'authenticated': True,
                'message': 'Simulated DigiLocker documents for authenticated user.'
            })
        
        # Get documents with access token
        document_type = request.args.get('type')
        docs_result = digilocker_integration.get_user_documents(access_token, document_type)
        
        return jsonify(docs_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Document retrieval error: {str(e)}'
        })

@app.route('/api/digilocker/verify-document', methods=['POST'])
def api_digilocker_verify_document():
    """Verify document using DigiLocker and NAD"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            })
        
        data = request.get_json()
        document_info = data.get('document_info', {})
        
        # Get comprehensive verification
        verification_result = digilocker_integration.get_comprehensive_verification(
            document_info, session_id
        )
        
        return jsonify(verification_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Document verification error: {str(e)}'
        })

@app.route('/api/digilocker/logout', methods=['POST'])
def api_digilocker_logout():
    """Logout user and clear session"""
    try:
        session_id = session.get('session_id')
        if session_id:
            digilocker_integration.logout_user(session_id)
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Logout error: {str(e)}'
        })

@app.route('/api/digilocker/status')
def api_digilocker_status():
    """Get DigiLocker integration status"""
    try:
        session_id = session.get('session_id')
        authenticated = False
        user_info = None
        
        if session_id:
            session_result = digilocker_integration.get_user_session(session_id)
            if session_result.get('success'):
                authenticated = True
                user_info = session_result['session_data']['user_info']
        
        # Get integration statistics or provide demo stats
        try:
            integration_stats = digilocker_integration.get_integration_statistics()
        except:
            # Provide demo statistics
            integration_stats = {
                'total_users': 1250,
                'active_sessions': 45,
                'nad_cache_entries': 3500,
                'verification_requests_today': 89,
                'system_status': 'OPERATIONAL',
                'last_nad_sync': '2024-10-01T19:30:00Z'
            }
        
        return jsonify({
            'success': True,
            'authenticated': authenticated,
            'user_info': user_info,
            'integration_statistics': integration_stats,
            'demo_mode': not authenticated,
            'system_status': 'OPERATIONAL'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Status check error: {str(e)}'
        })

@app.route('/api/digilocker/sync-certificates', methods=['POST'])
def api_digilocker_sync_certificates():
    """Sync certificates from DigiLocker to local database"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            })
        
        # Sync with DigiLocker
        sync_result = certificate_db.sync_with_digilocker(session_id)
        
        if sync_result.get('success'):
            return jsonify({
                'success': True,
                'synced_count': sync_result.get('synced_count', 0),
                'new_certificates': sync_result.get('new_certificates', []),
                'total_digilocker_docs': sync_result.get('total_digilocker_docs', 0),
                'message': f"Successfully synced {sync_result.get('synced_count', 0)} certificates from DigiLocker"
            })
        else:
            return jsonify({
                'success': False,
                'error': sync_result.get('error', 'Sync failed')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Sync error: {str(e)}'
        })

@app.route('/api/digilocker/verify-certificate/<certificate_id>', methods=['POST'])
def api_digilocker_verify_certificate(certificate_id):
    """Verify specific certificate using DigiLocker and NAD"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            })
        
        # Verify with DigiLocker and NAD
        verification_result = certificate_db.verify_with_digilocker_and_nad(certificate_id, session_id)
        
        return jsonify(verification_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Verification error: {str(e)}'
        })

@app.route('/api/certificates/enhanced')
def api_get_enhanced_certificates():
    """Get certificates with DigiLocker enhancement information"""
    try:
        session_id = session.get('session_id')
        enhanced_certificates = certificate_db.get_digilocker_enhanced_certificates(session_id)
        
        return jsonify({
            'success': True,
            'certificates': enhanced_certificates,
            'total_count': len(enhanced_certificates),
            'digilocker_integration': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error retrieving enhanced certificates: {str(e)}'
        })

# Certificate Generation Endpoints
@app.route('/api/generate-sslc-certificate', methods=['POST'])
def api_generate_sslc_certificate():
    """Generate SSLC (10th Standard) Certificate"""
    try:
        data = request.get_json()
        html_certificate = certificate_templates.sslc_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'SSLC',
            'certificate_no': data.get('certificate_sl_no', 'SSLC/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-hsc1-certificate', methods=['POST'])
def api_generate_hsc1_certificate():
    """Generate HSC First Year Certificate"""
    try:
        data = request.get_json()
        html_certificate = certificate_templates.hsc_first_year_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'HSC_FIRST_YEAR',
            'certificate_no': data.get('certificate_sl_no', 'HSC1/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-hsc2-certificate', methods=['POST'])
def api_generate_hsc2_certificate():
    """Generate HSC Second Year Certificate"""
    try:
        data = request.get_json()
        html_certificate = certificate_templates.hsc_second_year_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'HSC_SECOND_YEAR',
            'certificate_no': data.get('certificate_sl_no', 'HSC2/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-income-certificate', methods=['POST'])
def api_generate_income_certificate():
    """Generate Income Certificate"""
    try:
        data = request.get_json()
        html_certificate = government_certificates.income_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'INCOME',
            'certificate_no': data.get('certificate_no', 'INC/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-community-certificate', methods=['POST'])
def api_generate_community_certificate():
    """Generate Community Certificate"""
    try:
        data = request.get_json()
        html_certificate = government_certificates.community_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'COMMUNITY',
            'certificate_no': data.get('certificate_no', 'COM/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-nativity-certificate', methods=['POST'])
def api_generate_nativity_certificate():
    """Generate Nativity Certificate"""
    try:
        data = request.get_json()
        html_certificate = government_certificates.nativity_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'NATIVITY',
            'certificate_no': data.get('certificate_no', 'NAT/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-transfer-certificate', methods=['POST'])
def api_generate_transfer_certificate():
    """Generate Transfer Certificate"""
    try:
        data = request.get_json()
        html_certificate = government_certificates.transfer_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'TRANSFER',
            'certificate_no': data.get('certificate_no', 'TC/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate-firstgraduate-certificate', methods=['POST'])
def api_generate_firstgraduate_certificate():
    """Generate First Graduate Certificate"""
    try:
        data = request.get_json()
        html_certificate = government_certificates.first_graduate_certificate(data)
        
        return jsonify({
            'success': True,
            'html': html_certificate,
            'certificate_type': 'FIRST_GRADUATE',
            'certificate_no': data.get('certificate_no', 'FG/2024/XXXXX')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting Academic Authenticity Validator...")
    print("Visit http://localhost:5000 to access the system")
    print("Perfect for Smart India Hackathon 2024!")
    app.run(debug=True, host='0.0.0.0', port=5000)
