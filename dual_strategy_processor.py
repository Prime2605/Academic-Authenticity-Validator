"""
Dual Strategy Processor for Legacy vs New Certificates
Handles both traditional certificate verification and new blockchain-based certificates
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import base64
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import io

class CertificateType(Enum):
    LEGACY_PHYSICAL = "legacy_physical"
    LEGACY_DIGITAL = "legacy_digital"
    NEW_BLOCKCHAIN = "new_blockchain"
    HYBRID = "hybrid"

class VerificationMethod(Enum):
    OCR_FORENSICS = "ocr_forensics"
    DATABASE_LOOKUP = "database_lookup"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"
    DIGITAL_SIGNATURE = "digital_signature"
    HUMAN_REVIEW = "human_review"

class DualStrategyProcessor:
    """Processes both legacy and new certificates with appropriate verification methods"""
    
    def __init__(self):
        self.legacy_database_file = "legacy_certificates.json"
        self.verification_rules_file = "verification_rules.json"
        self.processing_stats_file = "processing_statistics.json"
        
        self.load_legacy_database()
        self.load_verification_rules()
        self.load_processing_stats()
    
    def load_legacy_database(self):
        """Load legacy certificate database"""
        if os.path.exists(self.legacy_database_file):
            with open(self.legacy_database_file, 'r') as f:
                self.legacy_database = json.load(f)
        else:
            self.legacy_database = {
                'certificates': [],
                'institutions': {},
                'verification_patterns': {},
                'last_updated': datetime.now().isoformat()
            }
            self.save_legacy_database()
    
    def save_legacy_database(self):
        """Save legacy certificate database"""
        self.legacy_database['last_updated'] = datetime.now().isoformat()
        with open(self.legacy_database_file, 'w') as f:
            json.dump(self.legacy_database, f, indent=2)
    
    def load_verification_rules(self):
        """Load verification rules for different certificate types"""
        if os.path.exists(self.verification_rules_file):
            with open(self.verification_rules_file, 'r') as f:
                self.verification_rules = json.load(f)
        else:
            self.verification_rules = {
                'legacy_physical': {
                    'primary_methods': ['ocr_forensics', 'database_lookup'],
                    'secondary_methods': ['human_review'],
                    'confidence_threshold': 70,
                    'requires_manual_review': True,
                    'processing_time_estimate': '5-10 minutes'
                },
                'legacy_digital': {
                    'primary_methods': ['database_lookup', 'digital_signature'],
                    'secondary_methods': ['ocr_forensics'],
                    'confidence_threshold': 80,
                    'requires_manual_review': False,
                    'processing_time_estimate': '1-2 minutes'
                },
                'new_blockchain': {
                    'primary_methods': ['blockchain_verification', 'digital_signature'],
                    'secondary_methods': ['database_lookup'],
                    'confidence_threshold': 95,
                    'requires_manual_review': False,
                    'processing_time_estimate': '30 seconds'
                },
                'hybrid': {
                    'primary_methods': ['blockchain_verification', 'database_lookup', 'digital_signature'],
                    'secondary_methods': ['ocr_forensics', 'human_review'],
                    'confidence_threshold': 85,
                    'requires_manual_review': False,
                    'processing_time_estimate': '1-3 minutes'
                }
            }
            self.save_verification_rules()
    
    def save_verification_rules(self):
        """Save verification rules"""
        with open(self.verification_rules_file, 'w') as f:
            json.dump(self.verification_rules, f, indent=2)
    
    def load_processing_stats(self):
        """Load processing statistics"""
        if os.path.exists(self.processing_stats_file):
            with open(self.processing_stats_file, 'r') as f:
                self.processing_stats = json.load(f)
        else:
            self.processing_stats = {
                'total_processed': 0,
                'by_type': {
                    'legacy_physical': 0,
                    'legacy_digital': 0,
                    'new_blockchain': 0,
                    'hybrid': 0
                },
                'by_result': {
                    'verified': 0,
                    'rejected': 0,
                    'pending_review': 0
                },
                'average_processing_time': {},
                'last_updated': datetime.now().isoformat()
            }
            self.save_processing_stats()
    
    def save_processing_stats(self):
        """Save processing statistics"""
        self.processing_stats['last_updated'] = datetime.now().isoformat()
        with open(self.processing_stats_file, 'w') as f:
            json.dump(self.processing_stats, f, indent=2)
    
    def classify_certificate_type(self, certificate_data: Dict[str, Any], image_data: Optional[bytes] = None) -> CertificateType:
        """Classify certificate type based on available data"""
        
        # Check for blockchain indicators
        has_blockchain_hash = certificate_data.get('blockchain_hash') is not None
        has_verification_code = certificate_data.get('verification_code') is not None
        has_digital_signature = certificate_data.get('digital_signature') is not None
        
        # Check for legacy indicators
        has_physical_scan = image_data is not None
        has_legacy_format = self.detect_legacy_format(certificate_data)
        
        # Classification logic
        if has_blockchain_hash and has_digital_signature:
            if has_physical_scan or has_legacy_format:
                return CertificateType.HYBRID
            else:
                return CertificateType.NEW_BLOCKCHAIN
        elif has_physical_scan:
            return CertificateType.LEGACY_PHYSICAL
        elif has_legacy_format:
            return CertificateType.LEGACY_DIGITAL
        else:
            # Default to new blockchain if modern format
            return CertificateType.NEW_BLOCKCHAIN
    
    def detect_legacy_format(self, certificate_data: Dict[str, Any]) -> bool:
        """Detect if certificate follows legacy format patterns"""
        legacy_indicators = [
            'registration_number' in certificate_data,
            'seal_number' in certificate_data,
            'manual_signature' in certificate_data,
            certificate_data.get('issue_year', 0) < 2020,
            'physical_certificate' in certificate_data,
            'scanned_document' in certificate_data
        ]
        
        return sum(legacy_indicators) >= 2
    
    def process_certificate(self, certificate_data: Dict[str, Any], image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Process certificate using appropriate dual strategy"""
        processing_start = datetime.now()
        processing_id = hashlib.sha256(f"{certificate_data}{processing_start}".encode()).hexdigest()[:12]
        
        # Classify certificate type
        cert_type = self.classify_certificate_type(certificate_data, image_data)
        
        # Get verification rules for this type
        rules = self.verification_rules.get(cert_type.value, self.verification_rules['hybrid'])
        
        # Initialize processing result
        processing_result = {
            'processing_id': processing_id,
            'certificate_type': cert_type.value,
            'processing_start': processing_start.isoformat(),
            'verification_methods_used': [],
            'results': {},
            'overall_confidence': 0,
            'verification_status': 'PROCESSING',
            'requires_manual_review': rules['requires_manual_review']
        }
        
        # Execute primary verification methods
        for method in rules['primary_methods']:
            method_result = self.execute_verification_method(method, certificate_data, image_data)
            processing_result['verification_methods_used'].append(method)
            processing_result['results'][method] = method_result
        
        # Calculate overall confidence
        overall_confidence = self.calculate_overall_confidence(processing_result['results'], cert_type)
        processing_result['overall_confidence'] = overall_confidence
        
        # Determine if secondary methods are needed
        if overall_confidence < rules['confidence_threshold']:
            for method in rules['secondary_methods']:
                if method not in processing_result['verification_methods_used']:
                    method_result = self.execute_verification_method(method, certificate_data, image_data)
                    processing_result['verification_methods_used'].append(method)
                    processing_result['results'][method] = method_result
            
            # Recalculate confidence
            overall_confidence = self.calculate_overall_confidence(processing_result['results'], cert_type)
            processing_result['overall_confidence'] = overall_confidence
        
        # Determine final verification status
        processing_result['verification_status'] = self.determine_verification_status(
            overall_confidence, rules, processing_result['results']
        )
        
        # Add processing metadata
        processing_end = datetime.now()
        processing_result['processing_end'] = processing_end.isoformat()
        processing_result['processing_time_seconds'] = (processing_end - processing_start).total_seconds()
        processing_result['estimated_time'] = rules['processing_time_estimate']
        
        # Generate recommendation
        processing_result['recommendation'] = self.generate_recommendation(processing_result)
        
        # Update statistics
        self.update_processing_statistics(cert_type, processing_result)
        
        return processing_result
    
    def execute_verification_method(self, method: str, certificate_data: Dict[str, Any], image_data: Optional[bytes]) -> Dict[str, Any]:
        """Execute specific verification method"""
        
        if method == 'ocr_forensics':
            return self.execute_ocr_forensics(certificate_data, image_data)
        elif method == 'database_lookup':
            return self.execute_database_lookup(certificate_data)
        elif method == 'blockchain_verification':
            return self.execute_blockchain_verification(certificate_data)
        elif method == 'digital_signature':
            return self.execute_digital_signature_verification(certificate_data)
        elif method == 'human_review':
            return self.execute_human_review_preparation(certificate_data, image_data)
        else:
            return {
                'method': method,
                'success': False,
                'error': f'Unknown verification method: {method}',
                'confidence': 0
            }
    
    def execute_ocr_forensics(self, certificate_data: Dict[str, Any], image_data: Optional[bytes]) -> Dict[str, Any]:
        """Execute OCR and forensics analysis"""
        if not image_data:
            return {
                'method': 'ocr_forensics',
                'success': False,
                'error': 'No image data provided for OCR analysis',
                'confidence': 0
            }
        
        try:
            # Simulate OCR forensics analysis (integrate with actual OCR engine)
            from ocr_forensics import ocr_forensics_engine
            analysis_result = ocr_forensics_engine.comprehensive_analysis(image_data)
            
            return {
                'method': 'ocr_forensics',
                'success': True,
                'analysis_result': analysis_result,
                'confidence': analysis_result.get('overall_confidence', 0),
                'authenticity_level': analysis_result.get('forensics_analysis', {}).get('authenticity_level', 'UNKNOWN')
            }
        except Exception as e:
            return {
                'method': 'ocr_forensics',
                'success': False,
                'error': f'OCR forensics failed: {str(e)}',
                'confidence': 0
            }
    
    def execute_database_lookup(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database lookup verification"""
        try:
            # Check in legacy database
            verification_code = certificate_data.get('verification_code')
            certificate_id = certificate_data.get('certificate_id')
            student_name = certificate_data.get('student_name')
            
            # Search legacy database
            for cert in self.legacy_database['certificates']:
                if (cert.get('verification_code') == verification_code or 
                    cert.get('certificate_id') == certificate_id or
                    (cert.get('student_name') == student_name and 
                     cert.get('institution_id') == certificate_data.get('institution_id'))):
                    
                    return {
                        'method': 'database_lookup',
                        'success': True,
                        'found_in_database': True,
                        'database_record': cert,
                        'confidence': 90,
                        'match_type': 'EXACT' if cert.get('verification_code') == verification_code else 'PARTIAL'
                    }
            
            # Check modern database (integrate with existing certificate database)
            from certificate_database import certificate_db
            db_result = certificate_db.verify_certificate(verification_code or certificate_id)
            
            if db_result.get('valid'):
                return {
                    'method': 'database_lookup',
                    'success': True,
                    'found_in_database': True,
                    'database_record': db_result.get('certificate'),
                    'confidence': 95,
                    'match_type': 'EXACT'
                }
            
            return {
                'method': 'database_lookup',
                'success': True,
                'found_in_database': False,
                'confidence': 10,
                'message': 'Certificate not found in any database'
            }
            
        except Exception as e:
            return {
                'method': 'database_lookup',
                'success': False,
                'error': f'Database lookup failed: {str(e)}',
                'confidence': 0
            }
    
    def execute_blockchain_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute blockchain verification"""
        try:
            blockchain_hash = certificate_data.get('blockchain_hash')
            if not blockchain_hash:
                return {
                    'method': 'blockchain_verification',
                    'success': False,
                    'error': 'No blockchain hash provided',
                    'confidence': 0
                }
            
            # Integrate with blockchain verification
            from enhanced_blockchain import academic_blockchain
            
            # Verify blockchain integrity
            chain_valid = academic_blockchain.is_chain_valid()
            
            if chain_valid:
                # Search for certificate in blockchain
                for block in academic_blockchain.chain:
                    for transaction in block.data.get('transactions', []):
                        if transaction.get('certificate_hash') == blockchain_hash:
                            return {
                                'method': 'blockchain_verification',
                                'success': True,
                                'blockchain_valid': True,
                                'transaction_found': True,
                                'block_index': block.index,
                                'block_hash': block.hash,
                                'confidence': 98,
                                'immutable_proof': True
                            }
                
                return {
                    'method': 'blockchain_verification',
                    'success': True,
                    'blockchain_valid': True,
                    'transaction_found': False,
                    'confidence': 20,
                    'message': 'Blockchain valid but certificate not found'
                }
            else:
                return {
                    'method': 'blockchain_verification',
                    'success': False,
                    'blockchain_valid': False,
                    'confidence': 0,
                    'error': 'Blockchain integrity compromised'
                }
                
        except Exception as e:
            return {
                'method': 'blockchain_verification',
                'success': False,
                'error': f'Blockchain verification failed: {str(e)}',
                'confidence': 0
            }
    
    def execute_digital_signature_verification(self, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute digital signature verification"""
        try:
            digital_signature = certificate_data.get('digital_signature')
            if not digital_signature:
                return {
                    'method': 'digital_signature',
                    'success': False,
                    'error': 'No digital signature provided',
                    'confidence': 0
                }
            
            # Integrate with PKI verification
            from pki_digital_signing import pki_signing_engine
            
            verification_result = pki_signing_engine.verify_digital_signature(
                certificate_data, digital_signature
            )
            
            if verification_result.get('valid'):
                return {
                    'method': 'digital_signature',
                    'success': True,
                    'signature_valid': True,
                    'verification_details': verification_result.get('verification_details'),
                    'confidence': 95,
                    'trust_level': verification_result.get('trust_level', 'MEDIUM')
                }
            else:
                return {
                    'method': 'digital_signature',
                    'success': False,
                    'signature_valid': False,
                    'error': verification_result.get('error'),
                    'confidence': 0
                }
                
        except Exception as e:
            return {
                'method': 'digital_signature',
                'success': False,
                'error': f'Digital signature verification failed: {str(e)}',
                'confidence': 0
            }
    
    def execute_human_review_preparation(self, certificate_data: Dict[str, Any], image_data: Optional[bytes]) -> Dict[str, Any]:
        """Prepare certificate for human review"""
        review_package = {
            'method': 'human_review',
            'success': True,
            'review_id': hashlib.sha256(f"{certificate_data}{datetime.now()}".encode()).hexdigest()[:8],
            'certificate_data': certificate_data,
            'has_image': image_data is not None,
            'review_priority': self.calculate_review_priority(certificate_data),
            'review_checklist': self.generate_review_checklist(certificate_data),
            'estimated_review_time': '10-15 minutes',
            'confidence': 50,  # Neutral until human review
            'status': 'PENDING_HUMAN_REVIEW'
        }
        
        return review_package
    
    def calculate_review_priority(self, certificate_data: Dict[str, Any]) -> str:
        """Calculate priority for human review"""
        high_priority_indicators = [
            certificate_data.get('degree_type', '').upper() in ['PHD', 'DOCTORATE', 'MD'],
            certificate_data.get('institution_type') == 'GOVERNMENT',
            'urgent' in certificate_data.get('notes', '').lower(),
            certificate_data.get('verification_purpose') == 'EMPLOYMENT'
        ]
        
        if sum(high_priority_indicators) >= 2:
            return 'HIGH'
        elif sum(high_priority_indicators) >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_review_checklist(self, certificate_data: Dict[str, Any]) -> List[str]:
        """Generate checklist for human reviewers"""
        checklist = [
            "Verify student name matches official records",
            "Check institution name and accreditation status",
            "Validate degree type and field of study",
            "Confirm graduation date is reasonable",
            "Check for any signs of tampering or forgery",
            "Verify institutional seal and signatures",
            "Cross-reference with institution's official records"
        ]
        
        # Add specific checks based on certificate type
        if certificate_data.get('degree_type', '').upper() in ['PHD', 'DOCTORATE']:
            checklist.append("Verify thesis title and supervisor information")
            checklist.append("Check research publication requirements")
        
        if certificate_data.get('honors'):
            checklist.append("Verify honors and distinctions claimed")
        
        return checklist
    
    def calculate_overall_confidence(self, results: Dict[str, Any], cert_type: CertificateType) -> float:
        """Calculate overall confidence from all verification methods"""
        if not results:
            return 0.0
        
        # Weight different methods based on certificate type
        weights = {
            CertificateType.LEGACY_PHYSICAL: {
                'ocr_forensics': 0.4,
                'database_lookup': 0.3,
                'human_review': 0.3
            },
            CertificateType.LEGACY_DIGITAL: {
                'database_lookup': 0.4,
                'digital_signature': 0.4,
                'ocr_forensics': 0.2
            },
            CertificateType.NEW_BLOCKCHAIN: {
                'blockchain_verification': 0.5,
                'digital_signature': 0.4,
                'database_lookup': 0.1
            },
            CertificateType.HYBRID: {
                'blockchain_verification': 0.3,
                'digital_signature': 0.3,
                'database_lookup': 0.2,
                'ocr_forensics': 0.2
            }
        }
        
        method_weights = weights.get(cert_type, weights[CertificateType.HYBRID])
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for method, result in results.items():
            if method in method_weights and result.get('success'):
                confidence = result.get('confidence', 0)
                weight = method_weights[method]
                weighted_confidence += confidence * weight
                total_weight += weight
        
        if total_weight > 0:
            return round(weighted_confidence / total_weight, 2)
        else:
            return 0.0
    
    def determine_verification_status(self, confidence: float, rules: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Determine final verification status"""
        threshold = rules['confidence_threshold']
        requires_review = rules['requires_manual_review']
        
        # Check for critical failures
        blockchain_result = results.get('blockchain_verification')
        if blockchain_result and not blockchain_result.get('success') and blockchain_result.get('blockchain_valid') is False:
            return 'REJECTED'
        
        signature_result = results.get('digital_signature')
        if signature_result and not signature_result.get('success') and signature_result.get('signature_valid') is False:
            return 'REJECTED'
        
        # Determine status based on confidence
        if confidence >= threshold:
            if requires_review:
                return 'VERIFIED_PENDING_REVIEW'
            else:
                return 'VERIFIED'
        elif confidence >= threshold * 0.7:
            return 'PENDING_REVIEW'
        else:
            return 'REJECTED'
    
    def generate_recommendation(self, processing_result: Dict[str, Any]) -> str:
        """Generate human-readable recommendation"""
        status = processing_result['verification_status']
        confidence = processing_result['overall_confidence']
        cert_type = processing_result['certificate_type']
        
        if status == 'VERIFIED':
            return f"ACCEPT: High confidence ({confidence}%) verification for {cert_type} certificate"
        elif status == 'VERIFIED_PENDING_REVIEW':
            return f"CONDITIONAL ACCEPT: Verification successful ({confidence}%) but requires human review per policy"
        elif status == 'PENDING_REVIEW':
            return f"MANUAL REVIEW: Moderate confidence ({confidence}%), human verification recommended"
        elif status == 'REJECTED':
            return f"REJECT: Low confidence ({confidence}%) or critical verification failures detected"
        else:
            return f"UNKNOWN: Unable to determine verification status"
    
    def update_processing_statistics(self, cert_type: CertificateType, processing_result: Dict[str, Any]):
        """Update processing statistics"""
        self.processing_stats['total_processed'] += 1
        self.processing_stats['by_type'][cert_type.value] += 1
        
        status = processing_result['verification_status']
        if status in ['VERIFIED', 'VERIFIED_PENDING_REVIEW']:
            self.processing_stats['by_result']['verified'] += 1
        elif status == 'REJECTED':
            self.processing_stats['by_result']['rejected'] += 1
        else:
            self.processing_stats['by_result']['pending_review'] += 1
        
        # Update average processing time
        processing_time = processing_result.get('processing_time_seconds', 0)
        if cert_type.value not in self.processing_stats['average_processing_time']:
            self.processing_stats['average_processing_time'][cert_type.value] = []
        
        self.processing_stats['average_processing_time'][cert_type.value].append(processing_time)
        
        # Keep only last 100 entries for average calculation
        if len(self.processing_stats['average_processing_time'][cert_type.value]) > 100:
            self.processing_stats['average_processing_time'][cert_type.value] = \
                self.processing_stats['average_processing_time'][cert_type.value][-100:]
        
        self.save_processing_stats()
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = self.processing_stats.copy()
        
        # Calculate average processing times
        avg_times = {}
        for cert_type, times in stats['average_processing_time'].items():
            if times:
                avg_times[cert_type] = {
                    'average_seconds': round(sum(times) / len(times), 2),
                    'sample_size': len(times)
                }
            else:
                avg_times[cert_type] = {'average_seconds': 0, 'sample_size': 0}
        
        stats['average_processing_time'] = avg_times
        
        # Calculate success rates
        total = stats['total_processed']
        if total > 0:
            stats['success_rate'] = {
                'verified_percentage': round((stats['by_result']['verified'] / total) * 100, 2),
                'rejected_percentage': round((stats['by_result']['rejected'] / total) * 100, 2),
                'pending_review_percentage': round((stats['by_result']['pending_review'] / total) * 100, 2)
            }
        else:
            stats['success_rate'] = {'verified_percentage': 0, 'rejected_percentage': 0, 'pending_review_percentage': 0}
        
        return stats

# Global dual strategy processor instance
dual_strategy_processor = DualStrategyProcessor()
