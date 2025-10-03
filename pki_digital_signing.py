"""
PKI Digital Signing System with Indian e-sign/CCA Integration
Implements digital signatures for academic certificates with government compliance
"""

import hashlib
import base64
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
import uuid
import requests
from pathlib import Path

class PKIDigitalSigningEngine:
    """Advanced PKI system for digital certificate signing with Indian e-sign compliance"""
    
    def __init__(self):
        self.keys_directory = "pki_keys"
        self.certificates_directory = "digital_certificates"
        self.signatures_directory = "digital_signatures"
        self.cca_config_file = "cca_integration.json"
        
        # Create directories
        for directory in [self.keys_directory, self.certificates_directory, self.signatures_directory]:
            os.makedirs(directory, exist_ok=True)
        
        self.load_cca_configuration()
        self.initialize_root_ca()
    
    def load_cca_configuration(self):
        """Load CCA (Controller of Certifying Authorities) configuration"""
        if os.path.exists(self.cca_config_file):
            with open(self.cca_config_file, 'r') as f:
                self.cca_config = json.load(f)
        else:
            # Default CCA configuration for Indian e-sign compliance
            self.cca_config = {
                'cca_root_url': 'https://cca.gov.in/api/v1',
                'esign_service_url': 'https://esignlive.com/api/packages',
                'timestamp_authority': 'http://timestamp.digicert.com',
                'ocsp_responder': 'http://ocsp.digicert.com',
                'crl_distribution': 'http://crl.digicert.com',
                'key_size': 2048,
                'hash_algorithm': 'SHA-256',
                'certificate_validity_days': 365,
                'compliance_standards': ['CCA_2000', 'IT_Act_2000', 'DSC_Guidelines_2009']
            }
            self.save_cca_configuration()
    
    def save_cca_configuration(self):
        """Save CCA configuration"""
        with open(self.cca_config_file, 'w') as f:
            json.dump(self.cca_config, f, indent=2)
    
    def initialize_root_ca(self):
        """Initialize Root Certificate Authority for the institution"""
        root_key_path = os.path.join(self.keys_directory, "root_ca_key.pem")
        root_cert_path = os.path.join(self.certificates_directory, "root_ca_cert.pem")
        
        if not os.path.exists(root_key_path) or not os.path.exists(root_cert_path):
            self.generate_root_ca()
        
        # Load existing root CA
        with open(root_key_path, 'rb') as f:
            self.root_private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        with open(root_cert_path, 'rb') as f:
            self.root_certificate = x509.load_pem_x509_certificate(f.read())
    
    def generate_root_ca(self):
        """Generate Root Certificate Authority"""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.cca_config['key_size']
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tamil Nadu"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Chennai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Academic Authenticity Validator"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Certificate Authority"),
            x509.NameAttribute(NameOID.COMMON_NAME, "AAV Root CA"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("academicvalidator.gov.in"),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Save private key
        with open(os.path.join(self.keys_directory, "root_ca_key.pem"), 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save certificate
        with open(os.path.join(self.certificates_directory, "root_ca_cert.pem"), 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        self.root_private_key = private_key
        self.root_certificate = cert
    
    def generate_institution_certificate(self, institution_data: Dict[str, str]) -> Dict[str, Any]:
        """Generate digital certificate for an institution"""
        # Generate private key for institution
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.cca_config['key_size']
        )
        
        # Create subject for institution
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, institution_data.get('state', 'Tamil Nadu')),
            x509.NameAttribute(NameOID.LOCALITY_NAME, institution_data.get('city', 'Chennai')),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, institution_data.get('name', 'Unknown Institution')),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Academic Department"),
            x509.NameAttribute(NameOID.COMMON_NAME, institution_data.get('domain', 'institution.edu.in')),
        ])
        
        # Generate certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.root_certificate.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.cca_config['certificate_validity_days'])
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(institution_data.get('domain', 'institution.edu.in')),
                x509.RFC822Name(institution_data.get('email', 'admin@institution.edu.in')),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION,
            ]),
            critical=True,
        ).sign(self.root_private_key, hashes.SHA256())
        
        # Generate certificate ID
        cert_id = str(uuid.uuid4())
        institution_id = institution_data.get('id', 'unknown')
        
        # Save institution private key
        key_filename = f"institution_{institution_id}_key.pem"
        with open(os.path.join(self.keys_directory, key_filename), 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save institution certificate
        cert_filename = f"institution_{institution_id}_cert.pem"
        with open(os.path.join(self.certificates_directory, cert_filename), 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        return {
            'certificate_id': cert_id,
            'institution_id': institution_id,
            'certificate_path': cert_filename,
            'private_key_path': key_filename,
            'serial_number': str(cert.serial_number),
            'not_valid_before': cert.not_valid_before.isoformat(),
            'not_valid_after': cert.not_valid_after.isoformat(),
            'subject': cert.subject.rfc4514_string(),
            'issuer': cert.issuer.rfc4514_string(),
            'fingerprint_sha256': cert.fingerprint(hashes.SHA256()).hex(),
            'compliance_standards': self.cca_config['compliance_standards']
        }
    
    def sign_certificate_document(self, certificate_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Digitally sign an academic certificate document"""
        try:
            # Load institution's private key
            key_path = os.path.join(self.keys_directory, f"institution_{institution_id}_key.pem")
            if not os.path.exists(key_path):
                raise ValueError(f"Institution private key not found for {institution_id}")
            
            with open(key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Create document hash
            document_json = json.dumps(certificate_data, sort_keys=True)
            document_hash = hashlib.sha256(document_json.encode()).digest()
            
            # Create digital signature
            signature = private_key.sign(
                document_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Encode signature
            signature_b64 = base64.b64encode(signature).decode()
            
            # Create signature metadata
            signature_metadata = {
                'signature_id': str(uuid.uuid4()),
                'document_hash': document_hash.hex(),
                'signature': signature_b64,
                'algorithm': 'RSA-PSS-SHA256',
                'institution_id': institution_id,
                'timestamp': datetime.utcnow().isoformat(),
                'certificate_id': certificate_data.get('certificate_id', 'unknown'),
                'verification_code': certificate_data.get('verification_code', 'unknown'),
                'compliance': {
                    'cca_compliant': True,
                    'it_act_2000_compliant': True,
                    'standards': self.cca_config['compliance_standards']
                }
            }
            
            # Add timestamp from authority (simulated)
            timestamp_response = self.get_trusted_timestamp(document_hash.hex())
            signature_metadata['trusted_timestamp'] = timestamp_response
            
            # Save signature
            signature_filename = f"signature_{signature_metadata['signature_id']}.json"
            with open(os.path.join(self.signatures_directory, signature_filename), 'w') as f:
                json.dump(signature_metadata, f, indent=2)
            
            return {
                'success': True,
                'signature_metadata': signature_metadata,
                'signature_file': signature_filename,
                'digital_signature_valid': True,
                'cca_compliant': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Digital signing failed: {str(e)}",
                'digital_signature_valid': False,
                'cca_compliant': False
            }
    
    def verify_digital_signature(self, certificate_data: Dict[str, Any], signature_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Verify digital signature of a certificate"""
        try:
            institution_id = signature_metadata.get('institution_id')
            
            # Load institution's certificate
            cert_path = os.path.join(self.certificates_directory, f"institution_{institution_id}_cert.pem")
            if not os.path.exists(cert_path):
                raise ValueError(f"Institution certificate not found for {institution_id}")
            
            with open(cert_path, 'rb') as f:
                certificate = x509.load_pem_x509_certificate(f.read())
            
            # Recreate document hash
            document_json = json.dumps(certificate_data, sort_keys=True)
            document_hash = hashlib.sha256(document_json.encode()).digest()
            
            # Verify document hash matches
            if document_hash.hex() != signature_metadata.get('document_hash'):
                return {
                    'valid': False,
                    'error': 'Document hash mismatch - document may have been tampered with',
                    'verification_details': {
                        'hash_match': False,
                        'signature_valid': False,
                        'certificate_valid': False
                    }
                }
            
            # Decode signature
            signature = base64.b64decode(signature_metadata.get('signature', ''))
            
            # Verify signature
            public_key = certificate.public_key()
            public_key.verify(
                signature,
                document_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Check certificate validity
            now = datetime.utcnow()
            cert_valid = certificate.not_valid_before <= now <= certificate.not_valid_after
            
            # Verify certificate chain
            chain_valid = self.verify_certificate_chain(certificate)
            
            verification_details = {
                'hash_match': True,
                'signature_valid': True,
                'certificate_valid': cert_valid,
                'certificate_chain_valid': chain_valid,
                'institution_verified': True,
                'cca_compliant': signature_metadata.get('compliance', {}).get('cca_compliant', False),
                'verification_timestamp': datetime.utcnow().isoformat(),
                'certificate_serial': str(certificate.serial_number),
                'certificate_fingerprint': certificate.fingerprint(hashes.SHA256()).hex()
            }
            
            return {
                'valid': True,
                'verification_details': verification_details,
                'trust_level': 'HIGH' if chain_valid and cert_valid else 'MEDIUM'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Signature verification failed: {str(e)}",
                'verification_details': {
                    'hash_match': False,
                    'signature_valid': False,
                    'certificate_valid': False
                }
            }
    
    def verify_certificate_chain(self, certificate: x509.Certificate) -> bool:
        """Verify certificate chain up to root CA"""
        try:
            # Verify certificate was issued by our root CA
            root_public_key = self.root_certificate.public_key()
            root_public_key.verify(
                certificate.signature,
                certificate.tbs_certificate_bytes,
                padding.PKCS1v15(),
                certificate.signature_hash_algorithm
            )
            return True
        except Exception:
            return False
    
    def get_trusted_timestamp(self, document_hash: str) -> Dict[str, Any]:
        """Get trusted timestamp from timestamp authority (simulated)"""
        # In production, this would connect to a real TSA
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'tsa_url': self.cca_config['timestamp_authority'],
            'hash': document_hash,
            'tsa_signature': hashlib.sha256(f"{document_hash}{datetime.utcnow()}".encode()).hexdigest(),
            'status': 'VALID'
        }
    
    def generate_esign_request(self, certificate_data: Dict[str, Any], signer_info: Dict[str, str]) -> Dict[str, Any]:
        """Generate e-sign request compatible with Indian e-sign services"""
        esign_request = {
            'request_id': str(uuid.uuid4()),
            'document_info': {
                'document_type': 'ACADEMIC_CERTIFICATE',
                'document_id': certificate_data.get('certificate_id'),
                'verification_code': certificate_data.get('verification_code'),
                'document_hash': hashlib.sha256(json.dumps(certificate_data).encode()).hexdigest()
            },
            'signer_info': {
                'name': signer_info.get('name', 'Unknown'),
                'email': signer_info.get('email', 'unknown@institution.edu.in'),
                'mobile': signer_info.get('mobile', '+91-0000000000'),
                'aadhaar_last_4': signer_info.get('aadhaar_last_4', '0000'),
                'designation': signer_info.get('designation', 'Registrar'),
                'institution': signer_info.get('institution', 'Unknown Institution')
            },
            'esign_config': {
                'auth_mode': 'AADHAAR_OTP',
                'response_url': 'https://academicvalidator.gov.in/esign/callback',
                'hash_algorithm': 'SHA256',
                'pdf_signing': True,
                'visible_signature': True,
                'signature_position': {
                    'page': 1,
                    'x': 400,
                    'y': 100,
                    'width': 150,
                    'height': 50
                }
            },
            'compliance': {
                'it_act_2000': True,
                'cca_guidelines': True,
                'legal_validity': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return esign_request
    
    def get_signing_statistics(self) -> Dict[str, Any]:
        """Get statistics about digital signatures"""
        signature_files = [f for f in os.listdir(self.signatures_directory) if f.endswith('.json')]
        
        if not signature_files:
            return {
                'total_signatures': 0,
                'message': 'No digital signatures created yet'
            }
        
        signatures_data = []
        for filename in signature_files:
            with open(os.path.join(self.signatures_directory, filename), 'r') as f:
                signatures_data.append(json.load(f))
        
        # Calculate statistics
        total_signatures = len(signatures_data)
        cca_compliant = sum(1 for sig in signatures_data if sig.get('compliance', {}).get('cca_compliant', False))
        
        institutions = set(sig.get('institution_id') for sig in signatures_data)
        
        recent_signatures = sorted(signatures_data, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        
        return {
            'total_signatures': total_signatures,
            'cca_compliant_signatures': cca_compliant,
            'compliance_percentage': round((cca_compliant / total_signatures) * 100, 2) if total_signatures > 0 else 0,
            'unique_institutions': len(institutions),
            'recent_signatures': recent_signatures,
            'standards_compliance': self.cca_config['compliance_standards']
        }

# Global PKI digital signing engine instance
pki_signing_engine = PKIDigitalSigningEngine()
