"""
Academic Authenticity Validator - Blockchain Extension
Extends the base blockchain to handle academic credentials and certificates
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Assuming base blockchain and block classes are in the same directory
# If not, adjust the import path
try:
    from blockchain import Blockchain
    from block import Block
except ImportError:
    # Create dummy classes if the base files were removed
    class Block:
        def __init__(self, data, previous_hash):
            self.data = data
            self.previous_hash = previous_hash
            self.timestamp = time.time()
            self.nonce = 0
            self.hash = self.calculate_hash()

        def calculate_hash(self):
            # A simple hash for the dummy class
            block_string = json.dumps(self.__dict__, sort_keys=True)
            return "dummy_hash_" + str(len(block_string))

        def mine_block(self, difficulty):
            pass

    class Blockchain:
        def __init__(self, difficulty=2):
            self.chain = [self.create_genesis_block()]
            self.difficulty = difficulty

        def create_genesis_block(self):
            return Block("Genesis Block", "0")

        def get_latest_block(self):
            return self.chain[-1]

        def is_chain_valid(self):
            return True  # Dummy validation

        def to_dict(self):
            return [b.__dict__ for b in self.chain]

from academic_models import (
    AcademicCredential, Institution, Student, ResearchPaper,
    AcademicTransaction, CredentialType, InstitutionType
)
from college_database import get_institution_by_id


class AcademicBlockchain(Blockchain):
    """Extended blockchain for academic credential validation"""
    
    def __init__(self, difficulty=2):
        super().__init__(difficulty)
        self.institutions: Dict[str, Institution] = {}
        self.students: Dict[str, Student] = {}
        self.credentials: Dict[str, AcademicCredential] = {}
        self.research_papers: Dict[str, ResearchPaper] = {}
        self.pending_academic_transactions: List[AcademicTransaction] = []
        
        # Initialize institutions from the college database
        self._initialize_institutions_from_db()
    
    def _initialize_institutions_from_db(self):
        """Load institutions from the college database"""
        all_institutions = Institution.get_all_institutions()
        for inst in all_institutions:
            self.institutions[inst.institution_id] = inst
    
    def register_institution(self, institution: Institution) -> bool:
        """Register a new academic institution"""
        if institution.institution_id in self.institutions:
            return False
        
        self.institutions[institution.institution_id] = institution
        
        # Create transaction for institution registration
        transaction = AcademicTransaction(
            transaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            transaction_type="INSTITUTION_REGISTRATION",
            institution_id=institution.institution_id,
            details=institution.to_dict()
        )
        
        self.pending_academic_transactions.append(transaction)
        return True
    
    def register_student(self, student: Student) -> bool:
        """Register a new student"""
        if student.student_id in self.students:
            return False
        
        self.students[student.student_id] = student
        return True
    
    def issue_credential(self, credential: AcademicCredential, issuer_institution_id: str) -> Dict[str, Any]:
        """Issue a new academic credential"""
        # Validate institution exists and is verified
        if issuer_institution_id not in self.institutions:
            return {"success": False, "error": "Institution not found"}
        
        institution = self.institutions[issuer_institution_id]
        if not institution.is_verified:
            return {"success": False, "error": "Institution not verified"}
        
        # Validate credential data
        credential_dict = credential.to_dict()
        errors = validate_credential_data(credential_dict)
        if errors:
            return {"success": False, "error": f"Validation errors: {', '.join(errors)}"}
        
        # Check if credential already exists
        if credential.id in self.credentials:
            return {"success": False, "error": "Credential already exists"}
        
        # Register student if not exists
        if credential.student.id not in self.students:
            self.register_student(credential.student)
        
        # Store credential
        self.credentials[credential.id] = credential
        
        # Create transaction for credential issuance
        transaction = AcademicTransaction(
            transaction_type="CREDENTIAL_ISSUANCE",
            data=credential_dict,
            institution_id=issuer_institution_id
        )
        
        self.pending_academic_transactions.append(transaction)
        
        return {
            "success": True,
            "credential_id": credential.id,
            "credential_hash": credential.calculate_hash(),
            "transaction_id": transaction.transaction_id
        }
    
    def verify_credential(self, credential_id: str) -> Dict[str, Any]:
        """Verify an academic credential"""
        if credential_id not in self.credentials:
            return {"valid": False, "error": "Credential not found"}
        
        credential = self.credentials[credential_id]
        
        # Check if credential exists in blockchain
        credential_found_in_chain = False
        for block in self.chain:
            if isinstance(block.data, list):
                for transaction in block.data:
                    if (isinstance(transaction, dict) and 
                        transaction.get('transaction_type') == 'CREDENTIAL_ISSUANCE' and
                        transaction.get('data', {}).get('id') == credential_id):
                        credential_found_in_chain = True
                        break
        
        if not credential_found_in_chain:
            return {"valid": False, "error": "Credential not found in blockchain"}
        
        # Verify institution
        institution = credential.institution
        if institution.id not in self.institutions:
            return {"valid": False, "error": "Issuing institution not found"}
        
        if not self.institutions[institution.id].is_verified:
            return {"valid": False, "error": "Issuing institution not verified"}
        
        return {
            "valid": True,
            "credential": credential.to_dict(),
            "verification_date": time.time(),
            "blockchain_verified": True
        }
    
    def submit_research_paper(self, paper: ResearchPaper, submitter_institution_id: str) -> Dict[str, Any]:
        """Submit a research paper for authenticity tracking"""
        if submitter_institution_id not in self.institutions:
            return {"success": False, "error": "Institution not found"}
        
        if paper.id in self.research_papers:
            return {"success": False, "error": "Research paper already exists"}
        
        # Store research paper
        self.research_papers[paper.id] = paper
        
        # Create transaction for research paper submission
        transaction = AcademicTransaction(
            transaction_type="RESEARCH_PAPER_SUBMISSION",
            data=paper.to_dict(),
            institution_id=submitter_institution_id
        )
        
        self.pending_academic_transactions.append(transaction)
        
        return {
            "success": True,
            "paper_id": paper.id,
            "paper_hash": paper.calculate_hash(),
            "transaction_id": transaction.transaction_id
        }
    
    def mine_academic_transactions(self, miner_institution_id: str) -> Dict[str, Any]:
        """Mine pending academic transactions"""
        if not self.pending_academic_transactions:
            return {"success": False, "error": "No pending academic transactions"}
        
        if miner_institution_id not in self.institutions:
            return {"success": False, "error": "Miner institution not found"}
        
        # Convert academic transactions to standard format
        transactions_data = []
        for academic_tx in self.pending_academic_transactions:
            transactions_data.append(academic_tx.to_dict())
        
        # Add mining reward for institution
        reward_transaction = {
            "transaction_type": "MINING_REWARD",
            "institution_id": miner_institution_id,
            "reward": "Academic Mining Reward",
            "timestamp": time.time()
        }
        transactions_data.append(reward_transaction)
        
        # Create new block with academic transactions
        block = Block(transactions_data, self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        
        print(f"Academic block successfully mined by {self.institutions[miner_institution_id].name}!")
        self.chain.append(block)
        
        # Clear pending transactions
        self.pending_academic_transactions = []
        
        return {
            "success": True,
            "block_hash": block.hash,
            "transactions_count": len(transactions_data),
            "miner_institution": self.institutions[miner_institution_id].name
        }
    
    def get_student_credentials(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all credentials for a specific student"""
        student_credentials = []
        for credential in self.credentials.values():
            if credential.student.id == student_id:
                student_credentials.append(credential.to_dict())
        
        return student_credentials
    
    def get_institution_credentials(self, institution_id: str) -> List[Dict[str, Any]]:
        """Get all credentials issued by a specific institution"""
        institution_credentials = []
        for credential in self.credentials.values():
            if credential.institution.id == institution_id:
                institution_credentials.append(credential.to_dict())
        
        return institution_credentials
    
    def get_academic_statistics(self) -> Dict[str, Any]:
        """Get comprehensive academic blockchain statistics"""
        total_credentials = len(self.credentials)
        total_institutions = len(self.institutions)
        total_students = len(self.students)
        total_research_papers = len(self.research_papers)
        
        # Count credentials by type
        credential_types = {}
        for credential in self.credentials.values():
            cred_type = credential.credential_type.value
            credential_types[cred_type] = credential_types.get(cred_type, 0) + 1
        
        # Count credentials by level
        credential_levels = {}
        for credential in self.credentials.values():
            level = credential.level.value
            credential_levels[level] = credential_levels.get(level, 0) + 1
        
        # Count verified institutions
        verified_institutions = sum(1 for inst in self.institutions.values() if inst.is_verified)
        
        return {
            "total_credentials": total_credentials,
            "total_institutions": total_institutions,
            "verified_institutions": verified_institutions,
            "total_students": total_students,
            "total_research_papers": total_research_papers,
            "pending_transactions": len(self.pending_academic_transactions),
            "credential_types": credential_types,
            "credential_levels": credential_levels,
            "blockchain_length": len(self.chain),
            "is_valid": self.is_chain_valid()
        }
    
    def search_credentials(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search credentials based on various criteria"""
        results = []
        
        for credential in self.credentials.values():
            match = True
            
            # Check each query parameter
            if 'student_name' in query:
                student_name = credential.student.get_full_name().lower()
                if query['student_name'].lower() not in student_name:
                    match = False
            
            if 'institution_name' in query:
                inst_name = credential.institution.name.lower()
                if query['institution_name'].lower() not in inst_name:
                    match = False
            
            if 'credential_type' in query:
                if credential.credential_type.value != query['credential_type']:
                    match = False
            
            if 'level' in query:
                if credential.level.value != query['level']:
                    match = False
            
            if 'field_of_study' in query:
                field = credential.field_of_study.lower()
                if query['field_of_study'].lower() not in field:
                    match = False
            
            if match:
                results.append(credential.to_dict())
        
        return results
    
    def export_academic_data(self) -> Dict[str, Any]:
        """Export all academic data for backup/analysis"""
        return {
            "institutions": {id: inst.to_dict() for id, inst in self.institutions.items()},
            "students": {id: student.to_dict() for id, student in self.students.items()},
            "credentials": {id: cred.to_dict() for id, cred in self.credentials.items()},
            "research_papers": {id: paper.to_dict() for id, paper in self.research_papers.items()},
            "blockchain": self.to_dict(),
            "export_timestamp": time.time()
        }
