"""
Certificate Database for Academic Authenticity Validator
Handles certificate storage, verification, and management
"""

import json
import hashlib
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from digilocker_integration import digilocker_integration

@dataclass
class CertificateRecord:
    """Individual certificate record in the database"""
    certificate_id: str
    student_name: str
    student_id: str
    institution_name: str
    institution_id: str
    degree_type: str
    field_of_study: str
    graduation_date: str
    issue_date: str
    certificate_hash: str
    verification_status: str  # 'verified', 'pending', 'rejected'
    issuer_signature: str
    blockchain_hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CertificateRecord':
        return cls(**data)
    
    def generate_verification_code(self) -> str:
        """Generate a unique verification code for this certificate"""
        combined = f"{self.certificate_id}{self.student_id}{self.institution_id}{self.issue_date}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12].upper()

class CertificateDatabase:
    """Database for managing academic certificates"""
    
    def __init__(self, db_file: str = "certificates.json"):
        self.db_file = db_file
        self.certificates: Dict[str, CertificateRecord] = {}
        self.verification_codes: Dict[str, str] = {}  # code -> certificate_id mapping
        self.load_database()
    
    def load_database(self):
        """Load certificates from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    for cert_id, cert_data in data.get('certificates', {}).items():
                        self.certificates[cert_id] = CertificateRecord.from_dict(cert_data)
                    self.verification_codes = data.get('verification_codes', {})
            except Exception as e:
                print(f"Error loading database: {e}")
                self.certificates = {}
                self.verification_codes = {}
    
    def save_database(self):
        """Save certificates to JSON file"""
        try:
            data = {
                'certificates': {cert_id: cert.to_dict() for cert_id, cert in self.certificates.items()},
                'verification_codes': self.verification_codes,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def add_certificate(self, certificate: CertificateRecord) -> Dict[str, Any]:
        """Add a new certificate to the database"""
        if certificate.certificate_id in self.certificates:
            return {"success": False, "error": "Certificate ID already exists"}
        
        # Generate verification code
        verification_code = certificate.generate_verification_code()
        
        # Ensure unique verification code
        counter = 0
        original_code = verification_code
        while verification_code in self.verification_codes:
            counter += 1
            verification_code = f"{original_code}{counter:02d}"
        
        # Add to database
        self.certificates[certificate.certificate_id] = certificate
        self.verification_codes[verification_code] = certificate.certificate_id
        
        # Save to file
        self.save_database()
        
        return {
            "success": True,
            "certificate_id": certificate.certificate_id,
            "verification_code": verification_code,
            "message": "Certificate added successfully"
        }
    
    def verify_certificate(self, verification_code: str) -> Dict[str, Any]:
        """Verify a certificate using its verification code"""
        if verification_code not in self.verification_codes:
            return {
                "valid": False,
                "error": "Invalid verification code",
                "certificate": None
            }
        
        certificate_id = self.verification_codes[verification_code]
        certificate = self.certificates.get(certificate_id)
        
        if not certificate:
            return {
                "valid": False,
                "error": "Certificate not found in database",
                "certificate": None
            }
        
        return {
            "valid": True,
            "certificate": certificate.to_dict(),
            "verification_code": verification_code,
            "verified_at": datetime.now().isoformat()
        }
    
    def get_certificate_by_id(self, certificate_id: str) -> Optional[CertificateRecord]:
        """Get certificate by ID"""
        return self.certificates.get(certificate_id)
    
    def search_certificates(self, **kwargs) -> List[CertificateRecord]:
        """Search certificates by various criteria"""
        results = []
        for certificate in self.certificates.values():
            match = True
            for key, value in kwargs.items():
                if hasattr(certificate, key):
                    cert_value = getattr(certificate, key)
                    if isinstance(cert_value, str) and isinstance(value, str):
                        if value.lower() not in cert_value.lower():
                            match = False
                            break
                    elif cert_value != value:
                        match = False
                        break
            if match:
                results.append(certificate)
        return results
    
    def get_student_certificates(self, student_id: str) -> List[CertificateRecord]:
        """Get all certificates for a specific student"""
        return [cert for cert in self.certificates.values() if cert.student_id == student_id]
    
    def get_institution_certificates(self, institution_id: str) -> List[CertificateRecord]:
        """Get all certificates issued by a specific institution"""
        return [cert for cert in self.certificates.values() if cert.institution_id == institution_id]
    
    def update_verification_status(self, certificate_id: str, status: str) -> bool:
        """Update the verification status of a certificate"""
        if certificate_id in self.certificates:
            self.certificates[certificate_id].verification_status = status
            self.save_database()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_certificates = len(self.certificates)
        verified_count = len([c for c in self.certificates.values() if c.verification_status == 'verified'])
        pending_count = len([c for c in self.certificates.values() if c.verification_status == 'pending'])
        rejected_count = len([c for c in self.certificates.values() if c.verification_status == 'rejected'])
        
        # Get institution statistics
        institutions = {}
        for cert in self.certificates.values():
            if cert.institution_name not in institutions:
                institutions[cert.institution_name] = 0
            institutions[cert.institution_name] += 1
        
        # Get degree type statistics
        degree_types = {}
        for cert in self.certificates.values():
            if cert.degree_type not in degree_types:
                degree_types[cert.degree_type] = 0
            degree_types[cert.degree_type] += 1
        
        return {
            "total_certificates": total_certificates,
            "verified_certificates": verified_count,
            "pending_certificates": pending_count,
            "rejected_certificates": rejected_count,
            "institutions": institutions,
            "degree_types": degree_types,
            "verification_codes_issued": len(self.verification_codes)
        }
    
    def sync_with_digilocker(self, session_id: str) -> Dict[str, Any]:
        """Sync certificates with DigiLocker documents"""
        try:
            # Get user session
            session_result = digilocker_integration.get_user_session(session_id)
            if not session_result.get('success'):
                return {'success': False, 'error': 'Invalid session'}
            
            user_info = session_result['session_data']['user_info']
            
            # Simulate DigiLocker documents
            digilocker_docs = self._simulate_digilocker_documents(user_info)
            
            synced_count = 0
            new_certificates = []
            
            for doc in digilocker_docs:
                existing_cert = self._find_certificate_by_digilocker_uri(doc.get('digilocker_uri'))
                
                if not existing_cert:
                    certificate = self._create_certificate_from_digilocker_doc(doc, user_info)
                    if certificate:
                        result = self.add_certificate(certificate)
                        if result['success']:
                            synced_count += 1
                            new_certificates.append(certificate.certificate_id)
            
            return {
                'success': True,
                'synced_count': synced_count,
                'new_certificates': new_certificates,
                'total_digilocker_docs': len(digilocker_docs)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'DigiLocker sync error: {str(e)}'}
    
    def verify_with_digilocker_and_nad(self, certificate_id: str, session_id: str) -> Dict[str, Any]:
        """Verify certificate using DigiLocker and NAD integration"""
        try:
            certificate = self.get_certificate(certificate_id)
            if not certificate:
                return {'success': False, 'error': 'Certificate not found'}
            
            document_info = {
                'document_id': certificate.certificate_id,
                'name': f"{certificate.degree_type} - {certificate.field_of_study}",
                'issuer': certificate.institution_name,
                'document_type': certificate.degree_type.upper().replace(' ', '_'),
                'issue_date': certificate.issue_date,
                'verification_status': 'DIGILOCKER_VERIFIED',
                'source': 'LOCAL_DATABASE'
            }
            
            verification_result = digilocker_integration.get_comprehensive_verification(
                document_info, session_id
            )
            
            if verification_result.get('success'):
                verification_data = verification_result['verification_result']
                confidence = verification_data.get('overall_confidence', 0)
                
                if confidence > 80:
                    certificate.verification_status = 'verified'
                elif confidence > 50:
                    certificate.verification_status = 'pending'
                else:
                    certificate.verification_status = 'rejected'
                
                if not certificate.metadata:
                    certificate.metadata = {}
                
                certificate.metadata.update({
                    'digilocker_verified': True,
                    'nad_verified': verification_data.get('verification_sources', {}).get('nad', {}).get('nad_verified', False),
                    'verification_confidence': confidence,
                    'verification_timestamp': datetime.now().isoformat(),
                    'verification_recommendation': verification_data.get('recommendation', '')
                })
                
                self.save_database()
                
                return {
                    'success': True,
                    'verification_result': verification_data,
                    'updated_certificate': certificate.to_dict()
                }
            else:
                return verification_result
                
        except Exception as e:
            return {'success': False, 'error': f'Verification error: {str(e)}'}
    
    def _simulate_digilocker_documents(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate DigiLocker documents for the user"""
        user_name = user_info.get('name', 'Unknown User')
        
        return [
            {
                'document_id': f"DL_{uuid.uuid4().hex[:8].upper()}",
                'name': 'Bachelor of Technology Certificate',
                'issuer': 'Indian Institute of Technology Madras',
                'document_type': 'DEGREE_CERTIFICATE',
                'issue_date': '2024-05-20',
                'digilocker_uri': f"in.gov.iitm-BTCER-{uuid.uuid4().hex[:12]}",
                'verification_status': 'DIGILOCKER_VERIFIED',
                'student_name': user_name,
                'field_of_study': 'Computer Science & Engineering'
            }
        ]
    
    def _find_certificate_by_digilocker_uri(self, digilocker_uri: str) -> Optional[CertificateRecord]:
        """Find certificate by DigiLocker URI"""
        for certificate in self.certificates.values():
            if (certificate.metadata and 
                certificate.metadata.get('digilocker_uri') == digilocker_uri):
                return certificate
        return None
    
    def _create_certificate_from_digilocker_doc(self, doc: Dict[str, Any], user_info: Dict[str, Any]) -> Optional[CertificateRecord]:
        """Create certificate record from DigiLocker document"""
        try:
            certificate_id = f"DL_{doc['document_id']}"
            
            degree_type_mapping = {
                'DEGREE_CERTIFICATE': 'Bachelor of Technology',
                'MARKSHEET': 'Class XII Certificate',
                'DIPLOMA': 'Diploma'
            }
            
            degree_type = degree_type_mapping.get(doc.get('document_type', ''), 'Academic Certificate')
            
            certificate = CertificateRecord(
                certificate_id=certificate_id,
                student_name=doc.get('student_name', user_info.get('name', 'Unknown')),
                student_id=user_info.get('user_id', f"USR_{uuid.uuid4().hex[:8]}"),
                institution_name=doc.get('issuer', 'Unknown Institution'),
                institution_id=self._generate_institution_id(doc.get('issuer', '')),
                degree_type=degree_type,
                field_of_study=doc.get('field_of_study', 'General'),
                graduation_date=doc.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
                issue_date=doc.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
                certificate_hash=hashlib.sha256(f"{certificate_id}{doc.get('digilocker_uri', '')}".encode()).hexdigest()[:16],
                verification_status='verified',
                issuer_signature=f"DIGILOCKER_{datetime.now().year}",
                blockchain_hash=None,
                metadata={
                    'source': 'DIGILOCKER',
                    'digilocker_uri': doc.get('digilocker_uri'),
                    'digilocker_verified': True,
                    'original_document_type': doc.get('document_type'),
                    'sync_timestamp': datetime.now().isoformat()
                }
            )
            
            return certificate
            
        except Exception as e:
            print(f"Error creating certificate from DigiLocker doc: {e}")
            return None
    
    def _generate_institution_id(self, institution_name: str) -> str:
        """Generate institution ID from name"""
        institution_mapping = {
            'Indian Institute of Technology Madras': 'iitm_001',
            'Central Board of Secondary Education': 'cbse_001',
            'Anna University': 'anna_001',
            'Loyola College': 'loyola_001'
        }
        
        return institution_mapping.get(
            institution_name, 
            f"inst_{hashlib.sha256(institution_name.encode()).hexdigest()[:8]}"
        )

