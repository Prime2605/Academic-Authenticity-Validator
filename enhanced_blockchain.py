"""
Enhanced Blockchain for Academic Authenticity Validator
Real blockchain implementation with mining, validation, and visualization
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, index: int, data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine the block with proof-of-work"""
        target = "0" * difficulty
        start_time = time.time()
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
            # Show mining progress every 10000 attempts
            if self.nonce % 10000 == 0:
                print(f"Mining block {self.index}... Nonce: {self.nonce}")
        
        mining_time = time.time() - start_time
        print(f"Block {self.index} mined! Hash: {self.hash[:16]}... Time: {mining_time:.2f}s")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash,
            'human_time': datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        }

class AcademicBlockchain:
    """Blockchain for academic credentials with enhanced features"""
    
    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []
        self.mining_reward = 100
        self.institutions: Dict[str, Any] = {}
        self.students: Dict[str, Any] = {}
        self.credentials: Dict[str, Any] = {}
        
        # Create genesis block
        self.create_genesis_block()
        
        print(f"Academic Blockchain initialized with difficulty {difficulty}")
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_data = {
            'type': 'GENESIS',
            'message': 'Academic Authenticity Validator Genesis Block',
            'timestamp': datetime.now().isoformat(),
            'creator': 'Smart India Hackathon 2024'
        }
        
        genesis_block = Block(0, genesis_data, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        
        print("Genesis block created and mined!")
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict[str, Any]) -> str:
        """Add a transaction to pending transactions"""
        transaction_id = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        transaction['transaction_id'] = transaction_id
        transaction['timestamp'] = datetime.now().isoformat()
        
        self.pending_transactions.append(transaction)
        
        print(f"Transaction added: {transaction_id}")
        return transaction_id
    
    def mine_pending_transactions(self, mining_reward_address: str) -> Block:
        """Mine all pending transactions into a new block"""
        if not self.pending_transactions:
            print("No pending transactions to mine")
            return None
        
        # Add mining reward transaction
        reward_transaction = {
            'type': 'MINING_REWARD',
            'to': mining_reward_address,
            'amount': self.mining_reward,
            'timestamp': datetime.now().isoformat()
        }
        
        # Combine all transactions
        block_data = {
            'transactions': self.pending_transactions.copy(),
            'mining_reward': reward_transaction,
            'total_transactions': len(self.pending_transactions),
            'miner': mining_reward_address
        }
        
        # Create and mine new block
        new_block = Block(
            len(self.chain),
            block_data,
            self.get_latest_block().hash
        )
        
        print(f"Mining block {new_block.index} with {len(self.pending_transactions)} transactions...")
        new_block.mine_block(self.difficulty)
        
        # Add to chain and clear pending transactions
        self.chain.append(new_block)
        self.pending_transactions = []
        
        print(f"Block {new_block.index} added to blockchain!")
        return new_block
    
    def register_institution(self, institution_data: Dict[str, Any]) -> str:
        """Register an educational institution on the blockchain"""
        transaction = {
            'type': 'INSTITUTION_REGISTRATION',
            'institution_id': institution_data.get('institution_id'),
            'name': institution_data.get('name'),
            'location': institution_data.get('location'),
            'verification_status': 'verified',
            'registration_date': datetime.now().isoformat()
        }
        
        # Store in institutions registry
        self.institutions[institution_data['institution_id']] = institution_data
        
        # Add to blockchain
        return self.add_transaction(transaction)
    
    def register_student(self, student_data: Dict[str, Any]) -> str:
        """Register a student on the blockchain"""
        transaction = {
            'type': 'STUDENT_REGISTRATION',
            'student_id': student_data.get('student_id'),
            'name': student_data.get('name'),
            'institution_id': student_data.get('institution_id'),
            'registration_date': datetime.now().isoformat()
        }
        
        # Store in students registry
        self.students[student_data['student_id']] = student_data
        
        # Add to blockchain
        return self.add_transaction(transaction)
    
    def issue_credential(self, credential_data: Dict[str, Any], issuer_id: str) -> Dict[str, Any]:
        """Issue an academic credential on the blockchain"""
        try:
            credential_id = credential_data.get('credential_id')
            
            transaction = {
                'type': 'CREDENTIAL_ISSUANCE',
                'credential_id': credential_id,
                'student_id': credential_data.get('student_id'),
                'institution_id': issuer_id,
                'degree_type': credential_data.get('title'),
                'issue_date': datetime.now().isoformat(),
                'issuer_signature': f"{issuer_id}_VERIFIED_{int(time.time())}"
            }
            
            # Store credential
            self.credentials[credential_id] = credential_data
            
            # Add to blockchain
            transaction_id = self.add_transaction(transaction)
            
            # Mine the transaction immediately for demo purposes
            mined_block = self.mine_pending_transactions('SYSTEM')
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'transaction_hash': mined_block.hash if mined_block else None,
                'block_index': len(self.chain) - 1,
                'message': 'Credential successfully recorded on blockchain'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_credential(self, credential_id: str) -> Dict[str, Any]:
        """Verify a credential exists on the blockchain"""
        # Search through all blocks for the credential
        for block in self.chain:
            if 'transactions' in block.data:
                for transaction in block.data['transactions']:
                    if (transaction.get('type') == 'CREDENTIAL_ISSUANCE' and 
                        transaction.get('credential_id') == credential_id):
                        return {
                            'valid': True,
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'transaction': transaction,
                            'verification_time': datetime.now().isoformat()
                        }
        
        return {
            'valid': False,
            'error': 'Credential not found on blockchain'
        }
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash at block {i}")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash at block {i}")
                return False
        
        print("Blockchain is valid!")
        return True
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get comprehensive blockchain statistics"""
        total_transactions = 0
        credential_count = 0
        institution_count = 0
        student_count = 0
        
        for block in self.chain:
            if 'transactions' in block.data:
                total_transactions += len(block.data['transactions'])
                for transaction in block.data['transactions']:
                    if transaction.get('type') == 'CREDENTIAL_ISSUANCE':
                        credential_count += 1
                    elif transaction.get('type') == 'INSTITUTION_REGISTRATION':
                        institution_count += 1
                    elif transaction.get('type') == 'STUDENT_REGISTRATION':
                        student_count += 1
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'credentials_issued': credential_count,
            'institutions_registered': institution_count,
            'students_registered': student_count,
            'chain_difficulty': self.difficulty,
            'latest_block_hash': self.get_latest_block().hash,
            'chain_valid': self.is_chain_valid(),
            'blockchain_size_kb': len(json.dumps(self.to_dict())) / 1024
        }
    
    def get_recent_blocks(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent blocks for display"""
        recent_blocks = self.chain[-count:] if len(self.chain) >= count else self.chain
        return [block.to_dict() for block in reversed(recent_blocks)]
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert entire blockchain to dictionary"""
        return [block.to_dict() for block in self.chain]

# Global blockchain instance
academic_blockchain = AcademicBlockchain(difficulty=2)

# Initialize with some sample institutions for demo
sample_institutions = [
    {
        'institution_id': 'iitm_001',
        'name': 'Indian Institute of Technology Madras (IIT Madras)',
        'location': 'Chennai, Tamil Nadu',
        'type': 'Engineering'
    },
    {
        'institution_id': 'anna_university_001',
        'name': 'Anna University',
        'location': 'Chennai, Tamil Nadu',
        'type': 'Engineering & Technology'
    }
]

# Register sample institutions
for institution in sample_institutions:
    academic_blockchain.register_institution(institution)

# Mine the initial transactions
academic_blockchain.mine_pending_transactions('GENESIS_MINER')

print("Enhanced Academic Blockchain ready for Smart India Hackathon!")
