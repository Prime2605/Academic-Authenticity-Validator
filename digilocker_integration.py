"""
DigiLocker/NAD Integration System for Academic Authenticity Validator
Integrates with DigiLocker API and National Academic Depository (NAD) for credential verification
"""

import requests
import json
import hashlib
import base64
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import uuid
from urllib.parse import urlencode, parse_qs
import hmac
import time

class DigiLockerIntegration:
    """DigiLocker and NAD integration for academic credential verification"""
    
    def __init__(self):
        self.config_file = "digilocker_config.json"
        self.user_sessions_file = "digilocker_sessions.json"
        self.nad_cache_file = "nad_cache.json"
        
        self.load_configuration()
        self.load_user_sessions()
        self.load_nad_cache()
        
        # DigiLocker API endpoints
        self.digilocker_base_url = "https://api.digitallocker.gov.in"
        self.nad_base_url = "https://nad.gov.in/api"
        
        # OAuth 2.0 configuration
        self.oauth_config = {
            'authorization_url': f"{self.digilocker_base_url}/public/oauth2/1/authorize",
            'token_url': f"{self.digilocker_base_url}/public/oauth2/1/token",
            'user_info_url': f"{self.digilocker_base_url}/public/oauth2/1/user",
            'documents_url': f"{self.digilocker_base_url}/public/oauth2/1/file/issued"
        }
    
    def load_configuration(self):
        """Load DigiLocker configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration for DigiLocker integration
            self.config = {
                'client_id': 'your_digilocker_client_id',
                'client_secret': 'your_digilocker_client_secret',
                'redirect_uri': 'http://localhost:5000/digilocker/callback',
                'scope': 'openid profile email phone documents',
                'nad_api_key': 'your_nad_api_key',
                'nad_client_id': 'your_nad_client_id',
                'session_timeout_hours': 24,
                'cache_timeout_hours': 6,
                'supported_document_types': [
                    'CERTIFICATE',
                    'MARKSHEET',
                    'DIPLOMA',
                    'DEGREE',
                    'TRANSCRIPT'
                ]
            }
            self.save_configuration()
    
    def save_configuration(self):
        """Save DigiLocker configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_user_sessions(self):
        """Load user session data"""
        if os.path.exists(self.user_sessions_file):
            try:
                with open(self.user_sessions_file, 'r') as f:
                    self.user_sessions = json.load(f)
            except (json.JSONDecodeError, ValueError):
                self.user_sessions = {}
        else:
            self.user_sessions = {}
    
    def save_user_sessions(self):
        """Save user session data"""
        with open(self.user_sessions_file, 'w') as f:
            json.dump(self.user_sessions, f, indent=2)
    
    def load_nad_cache(self):
        """Load NAD cache data"""
        if os.path.exists(self.nad_cache_file):
            try:
                with open(self.nad_cache_file, 'r') as f:
                    self.nad_cache = json.load(f)
            except (json.JSONDecodeError, ValueError):
                self.nad_cache = {}
        else:
            self.nad_cache = {}
    
    def save_nad_cache(self):
        """Save NAD cache data"""
        with open(self.nad_cache_file, 'w') as f:
            json.dump(self.nad_cache, f, indent=2)
    
    def generate_authorization_url(self, state: str = None) -> str:
        """Generate DigiLocker OAuth authorization URL"""
        if not state:
            state = str(uuid.uuid4())
        
        params = {
            'response_type': 'code',
            'client_id': self.config['client_id'],
            'redirect_uri': self.config['redirect_uri'],
            'scope': self.config['scope'],
            'state': state
        }
        
        return f"{self.oauth_config['authorization_url']}?{urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'code': authorization_code,
                'redirect_uri': self.config['redirect_uri']
            }
            
            response = requests.post(
                self.oauth_config['token_url'],
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Store token with expiration
                token_info['expires_at'] = datetime.now() + timedelta(seconds=token_info.get('expires_in', 3600))
                token_info['state'] = state
                
                return {
                    'success': True,
                    'token_info': token_info
                }
            else:
                return {
                    'success': False,
                    'error': f'Token exchange failed: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Token exchange error: {str(e)}'
            }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from DigiLocker"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                self.oauth_config['user_info_url'],
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_info = response.json()
                
                # Create user session
                session_id = str(uuid.uuid4())
                session_data = {
                    'session_id': session_id,
                    'user_info': user_info,
                    'access_token': access_token,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(hours=self.config['session_timeout_hours'])).isoformat(),
                    'last_activity': datetime.now().isoformat()
                }
                
                # Store session
                user_key = user_info.get('email') or user_info.get('mobile') or user_info.get('sub')
                self.user_sessions[user_key] = session_data
                self.save_user_sessions()
                
                return {
                    'success': True,
                    'user_info': user_info,
                    'session_id': session_id
                }
            else:
                return {
                    'success': False,
                    'error': f'User info retrieval failed: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'User info error: {str(e)}'
            }
    
    def get_user_documents(self, access_token: str, document_type: str = None) -> Dict[str, Any]:
        """Get user's documents from DigiLocker"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {}
            if document_type and document_type in self.config['supported_document_types']:
                params['doctype'] = document_type
            
            response = requests.get(
                self.oauth_config['documents_url'],
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                documents = response.json()
                
                # Filter academic documents
                academic_documents = []
                for doc in documents.get('items', []):
                    if self.is_academic_document(doc):
                        academic_documents.append(self.process_academic_document(doc))
                
                return {
                    'success': True,
                    'documents': academic_documents,
                    'total_count': len(academic_documents)
                }
            else:
                return {
                    'success': False,
                    'error': f'Document retrieval failed: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Document retrieval error: {str(e)}'
            }
    
    def is_academic_document(self, document: Dict[str, Any]) -> bool:
        """Check if document is academic-related"""
        doc_type = document.get('doctype', '').upper()
        doc_name = document.get('name', '').upper()
        issuer = document.get('issuer', '').upper()
        
        academic_keywords = [
            'CERTIFICATE', 'MARKSHEET', 'DIPLOMA', 'DEGREE', 'TRANSCRIPT',
            'UNIVERSITY', 'COLLEGE', 'INSTITUTE', 'EDUCATION', 'ACADEMIC',
            'GRADUATION', 'POST GRADUATION', 'BACHELOR', 'MASTER', 'PHD',
            'B.TECH', 'M.TECH', 'B.E.', 'M.E.', 'B.SC', 'M.SC', 'MBA', 'MCA'
        ]
        
        return any(keyword in doc_type or keyword in doc_name or keyword in issuer 
                  for keyword in academic_keywords)
    
    def process_academic_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process and standardize academic document information"""
        return {
            'document_id': document.get('uri') or document.get('id'),
            'document_type': document.get('doctype', 'UNKNOWN'),
            'name': document.get('name', 'Unknown Document'),
            'issuer': document.get('issuer', 'Unknown Issuer'),
            'issue_date': document.get('date') or document.get('issued_date'),
            'description': document.get('description', ''),
            'size': document.get('size', 0),
            'mime_type': document.get('mime', 'application/pdf'),
            'digilocker_uri': document.get('uri'),
            'verification_status': 'DIGILOCKER_VERIFIED',
            'source': 'DIGILOCKER',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def verify_with_nad(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verify document with National Academic Depository (NAD)"""
        try:
            # Create cache key
            cache_key = hashlib.sha256(
                f"{document_info.get('document_id')}{document_info.get('issuer')}".encode()
            ).hexdigest()
            
            # Check cache first
            if cache_key in self.nad_cache:
                cached_data = self.nad_cache[cache_key]
                cache_time = datetime.fromisoformat(cached_data.get('cached_at', '2000-01-01'))
                
                if datetime.now() - cache_time < timedelta(hours=self.config['cache_timeout_hours']):
                    return {
                        'success': True,
                        'verification_result': cached_data['result'],
                        'source': 'NAD_CACHE'
                    }
            
            # NAD API call (simulated - replace with actual NAD API)
            nad_verification = self.simulate_nad_verification(document_info)
            
            # Cache the result
            self.nad_cache[cache_key] = {
                'result': nad_verification,
                'cached_at': datetime.now().isoformat()
            }
            self.save_nad_cache()
            
            return {
                'success': True,
                'verification_result': nad_verification,
                'source': 'NAD_API'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'NAD verification error: {str(e)}'
            }
    
    def simulate_nad_verification(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate NAD verification (replace with actual NAD API calls)"""
        # This simulates NAD verification - in production, use actual NAD API
        
        issuer = document_info.get('issuer', '').upper()
        doc_type = document_info.get('document_type', '').upper()
        
        # Simulate verification based on known patterns
        verification_score = 85  # Base score
        
        # Increase score for known institutions
        known_institutions = [
            'UNIVERSITY', 'IIT', 'NIT', 'IIIT', 'ANNA UNIVERSITY', 
            'DELHI UNIVERSITY', 'MUMBAI UNIVERSITY', 'CBSE', 'ICSE'
        ]
        
        if any(inst in issuer for inst in known_institutions):
            verification_score += 10
        
        # Increase score for standard document types
        if doc_type in ['CERTIFICATE', 'MARKSHEET', 'DEGREE', 'DIPLOMA']:
            verification_score += 5
        
        verification_score = min(verification_score, 100)
        
        return {
            'nad_verified': verification_score > 80,
            'verification_score': verification_score,
            'verification_details': {
                'institution_verified': verification_score > 85,
                'document_format_valid': True,
                'digital_signature_valid': verification_score > 90,
                'nad_database_match': verification_score > 95
            },
            'verification_timestamp': datetime.now().isoformat(),
            'nad_reference_id': f"NAD_{uuid.uuid4().hex[:12].upper()}",
            'status': 'VERIFIED' if verification_score > 80 else 'PENDING_VERIFICATION'
        }
    
    def authenticate_user(self, email_or_mobile: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email/mobile and password (simulated)"""
        try:
            # In production, this would integrate with actual DigiLocker authentication
            # For now, we'll simulate the authentication process
            
            # Validate input
            if not email_or_mobile or not password:
                return {
                    'success': False,
                    'error': 'Email/mobile and password are required'
                }
            
            # Simulate authentication
            if len(password) < 6:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Create simulated user session
            user_info = {
                'user_id': hashlib.sha256(email_or_mobile.encode()).hexdigest()[:12],
                'email': email_or_mobile if '@' in email_or_mobile else None,
                'mobile': email_or_mobile if '@' not in email_or_mobile else None,
                'name': f"User {email_or_mobile.split('@')[0] if '@' in email_or_mobile else email_or_mobile[-4:]}",
                'verified': True,
                'digilocker_id': f"DL_{uuid.uuid4().hex[:8].upper()}"
            }
            
            session_id = str(uuid.uuid4())
            session_data = {
                'session_id': session_id,
                'user_info': user_info,
                'authenticated_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=self.config['session_timeout_hours'])).isoformat(),
                'authentication_method': 'EMAIL_PASSWORD' if '@' in email_or_mobile else 'MOBILE_PASSWORD'
            }
            
            # Store session
            self.user_sessions[email_or_mobile] = session_data
            self.save_user_sessions()
            
            return {
                'success': True,
                'user_info': user_info,
                'session_id': session_id,
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}'
            }
    
    def get_user_session(self, session_id: str) -> Dict[str, Any]:
        """Get user session by session ID"""
        for user_key, session_data in self.user_sessions.items():
            if session_data.get('session_id') == session_id:
                # Check if session is expired
                expires_at = datetime.fromisoformat(session_data.get('expires_at', '2000-01-01'))
                
                if datetime.now() > expires_at:
                    # Session expired
                    del self.user_sessions[user_key]
                    self.save_user_sessions()
                    return {
                        'success': False,
                        'error': 'Session expired'
                    }
                
                # Update last activity
                session_data['last_activity'] = datetime.now().isoformat()
                self.save_user_sessions()
                
                return {
                    'success': True,
                    'session_data': session_data
                }
        
        return {
            'success': False,
            'error': 'Session not found'
        }
    
    def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        for user_key, session_data in self.user_sessions.items():
            if session_data.get('session_id') == session_id:
                del self.user_sessions[user_key]
                self.save_user_sessions()
                return {
                    'success': True,
                    'message': 'Logout successful'
                }
        
        return {
            'success': False,
            'error': 'Session not found'
        }
    
    def get_comprehensive_verification(self, document_info: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Get comprehensive verification combining DigiLocker and NAD data"""
        try:
            # Verify session
            session_result = self.get_user_session(session_id)
            if not session_result.get('success'):
                return session_result
            
            user_info = session_result['session_data']['user_info']
            
            # Get DigiLocker verification
            digilocker_verified = document_info.get('source') == 'DIGILOCKER'
            
            # Get NAD verification
            nad_result = self.verify_with_nad(document_info)
            nad_verified = nad_result.get('success') and nad_result.get('verification_result', {}).get('nad_verified', False)
            
            # Calculate overall confidence
            confidence_score = 0
            if digilocker_verified:
                confidence_score += 40
            if nad_verified:
                confidence_score += 50
            
            # Additional verification factors
            if document_info.get('verification_status') == 'DIGILOCKER_VERIFIED':
                confidence_score += 10
            
            verification_result = {
                'document_id': document_info.get('document_id'),
                'overall_confidence': min(confidence_score, 100),
                'verification_sources': {
                    'digilocker': {
                        'verified': digilocker_verified,
                        'status': document_info.get('verification_status', 'UNKNOWN')
                    },
                    'nad': nad_result.get('verification_result', {}) if nad_result.get('success') else {'verified': False}
                },
                'user_context': {
                    'user_id': user_info.get('user_id'),
                    'verified_user': user_info.get('verified', False)
                },
                'verification_timestamp': datetime.now().isoformat(),
                'recommendation': self.generate_verification_recommendation(confidence_score)
            }
            
            return {
                'success': True,
                'verification_result': verification_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Comprehensive verification error: {str(e)}'
            }
    
    def generate_verification_recommendation(self, confidence_score: int) -> str:
        """Generate verification recommendation based on confidence score"""
        if confidence_score >= 90:
            return "HIGHLY_TRUSTED: Document verified through multiple authoritative sources"
        elif confidence_score >= 70:
            return "TRUSTED: Document verified through DigiLocker/NAD with high confidence"
        elif confidence_score >= 50:
            return "MODERATELY_TRUSTED: Document partially verified, additional verification recommended"
        else:
            return "VERIFICATION_REQUIRED: Document requires manual verification"
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get DigiLocker integration statistics"""
        active_sessions = 0
        total_users = len(self.user_sessions)
        
        for session_data in self.user_sessions.values():
            expires_at = datetime.fromisoformat(session_data.get('expires_at', '2000-01-01'))
            if datetime.now() <= expires_at:
                active_sessions += 1
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'nad_cache_entries': len(self.nad_cache),
            'supported_document_types': self.config['supported_document_types'],
            'integration_status': 'OPERATIONAL',
            'last_updated': datetime.now().isoformat()
        }

# Global DigiLocker integration instance
digilocker_integration = DigiLockerIntegration()
