"""
OCR & Forensics Engine for Academic Certificate Validation
Implements Tesseract + Google Vision for document analysis and forgery detection
"""

import cv2
import numpy as np
import pytesseract
import os
from PIL import Image, ImageEnhance, ImageFilter
import base64
import io
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime
import hashlib
import re

class OCRForensicsEngine:
    """Advanced OCR and forensics analysis for academic certificates"""
    
    def __init__(self):
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path as needed
        self.confidence_threshold = 60
        self.forensics_results_file = "forensics_analysis.json"
        self.load_forensics_data()
    
    def load_forensics_data(self):
        """Load existing forensics analysis data"""
        if os.path.exists(self.forensics_results_file):
            with open(self.forensics_results_file, 'r') as f:
                self.forensics_data = json.load(f)
        else:
            self.forensics_data = {
                'analyzed_documents': [],
                'forgery_patterns': [],
                'genuine_patterns': [],
                'ml_training_data': []
            }
    
    def save_forensics_data(self):
        """Save forensics analysis data"""
        with open(self.forensics_results_file, 'w') as f:
            json.dump(self.forensics_data, f, indent=2)
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Advanced image preprocessing for better OCR accuracy"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance image quality
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoisingColored(opencv_image, None, 10, 10, 7, 21)
        
        # Convert to grayscale
        gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_with_confidence(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using Tesseract OCR with confidence scores"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:-/ '
            
            # Extract text with confidence
            data = pytesseract.image_to_data(processed_image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Filter high-confidence text
            extracted_text = []
            confidence_scores = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        extracted_text.append(text)
                        confidence_scores.append(int(conf))
            
            full_text = ' '.join(extracted_text)
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                'extracted_text': full_text,
                'confidence_scores': confidence_scores,
                'average_confidence': avg_confidence,
                'word_count': len(extracted_text),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'OCR extraction failed: {str(e)}',
                'extracted_text': '',
                'confidence_scores': [],
                'average_confidence': 0
            }
    
    def detect_forgery_patterns(self, image_data: bytes) -> Dict[str, Any]:
        """Advanced forensics analysis to detect document forgery"""
        try:
            # Convert to OpenCV format
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            forensics_results = {
                'timestamp': datetime.now().isoformat(),
                'image_hash': hashlib.sha256(image_data).hexdigest(),
                'analysis_results': {}
            }
            
            # 1. Edge Analysis - Detect inconsistent edges (copy-paste forgery)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            forensics_results['analysis_results']['edge_density'] = float(edge_density)
            
            # 2. Noise Analysis - Detect inconsistent noise patterns
            noise_variance = np.var(gray.astype(np.float32))
            forensics_results['analysis_results']['noise_variance'] = float(noise_variance)
            
            # 3. Compression Artifacts Analysis
            # Convert to JPEG and back to detect compression inconsistencies
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, encoded_img = cv2.imencode('.jpg', image, encode_param)
            decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
            compression_diff = np.mean(np.abs(image.astype(np.float32) - decoded_img.astype(np.float32)))
            forensics_results['analysis_results']['compression_artifacts'] = float(compression_diff)
            
            # 4. Font Consistency Analysis
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            font_sizes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if 10 < w < 100 and 10 < h < 100:  # Likely text
                    font_sizes.append(h)
            
            if font_sizes:
                font_variance = np.var(font_sizes)
                forensics_results['analysis_results']['font_consistency'] = float(font_variance)
            else:
                forensics_results['analysis_results']['font_consistency'] = 0.0
            
            # 5. Color Histogram Analysis
            hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
            
            hist_variance = np.var(hist_b) + np.var(hist_g) + np.var(hist_r)
            forensics_results['analysis_results']['color_histogram_variance'] = float(hist_variance)
            
            # 6. Calculate Forgery Probability
            forgery_score = self.calculate_forgery_probability(forensics_results['analysis_results'])
            forensics_results['forgery_probability'] = forgery_score
            forensics_results['authenticity_level'] = self.get_authenticity_level(forgery_score)
            
            return forensics_results
            
        except Exception as e:
            return {
                'error': f'Forensics analysis failed: {str(e)}',
                'forgery_probability': 0.5,
                'authenticity_level': 'UNKNOWN'
            }
    
    def calculate_forgery_probability(self, analysis_results: Dict[str, float]) -> float:
        """Calculate probability of document being forged based on analysis"""
        # Weighted scoring system
        weights = {
            'edge_density': 0.2,
            'noise_variance': 0.15,
            'compression_artifacts': 0.25,
            'font_consistency': 0.25,
            'color_histogram_variance': 0.15
        }
        
        # Normalize and score each metric
        scores = {}
        
        # Edge density (higher = more suspicious)
        edge_density = analysis_results.get('edge_density', 0)
        scores['edge_density'] = min(edge_density * 10, 1.0)
        
        # Noise variance (very high or very low = suspicious)
        noise_var = analysis_results.get('noise_variance', 1000)
        if noise_var < 100 or noise_var > 5000:
            scores['noise_variance'] = 0.8
        else:
            scores['noise_variance'] = 0.2
        
        # Compression artifacts (higher = more suspicious)
        compression = analysis_results.get('compression_artifacts', 0)
        scores['compression_artifacts'] = min(compression / 50, 1.0)
        
        # Font consistency (higher variance = more suspicious)
        font_var = analysis_results.get('font_consistency', 0)
        scores['font_consistency'] = min(font_var / 100, 1.0)
        
        # Color histogram variance (extreme values = suspicious)
        color_var = analysis_results.get('color_histogram_variance', 1000000)
        if color_var < 100000 or color_var > 10000000:
            scores['color_histogram_variance'] = 0.7
        else:
            scores['color_histogram_variance'] = 0.3
        
        # Calculate weighted average
        forgery_probability = sum(scores[key] * weights[key] for key in weights.keys())
        return min(max(forgery_probability, 0.0), 1.0)
    
    def get_authenticity_level(self, forgery_probability: float) -> str:
        """Convert forgery probability to authenticity level"""
        if forgery_probability < 0.2:
            return 'HIGHLY_AUTHENTIC'
        elif forgery_probability < 0.4:
            return 'LIKELY_AUTHENTIC'
        elif forgery_probability < 0.6:
            return 'UNCERTAIN'
        elif forgery_probability < 0.8:
            return 'LIKELY_FORGED'
        else:
            return 'HIGHLY_SUSPICIOUS'
    
    def extract_certificate_fields(self, extracted_text: str) -> Dict[str, str]:
        """Extract specific certificate fields using pattern matching"""
        fields = {}
        
        # Common patterns for certificate fields
        patterns = {
            'student_name': r'(?:name|student|candidate)[:\s]+([A-Za-z\s]+?)(?:\n|degree|born)',
            'institution': r'(?:university|college|institute|institution)[:\s]+([A-Za-z\s&,.-]+?)(?:\n|hereby|certify)',
            'degree': r'(?:degree|bachelor|master|diploma|certificate)[:\s]+([A-Za-z\s&,.-]+?)(?:\n|in|from)',
            'field_of_study': r'(?:in|of|major)[:\s]+([A-Za-z\s&,.-]+?)(?:\n|with|on)',
            'graduation_date': r'(?:date|dated|on|graduated)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            'grade': r'(?:grade|cgpa|percentage|marks)[:\s]+([A-Za-z0-9.\s%]+?)(?:\n|out)',
            'registration_number': r'(?:registration|reg|roll|id)[:\s]+([A-Za-z0-9/-]+?)(?:\n|\s)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
            if match:
                fields[field] = match.group(1).strip()
            else:
                fields[field] = None
        
        return fields
    
    def comprehensive_analysis(self, image_data: bytes) -> Dict[str, Any]:
        """Perform comprehensive OCR and forensics analysis"""
        analysis_id = hashlib.sha256(image_data + str(datetime.now()).encode()).hexdigest()[:12]
        
        # OCR Analysis
        ocr_results = self.extract_text_with_confidence(image_data)
        
        # Forensics Analysis
        forensics_results = self.detect_forgery_patterns(image_data)
        
        # Field Extraction
        extracted_fields = {}
        if ocr_results.get('extracted_text'):
            extracted_fields = self.extract_certificate_fields(ocr_results['extracted_text'])
        
        # Combine results
        comprehensive_results = {
            'analysis_id': analysis_id,
            'timestamp': datetime.now().isoformat(),
            'ocr_analysis': ocr_results,
            'forensics_analysis': forensics_results,
            'extracted_fields': extracted_fields,
            'overall_confidence': self.calculate_overall_confidence(ocr_results, forensics_results),
            'recommendation': self.generate_recommendation(ocr_results, forensics_results)
        }
        
        # Store in forensics database
        self.forensics_data['analyzed_documents'].append(comprehensive_results)
        self.save_forensics_data()
        
        return comprehensive_results
    
    def calculate_overall_confidence(self, ocr_results: Dict, forensics_results: Dict) -> float:
        """Calculate overall confidence in document authenticity"""
        ocr_confidence = ocr_results.get('average_confidence', 0) / 100
        authenticity_confidence = 1 - forensics_results.get('forgery_probability', 0.5)
        
        # Weighted average
        overall_confidence = (ocr_confidence * 0.4) + (authenticity_confidence * 0.6)
        return round(overall_confidence * 100, 2)
    
    def generate_recommendation(self, ocr_results: Dict, forensics_results: Dict) -> str:
        """Generate human-readable recommendation"""
        ocr_conf = ocr_results.get('average_confidence', 0)
        forgery_prob = forensics_results.get('forgery_probability', 0.5)
        authenticity_level = forensics_results.get('authenticity_level', 'UNKNOWN')
        
        if ocr_conf > 80 and forgery_prob < 0.3:
            return "ACCEPT: High confidence in document authenticity and text extraction"
        elif ocr_conf > 60 and forgery_prob < 0.5:
            return "REVIEW: Moderate confidence, human verification recommended"
        elif forgery_prob > 0.7:
            return "REJECT: High probability of document forgery detected"
        else:
            return "MANUAL_REVIEW: Insufficient confidence for automated decision"
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get statistics from all analyzed documents"""
        total_docs = len(self.forensics_data['analyzed_documents'])
        
        if total_docs == 0:
            return {'total_analyzed': 0, 'message': 'No documents analyzed yet'}
        
        authenticity_levels = [doc['forensics_analysis'].get('authenticity_level', 'UNKNOWN') 
                             for doc in self.forensics_data['analyzed_documents']]
        
        level_counts = {}
        for level in authenticity_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        avg_confidence = sum(doc.get('overall_confidence', 0) 
                           for doc in self.forensics_data['analyzed_documents']) / total_docs
        
        return {
            'total_analyzed': total_docs,
            'authenticity_distribution': level_counts,
            'average_confidence': round(avg_confidence, 2),
            'last_analysis': self.forensics_data['analyzed_documents'][-1]['timestamp'] if total_docs > 0 else None
        }

# Global OCR forensics engine instance
ocr_forensics_engine = OCRForensicsEngine()