# Sample data for testing
SAMPLE_CERTIFICATES = [
    {
        "certificate_id": "CERT001",
        "student_name": "Rahul Sharma",
        "student_id": "STU2024001",
        "institution_name": "Indian Institute of Technology Madras (IIT Madras)",
        "institution_id": "iitm_001",
        "degree_type": "Bachelor of Technology",
        "field_of_study": "Computer Science & Engineering",
        "graduation_date": "2024-05-15",
        "issue_date": "2024-05-20",
        "certificate_hash": "abc123def456",
        "verification_status": "verified",
        "issuer_signature": "IITM_REGISTRAR_2024",
        "metadata": {"gpa": 8.5, "honors": "Magna Cum Laude"}
    },
    {
        "certificate_id": "CERT002",
        "student_name": "Priya Patel",
        "student_id": "STU2024002",
        "institution_name": "Loyola College",
        "institution_id": "loyola_001",
        "degree_type": "Master of Science",
        "field_of_study": "Data Science",
        "graduation_date": "2024-06-10",
        "issue_date": "2024-06-15",
        "certificate_hash": "def456ghi789",
        "verification_status": "verified",
        "issuer_signature": "LOYOLA_REGISTRAR_2024",
        "metadata": {"gpa": 9.2, "thesis": "Machine Learning in Healthcare"}
    },
    {
        "certificate_id": "CERT003",
        "student_name": "Arjun Kumar",
        "student_id": "STU2024003",
        "institution_name": "Anna University",
        "institution_id": "anna_001",
        "degree_type": "Bachelor of Engineering",
        "field_of_study": "Electronics and Communication",
        "graduation_date": "2024-04-30",
        "issue_date": "2024-05-05",
        "certificate_hash": "ghi789jkl012",
        "verification_status": "pending",
        "issuer_signature": "ANNA_REGISTRAR_2024",
        "metadata": {"gpa": 7.8}
    }
]

def initialize_sample_data():
    """Initialize database with sample certificates"""
    db = CertificateDatabase()
    
    for cert_data in SAMPLE_CERTIFICATES:
        certificate = CertificateRecord(**cert_data)
        result = db.add_certificate(certificate)
        print(f"Added certificate {cert_data['certificate_id']}: {result}")
    
    return db

if __name__ == "__main__":
    # Initialize with sample data for testing
    db = initialize_sample_data()
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(json.dumps(stats, indent=2))
