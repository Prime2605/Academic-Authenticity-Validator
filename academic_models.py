"""
Academic Authenticity Validator - Data Models
Handles academic credentials, certificates, and institutional data
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from college_database import CHENNAI_COLLEGES_DATABASE, get_institution_by_id, search_institutions

class CredentialType(Enum):
    DEGREE = "degree"
    CERTIFICATE = "certificate"
    DIPLOMA = "diploma"
    TRANSCRIPT = "transcript"
    RESEARCH_PAPER = "research_paper"
    OTHER = "other"

class InstitutionType(Enum):
    ENGINEERING = "engineering"
    MEDICAL = "medical"
    ARTS_SCIENCE = "arts_science"
    MANAGEMENT = "management"
    POLYTECHNIC = "polytechnic"
    RESEARCH = "research"
    OTHER = "other"

@dataclass
class Institution:
    institution_id: str
    name: str
    location: str
    affiliation: Optional[str] = None
    type: Optional[InstitutionType] = None
    verified: bool = False
    established: Optional[int] = None
    courses: List[str] = None
    category: Optional[str] = None

    def __post_init__(self):
        if self.courses is None:
            self.courses = []
        if self.affiliation is None:
            self.affiliation = "Independent"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.type:
            result['type'] = self.type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Institution':
        # Convert string type back to enum
        if 'type' in data and data['type']:
            try:
                data['type'] = InstitutionType(data['type'])
            except ValueError:
                data['type'] = InstitutionType.OTHER
        return cls(**data)

    @staticmethod
    def get_all_institutions() -> List['Institution']:
        """Get all institutions from the database"""
        institutions = []
        for college_data in CHENNAI_COLLEGES_DATABASE:
            institution = Institution(
                institution_id=college_data['institution_id'],
                name=college_data['name'],
                location=college_data['location'],
                affiliation=college_data.get('affiliation'),
                verified=college_data.get('verified', False),
                established=college_data.get('established'),
                courses=college_data.get('courses', []),
                category=college_data.get('category')
            )
            institutions.append(institution)
        return institutions

    @staticmethod
    def search_by_name(query: str) -> List['Institution']:
        """Search institutions by name"""
        return [Institution.from_dict(inst) for inst in search_institutions(query=query)]

    @staticmethod
    def get_by_category(category: str) -> List['Institution']:
        """Get institutions by category"""
        return [Institution.from_dict(inst) for inst in search_institutions(category=category)]

@dataclass
class Student:
    student_id: str
    name: str
    email: str
    institution_id: Optional[str] = None
    enrolled_date: Optional[datetime] = None

    def __post_init__(self):
        if self.enrolled_date is None:
            self.enrolled_date = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.enrolled_date:
            result['enrolled_date'] = self.enrolled_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        if 'enrolled_date' in data and data['enrolled_date']:
            data['enrolled_date'] = datetime.fromisoformat(data['enrolled_date'])
        return cls(**data)

@dataclass
class AcademicCredential:
    credential_id: str
    title: str
    student_id: str
    institution_id: str
    credential_type: CredentialType
    issue_date: datetime
    grade: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = None
    expiry_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['credential_type'] = self.credential_type.value
        result['issue_date'] = self.issue_date.isoformat()
        if self.expiry_date:
            result['expiry_date'] = self.expiry_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AcademicCredential':
        data['credential_type'] = CredentialType(data['credential_type'])
        data['issue_date'] = datetime.fromisoformat(data['issue_date'])
        if 'expiry_date' in data and data['expiry_date']:
            data['expiry_date'] = datetime.fromisoformat(data['expiry_date'])
        return cls(**data)

@dataclass
class ResearchPaper:
    paper_id: str
    title: str
    authors: List[str]
    institution_id: str
    publication_date: datetime
    abstract: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['publication_date'] = self.publication_date.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchPaper':
        data['publication_date'] = datetime.fromisoformat(data['publication_date'])
        return cls(**data)

@dataclass
class AcademicTransaction:
    transaction_id: str
    timestamp: datetime
    credential_id: Optional[str] = None
    student_id: Optional[str] = None
    institution_id: Optional[str] = None
    transaction_type: str = "credential_issue"
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AcademicTransaction':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

def generate_credential_id(prefix: str = "CRED") -> str:
    """Generate a unique credential ID with timestamp and random suffix"""
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{random_suffix}"

def generate_qr_code_data(credential_data: dict) -> str:
    """Generate QR code data for a credential"""
    import json
    from urllib.parse import quote
    base_url = "https://academic-validator.example.com/verify/"
    credential_id = credential_data.get('credential_id', '')
    verification_code = credential_data.get('verification_code', str(uuid.uuid4()))
    
    # Store the verification code with the credential data if needed
    if 'verification_code' not in credential_data:
        credential_data['verification_code'] = verification_code
    
    # Create a verification URL
    verification_url = f"{base_url}{credential_id}?code={verification_code}"
    
    # Return the URL-encoded JSON data for QR code
    return quote(json.dumps({
        'credential_id': credential_id,
        'verification_url': verification_url,
        'timestamp': datetime.now().isoformat()
    }))

# Utility functions for college database integration
def get_institution_details(institution_id: str) -> Optional[Institution]:
    """Get detailed institution information by ID"""
    institution_data = get_institution_by_id(institution_id)
    if institution_data:
        return Institution.from_dict(institution_data)
    return None

def validate_institution_exists(institution_id: str) -> bool:
    """Check if institution exists in the database"""
    return get_institution_by_id(institution_id) is not None

def get_courses_for_institution(institution_id: str) -> List[str]:
    """Get all courses offered by an institution"""
    institution = get_institution_details(institution_id)
    return institution.courses if institution else []

def search_colleges(query: str = None, category: str = None, type_filter: str = None) -> List[Institution]:
    """Search colleges with various filters"""
    results = search_institutions(query=query, category=category, type_filter=type_filter)
    return [Institution.from_dict(inst) for inst in results]

def get_institution_statistics() -> Dict[str, Any]:
    """Get statistics about institutions in the database"""
    total_institutions = len(CHENNAI_COLLEGES_DATABASE)
    verified_institutions = len([inst for inst in CHENNAI_COLLEGES_DATABASE if inst['verified']])
    categories = {}
    types = {}

    for inst in CHENNAI_COLLEGES_DATABASE:
        category = inst.get('category', 'Other')
        inst_type = inst.get('type', 'Other')

        categories[category] = categories.get(category, 0) + 1
        types[inst_type] = types.get(inst_type, 0) + 1

    return {
        'total_institutions': total_institutions,
        'verified_institutions': verified_institutions,
        'unverified_institutions': total_institutions - verified_institutions,
        'categories': categories,
        'types': types
    }
