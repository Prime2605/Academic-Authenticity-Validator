"""
ML Forensics Engine for Advanced Certificate Analysis
Implements machine learning models for forgery detection and database matching
"""

import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import hashlib
import pickle
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import cv2
from PIL import Image
import io
import base64
from difflib import SequenceMatcher
import re
from fuzzywuzzy import fuzz, process

class MLForensicsEngine:
    """Advanced ML-based forensics and database matching system"""
    
    def __init__(self):
        self.models_directory = "ml_models"
        self.training_data_file = "ml_training_data.json"
        self.feature_cache_file = "feature_cache.json"
        self.matching_patterns_file = "matching_patterns.json"
        
        # Create directories
        os.makedirs(self.models_directory, exist_ok=True)
        
        self.load_training_data()
        self.load_feature_cache()
        self.load_matching_patterns()
        self.initialize_models()
    
    def load_training_data(self):
        """Load ML training data"""
        if os.path.exists(self.training_data_file):
            try:
                with open(self.training_data_file, 'r') as f:
                    self.training_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                # If file is corrupted, create new training data
                self.create_default_training_data()
                self.save_training_data()
        else:
            self.create_default_training_data()
            self.save_training_data()
    
    def create_default_training_data(self):
        """Create default training data structure"""
        self.training_data = {
            'forgery_detection': {
                'features': [],
                'labels': [],
                'feature_names': [
                    'edge_density', 'noise_variance', 'compression_artifacts',
                    'font_consistency', 'color_histogram_variance', 'text_alignment',
                    'logo_similarity', 'paper_texture', 'ink_consistency'
                ]
            },
            'authenticity_classification': {
                'features': [],
                'labels': [],
                'classes': ['GENUINE', 'FORGED', 'SUSPICIOUS', 'UNCERTAIN']
            },
            'institution_matching': {
                'institution_features': [],
                'similarity_scores': []
            }
        }
    
    def save_training_data(self):
        """Save ML training data"""
        with open(self.training_data_file, 'w') as f:
            json.dump(self.training_data, f, indent=2)
    
    def load_feature_cache(self):
        """Load cached features for faster processing"""
        if os.path.exists(self.feature_cache_file):
            try:
                with open(self.feature_cache_file, 'r') as f:
                    self.feature_cache = json.load(f)
            except (json.JSONDecodeError, ValueError):
                # If file is corrupted, create new cache
                self.feature_cache = {
                    'image_features': {},
                    'text_features': {},
                    'institution_features': {}
                }
                self.save_feature_cache()
        else:
            self.feature_cache = {
                'image_features': {},
                'text_features': {},
                'institution_features': {}
            }
    
    def save_feature_cache(self):
        """Save feature cache"""
        with open(self.feature_cache_file, 'w') as f:
            json.dump(self.feature_cache, f, indent=2)
    
    def load_matching_patterns(self):
        """Load patterns for database matching"""
        if os.path.exists(self.matching_patterns_file):
            try:
                with open(self.matching_patterns_file, 'r') as f:
                    self.matching_patterns = json.load(f)
            except (json.JSONDecodeError, ValueError):
                # If file is corrupted, create new patterns
                self.create_default_matching_patterns()
                self.save_matching_patterns()
        else:
            self.create_default_matching_patterns()
            self.save_matching_patterns()
    
    def create_default_matching_patterns(self):
        """Create default matching patterns"""
        self.matching_patterns = {
            'institution_aliases': {
                'iit_madras': ['IIT Madras', 'Indian Institute of Technology Madras', 'IITM'],
                'anna_university': ['Anna University', 'AU', 'Anna Univ'],
                'loyola_college': ['Loyola College', 'Loyola College Chennai', 'LC']
            },
            'degree_patterns': {
                'bachelor_engineering': ['B.E.', 'BE', 'Bachelor of Engineering', 'B.Eng'],
                'bachelor_technology': ['B.Tech', 'BTech', 'Bachelor of Technology', 'B.Tech.'],
                'master_science': ['M.S.', 'MS', 'Master of Science', 'M.Sc', 'MSc']
            },
            'common_misspellings': {
                'engineering': ['engg', 'enginering', 'enginnering'],
                'university': ['univercity', 'universty', 'univeristy'],
                'technology': ['tecnology', 'techology', 'technolgy']
            }
        }
    
    def save_matching_patterns(self):
        """Save matching patterns"""
        with open(self.matching_patterns_file, 'w') as f:
            json.dump(self.matching_patterns, f, indent=2)
    
    def initialize_models(self):
        """Initialize ML models"""
        # Forgery Detection Model
        self.forgery_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Anomaly Detection Model
        self.anomaly_model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Feature Scaler
        self.scaler = StandardScaler()
        
        # Load pre-trained models if available
        self.load_trained_models()
    
    def load_trained_models(self):
        """Load pre-trained models from disk"""
        model_files = {
            'forgery_model': os.path.join(self.models_directory, 'forgery_model.pkl'),
            'anomaly_model': os.path.join(self.models_directory, 'anomaly_model.pkl'),
            'scaler': os.path.join(self.models_directory, 'scaler.pkl')
        }
        
        for model_name, file_path in model_files.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        setattr(self, model_name, pickle.load(f))
                except Exception as e:
                    print(f"Warning: Could not load {model_name}: {e}")
    
    def save_trained_models(self):
        """Save trained models to disk"""
        models = {
            'forgery_model': self.forgery_model,
            'anomaly_model': self.anomaly_model,
            'scaler': self.scaler
        }
        
        for model_name, model in models.items():
            file_path = os.path.join(self.models_directory, f'{model_name}.pkl')
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(model, f)
            except Exception as e:
                print(f"Warning: Could not save {model_name}: {e}")
    
    def extract_advanced_features(self, image_data: bytes, certificate_data: Dict[str, Any]) -> np.ndarray:
        """Extract advanced features for ML analysis"""
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # Check cache first
        if image_hash in self.feature_cache['image_features']:
            return np.array(self.feature_cache['image_features'][image_hash])
        
        try:
            # Convert image data
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            features = []
            
            # 1. Edge Density Features
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # 2. Noise Analysis
            noise_variance = np.var(gray.astype(np.float32))
            features.append(noise_variance / 10000)  # Normalize
            
            # 3. Compression Artifacts
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, encoded_img = cv2.imencode('.jpg', image, encode_param)
            decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
            compression_diff = np.mean(np.abs(image.astype(np.float32) - decoded_img.astype(np.float32)))
            features.append(compression_diff / 100)  # Normalize
            
            # 4. Font Consistency
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            font_sizes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 10 < w < 100 and 10 < h < 100:
                    font_sizes.append(h)
            
            font_variance = np.var(font_sizes) if font_sizes else 0
            features.append(font_variance / 100)  # Normalize
            
            # 5. Color Histogram Variance
            hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
            hist_variance = np.var(hist_b) + np.var(hist_g) + np.var(hist_r)
            features.append(hist_variance / 1000000)  # Normalize
            
            # 6. Text Alignment Analysis
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            if lines is not None:
                angles = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    angles.append(angle)
                text_alignment = np.std(angles) if angles else 0
            else:
                text_alignment = 0
            features.append(text_alignment / 10)  # Normalize
            
            # 7. Logo/Seal Similarity (simplified)
            # In production, this would use template matching
            logo_region = gray[50:150, 50:150] if gray.shape[0] > 150 and gray.shape[1] > 150 else gray
            logo_features = cv2.calcHist([logo_region], [0], None, [256], [0, 256])
            logo_similarity = np.std(logo_features)
            features.append(logo_similarity / 1000)  # Normalize
            
            # 8. Paper Texture Analysis
            # Use Local Binary Pattern for texture analysis
            texture_variance = np.var(cv2.Laplacian(gray, cv2.CV_64F))
            features.append(texture_variance / 10000)  # Normalize
            
            # 9. Ink Consistency (color uniformity in text regions)
            # Simplified analysis of color consistency
            text_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            text_regions = cv2.bitwise_and(image, image, mask=255-text_mask)
            ink_consistency = np.std(text_regions) if np.any(text_regions) else 0
            features.append(ink_consistency / 100)  # Normalize
            
            # Cache the features
            self.feature_cache['image_features'][image_hash] = features
            self.save_feature_cache()
            
            return np.array(features)
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            # Return default features if extraction fails
            return np.zeros(9)
    
    def predict_forgery_probability(self, image_data: bytes, certificate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict probability of document being forged using ML"""
        try:
            # Extract features
            features = self.extract_advanced_features(image_data, certificate_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Predict using forgery model
            if hasattr(self.forgery_model, 'predict_proba'):
                try:
                    forgery_probability = self.forgery_model.predict_proba(features_scaled)[0]
                    if len(forgery_probability) >= 2:
                        forgery_score = forgery_probability[1]  # Probability of being forged
                    else:
                        forgery_score = 0.5  # Default if model not trained
                except:
                    forgery_score = 0.5  # Default if prediction fails
            else:
                forgery_score = 0.5  # Default if model not trained
            
            # Anomaly detection
            anomaly_score = self.anomaly_model.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_model.predict(features_scaled)[0] == -1
            
            # Combine scores
            combined_score = (forgery_score * 0.7) + (0.3 if is_anomaly else 0.0)
            
            # Classify authenticity
            if combined_score < 0.2:
                authenticity_class = 'GENUINE'
                confidence = 95
            elif combined_score < 0.4:
                authenticity_class = 'LIKELY_GENUINE'
                confidence = 80
            elif combined_score < 0.6:
                authenticity_class = 'UNCERTAIN'
                confidence = 60
            elif combined_score < 0.8:
                authenticity_class = 'SUSPICIOUS'
                confidence = 40
            else:
                authenticity_class = 'LIKELY_FORGED'
                confidence = 20
            
            return {
                'forgery_probability': round(combined_score, 4),
                'authenticity_class': authenticity_class,
                'confidence': confidence,
                'anomaly_detected': is_anomaly,
                'anomaly_score': round(float(anomaly_score), 4),
                'feature_vector': features.tolist(),
                'ml_analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'ML forgery prediction failed: {str(e)}',
                'forgery_probability': 0.5,
                'authenticity_class': 'UNCERTAIN',
                'confidence': 0
            }
    
    def advanced_database_matching(self, certificate_data: Dict[str, Any], database_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Advanced database matching using ML and fuzzy matching"""
        try:
            best_matches = []
            
            # Extract key fields for matching
            query_fields = {
                'student_name': certificate_data.get('student_name', ''),
                'institution_name': certificate_data.get('institution_name', ''),
                'degree_type': certificate_data.get('degree_type', ''),
                'field_of_study': certificate_data.get('field_of_study', ''),
                'graduation_date': certificate_data.get('graduation_date', ''),
                'student_id': certificate_data.get('student_id', ''),
                'verification_code': certificate_data.get('verification_code', '')
            }
            
            for record in database_records:
                match_score = self.calculate_comprehensive_match_score(query_fields, record)
                
                if match_score['overall_score'] > 0.3:  # Threshold for potential matches
                    best_matches.append({
                        'record': record,
                        'match_score': match_score,
                        'overall_similarity': match_score['overall_score']
                    })
            
            # Sort by similarity score
            best_matches.sort(key=lambda x: x['overall_similarity'], reverse=True)
            
            # Analyze match quality
            if best_matches:
                top_match = best_matches[0]
                if top_match['overall_similarity'] > 0.9:
                    match_quality = 'EXACT'
                elif top_match['overall_similarity'] > 0.7:
                    match_quality = 'HIGH'
                elif top_match['overall_similarity'] > 0.5:
                    match_quality = 'MEDIUM'
                else:
                    match_quality = 'LOW'
                
                return {
                    'matches_found': len(best_matches),
                    'best_match': top_match,
                    'match_quality': match_quality,
                    'all_matches': best_matches[:5],  # Top 5 matches
                    'matching_confidence': round(top_match['overall_similarity'] * 100, 2)
                }
            else:
                return {
                    'matches_found': 0,
                    'match_quality': 'NONE',
                    'matching_confidence': 0,
                    'message': 'No similar records found in database'
                }
                
        except Exception as e:
            return {
                'error': f'Database matching failed: {str(e)}',
                'matches_found': 0,
                'matching_confidence': 0
            }
    
    def calculate_comprehensive_match_score(self, query_fields: Dict[str, str], record: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive match score between query and database record"""
        field_scores = {}
        weights = {
            'verification_code': 0.3,
            'student_id': 0.2,
            'student_name': 0.2,
            'institution_name': 0.1,
            'degree_type': 0.1,
            'field_of_study': 0.05,
            'graduation_date': 0.05
        }
        
        for field, weight in weights.items():
            query_value = query_fields.get(field, '').strip().lower()
            record_value = str(record.get(field, '')).strip().lower()
            
            if not query_value or not record_value:
                field_scores[field] = 0.0
                continue
            
            # Exact match
            if query_value == record_value:
                field_scores[field] = 1.0
            else:
                # Fuzzy matching
                similarity = fuzz.ratio(query_value, record_value) / 100.0
                
                # Apply field-specific matching rules
                if field == 'student_name':
                    # Handle name variations
                    similarity = max(similarity, self.match_name_variations(query_value, record_value))
                elif field == 'institution_name':
                    # Handle institution aliases
                    similarity = max(similarity, self.match_institution_aliases(query_value, record_value))
                elif field == 'degree_type':
                    # Handle degree pattern matching
                    similarity = max(similarity, self.match_degree_patterns(query_value, record_value))
                elif field == 'graduation_date':
                    # Handle date variations
                    similarity = max(similarity, self.match_date_variations(query_value, record_value))
                
                field_scores[field] = similarity
        
        # Calculate weighted overall score
        overall_score = sum(field_scores[field] * weights[field] for field in weights.keys())
        
        return {
            'overall_score': round(overall_score, 4),
            'field_scores': field_scores,
            'weights_used': weights
        }
    
    def match_name_variations(self, query_name: str, record_name: str) -> float:
        """Match name variations (initials, order, etc.)"""
        # Split names into parts
        query_parts = query_name.split()
        record_parts = record_name.split()
        
        # Try different name matching strategies
        strategies = [
            # Direct fuzzy match
            fuzz.ratio(query_name, record_name) / 100.0,
            # Token sort ratio
            fuzz.token_sort_ratio(query_name, record_name) / 100.0,
            # Partial ratio
            fuzz.partial_ratio(query_name, record_name) / 100.0
        ]
        
        # Check if one name is subset of another (initials)
        if len(query_parts) != len(record_parts):
            shorter = query_parts if len(query_parts) < len(record_parts) else record_parts
            longer = record_parts if len(query_parts) < len(record_parts) else query_parts
            
            initial_match = all(
                any(part.startswith(short_part[0]) for part in longer)
                for short_part in shorter if short_part
            )
            
            if initial_match:
                strategies.append(0.8)  # High score for initial matching
        
        return max(strategies)
    
    def match_institution_aliases(self, query_inst: str, record_inst: str) -> float:
        """Match institution names considering aliases"""
        # Check known aliases
        for canonical_name, aliases in self.matching_patterns['institution_aliases'].items():
            if any(alias.lower() in query_inst for alias in aliases) and \
               any(alias.lower() in record_inst for alias in aliases):
                return 0.95  # High score for alias match
        
        # Fuzzy matching with common abbreviations
        query_normalized = self.normalize_institution_name(query_inst)
        record_normalized = self.normalize_institution_name(record_inst)
        
        return fuzz.ratio(query_normalized, record_normalized) / 100.0
    
    def normalize_institution_name(self, name: str) -> str:
        """Normalize institution name for better matching"""
        # Remove common words and abbreviations
        common_words = ['university', 'college', 'institute', 'of', 'technology', 'the', 'and']
        words = name.lower().split()
        normalized_words = [word for word in words if word not in common_words]
        return ' '.join(normalized_words)
    
    def match_degree_patterns(self, query_degree: str, record_degree: str) -> float:
        """Match degree types considering common patterns"""
        # Check known degree patterns
        for canonical_degree, patterns in self.matching_patterns['degree_patterns'].items():
            query_match = any(pattern.lower() in query_degree for pattern in patterns)
            record_match = any(pattern.lower() in record_degree for pattern in patterns)
            
            if query_match and record_match:
                return 0.9  # High score for pattern match
        
        return fuzz.ratio(query_degree, record_degree) / 100.0
    
    def match_date_variations(self, query_date: str, record_date: str) -> float:
        """Match date variations (different formats)"""
        # Extract year from both dates
        query_year = re.search(r'\b(19|20)\d{2}\b', query_date)
        record_year = re.search(r'\b(19|20)\d{2}\b', record_date)
        
        if query_year and record_year:
            if query_year.group() == record_year.group():
                return 0.8  # Good match if years are same
        
        return fuzz.ratio(query_date, record_date) / 100.0
    
    def train_models_with_new_data(self, new_training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train models with new data"""
        try:
            # Add new data to training set
            for data_point in new_training_data:
                if 'features' in data_point and 'label' in data_point:
                    self.training_data['forgery_detection']['features'].append(data_point['features'])
                    self.training_data['forgery_detection']['labels'].append(data_point['label'])
            
            # Prepare training data
            features = np.array(self.training_data['forgery_detection']['features'])
            labels = np.array(self.training_data['forgery_detection']['labels'])
            
            if len(features) < 10:
                return {
                    'success': False,
                    'message': 'Insufficient training data (minimum 10 samples required)',
                    'samples_available': len(features)
                }
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train forgery detection model
            self.forgery_model.fit(X_train_scaled, y_train)
            
            # Train anomaly detection model
            # Use only genuine samples for anomaly detection
            genuine_samples = X_train_scaled[y_train == 0]  # Assuming 0 = genuine, 1 = forged
            if len(genuine_samples) > 0:
                self.anomaly_model.fit(genuine_samples)
            
            # Evaluate models
            y_pred = self.forgery_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save trained models
            self.save_trained_models()
            self.save_training_data()
            
            return {
                'success': True,
                'training_samples': len(features),
                'test_accuracy': round(accuracy, 4),
                'model_performance': {
                    'accuracy': accuracy,
                    'training_samples': len(X_train),
                    'test_samples': len(X_test)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Model training failed: {str(e)}'
            }
    
    def get_ml_statistics(self) -> Dict[str, Any]:
        """Get ML engine statistics"""
        return {
            'training_data_size': len(self.training_data['forgery_detection']['features']),
            'feature_cache_size': len(self.feature_cache['image_features']),
            'models_available': {
                'forgery_model': hasattr(self.forgery_model, 'n_estimators'),
                'anomaly_model': hasattr(self.anomaly_model, 'contamination'),
                'scaler': hasattr(self.scaler, 'mean_')
            },
            'matching_patterns': {
                'institution_aliases': len(self.matching_patterns['institution_aliases']),
                'degree_patterns': len(self.matching_patterns['degree_patterns']),
                'common_misspellings': len(self.matching_patterns['common_misspellings'])
            },
            'last_updated': datetime.now().isoformat()
        }

# Global ML forensics engine instance
ml_forensics_engine = MLForensicsEngine()
