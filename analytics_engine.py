"""
Advanced Analytics Engine for Academic Authenticity Validator
Provides comprehensive analytics, insights, and reporting
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
import time

class AnalyticsEngine:
    """Advanced analytics system for academic certificates"""
    
    def __init__(self):
        self.analytics_file = "analytics_data.json"
        self.load_analytics_data()
    
    def load_analytics_data(self):
        """Load existing analytics data"""
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'r') as f:
                self.analytics_data = json.load(f)
        else:
            self.analytics_data = {
                'verification_logs': [],
                'issuance_logs': [],
                'access_logs': [],
                'performance_metrics': {},
                'institution_stats': {},
                'time_series_data': {},
                'user_behavior': {},
                'certificate_trends': {}
            }
    
    def save_analytics_data(self):
        """Save analytics data to file"""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics_data, f, indent=2)
    
    def log_verification(self, verification_code: str, certificate_data: Dict[str, Any], 
                        success: bool, user_ip: str = None):
        """Log certificate verification activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'verification_code': verification_code,
            'student_name': certificate_data.get('student_name', 'Unknown'),
            'institution_id': certificate_data.get('institution_id', 'Unknown'),
            'institution_name': certificate_data.get('institution_name', 'Unknown'),
            'degree_type': certificate_data.get('degree_type', 'Unknown'),
            'success': success,
            'user_ip': user_ip,
            'response_time': time.time()
        }
        
        self.analytics_data['verification_logs'].append(log_entry)
        self.update_institution_stats(certificate_data.get('institution_id'), 'verification')
        self.update_time_series('verifications')
        self.save_analytics_data()
    
    def log_issuance(self, certificate_data: Dict[str, Any], blockchain_hash: str = None):
        """Log certificate issuance activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'certificate_id': certificate_data.get('certificate_id', 'Unknown'),
            'student_name': certificate_data.get('student_name', 'Unknown'),
            'institution_id': certificate_data.get('institution_id', 'Unknown'),
            'institution_name': certificate_data.get('institution_name', 'Unknown'),
            'degree_type': certificate_data.get('degree_type', 'Unknown'),
            'field_of_study': certificate_data.get('field_of_study', 'Unknown'),
            'blockchain_hash': blockchain_hash,
            'blockchain_enabled': blockchain_hash is not None
        }
        
        self.analytics_data['issuance_logs'].append(log_entry)
        self.update_institution_stats(certificate_data.get('institution_id'), 'issuance')
        self.update_time_series('issuances')
        self.update_certificate_trends(certificate_data)
        self.save_analytics_data()
    
    def log_access(self, endpoint: str, user_ip: str = None, response_time: float = None):
        """Log system access and API usage"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'user_ip': user_ip,
            'response_time': response_time
        }
        
        self.analytics_data['access_logs'].append(log_entry)
        self.update_performance_metrics(endpoint, response_time)
        self.save_analytics_data()
    
    def update_institution_stats(self, institution_id: str, activity_type: str):
        """Update institution-specific statistics"""
        if institution_id not in self.analytics_data['institution_stats']:
            self.analytics_data['institution_stats'][institution_id] = {
                'verifications': 0,
                'issuances': 0,
                'last_activity': None,
                'total_certificates': 0
            }
        
        self.analytics_data['institution_stats'][institution_id][f'{activity_type}s'] += 1
        self.analytics_data['institution_stats'][institution_id]['last_activity'] = datetime.now().isoformat()
        
        if activity_type == 'issuance':
            self.analytics_data['institution_stats'][institution_id]['total_certificates'] += 1
    
    def update_time_series(self, metric_type: str):
        """Update time series data for trends"""
        today = datetime.now().strftime('%Y-%m-%d')
        hour = datetime.now().strftime('%Y-%m-%d-%H')
        
        if metric_type not in self.analytics_data['time_series_data']:
            self.analytics_data['time_series_data'][metric_type] = {
                'daily': {},
                'hourly': {}
            }
        
        # Daily stats
        if today not in self.analytics_data['time_series_data'][metric_type]['daily']:
            self.analytics_data['time_series_data'][metric_type]['daily'][today] = 0
        self.analytics_data['time_series_data'][metric_type]['daily'][today] += 1
        
        # Hourly stats
        if hour not in self.analytics_data['time_series_data'][metric_type]['hourly']:
            self.analytics_data['time_series_data'][metric_type]['hourly'][hour] = 0
        self.analytics_data['time_series_data'][metric_type]['hourly'][hour] += 1
    
    def update_performance_metrics(self, endpoint: str, response_time: float):
        """Update API performance metrics"""
        if response_time is None:
            return
        
        if endpoint not in self.analytics_data['performance_metrics']:
            self.analytics_data['performance_metrics'][endpoint] = {
                'total_requests': 0,
                'total_response_time': 0,
                'average_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0
            }
        
        metrics = self.analytics_data['performance_metrics'][endpoint]
        metrics['total_requests'] += 1
        metrics['total_response_time'] += response_time
        metrics['average_response_time'] = metrics['total_response_time'] / metrics['total_requests']
        metrics['min_response_time'] = min(metrics['min_response_time'], response_time)
        metrics['max_response_time'] = max(metrics['max_response_time'], response_time)
    
    def update_certificate_trends(self, certificate_data: Dict[str, Any]):
        """Update certificate trends and patterns"""
        degree_type = certificate_data.get('degree_type', 'Unknown')
        field_of_study = certificate_data.get('field_of_study', 'Unknown')
        
        if 'degree_types' not in self.analytics_data['certificate_trends']:
            self.analytics_data['certificate_trends']['degree_types'] = {}
        if 'fields_of_study' not in self.analytics_data['certificate_trends']:
            self.analytics_data['certificate_trends']['fields_of_study'] = {}
        
        # Count degree types
        if degree_type not in self.analytics_data['certificate_trends']['degree_types']:
            self.analytics_data['certificate_trends']['degree_types'][degree_type] = 0
        self.analytics_data['certificate_trends']['degree_types'][degree_type] += 1
        
        # Count fields of study
        if field_of_study and field_of_study != 'Unknown':
            if field_of_study not in self.analytics_data['certificate_trends']['fields_of_study']:
                self.analytics_data['certificate_trends']['fields_of_study'][field_of_study] = 0
            self.analytics_data['certificate_trends']['fields_of_study'][field_of_study] += 1
    
    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics for dashboard"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        this_week_start = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Basic counts
        total_verifications = len(self.analytics_data['verification_logs'])
        total_issuances = len(self.analytics_data['issuance_logs'])
        total_institutions = len(self.analytics_data['institution_stats'])
        
        # Today's activity
        today_verifications = self.analytics_data['time_series_data'].get('verifications', {}).get('daily', {}).get(today, 0)
        today_issuances = self.analytics_data['time_series_data'].get('issuances', {}).get('daily', {}).get(today, 0)
        
        # Yesterday's activity for comparison
        yesterday_verifications = self.analytics_data['time_series_data'].get('verifications', {}).get('daily', {}).get(yesterday, 0)
        yesterday_issuances = self.analytics_data['time_series_data'].get('issuances', {}).get('daily', {}).get(yesterday, 0)
        
        # Growth calculations
        verification_growth = self.calculate_growth(today_verifications, yesterday_verifications)
        issuance_growth = self.calculate_growth(today_issuances, yesterday_issuances)
        
        # Top institutions
        top_institutions = self.get_top_institutions(5)
        
        # Recent activity
        recent_verifications = self.analytics_data['verification_logs'][-10:] if self.analytics_data['verification_logs'] else []
        recent_issuances = self.analytics_data['issuance_logs'][-10:] if self.analytics_data['issuance_logs'] else []
        
        # Certificate trends
        degree_trends = self.analytics_data['certificate_trends'].get('degree_types', {})
        field_trends = self.analytics_data['certificate_trends'].get('fields_of_study', {})
        
        # Weekly trends
        weekly_data = self.get_weekly_trends()
        
        return {
            'overview': {
                'total_verifications': total_verifications,
                'total_issuances': total_issuances,
                'total_institutions': total_institutions,
                'active_certificates': total_issuances
            },
            'today_stats': {
                'verifications': today_verifications,
                'issuances': today_issuances,
                'verification_growth': verification_growth,
                'issuance_growth': issuance_growth
            },
            'top_institutions': top_institutions,
            'recent_activity': {
                'verifications': recent_verifications,
                'issuances': recent_issuances
            },
            'trends': {
                'degree_types': dict(sorted(degree_trends.items(), key=lambda x: x[1], reverse=True)[:10]),
                'fields_of_study': dict(sorted(field_trends.items(), key=lambda x: x[1], reverse=True)[:10]),
                'weekly_data': weekly_data
            },
            'performance': self.get_performance_summary()
        }
    
    def calculate_growth(self, current: int, previous: int) -> float:
        """Calculate growth percentage"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)
    
    def get_top_institutions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top institutions by activity"""
        institutions = []
        for inst_id, stats in self.analytics_data['institution_stats'].items():
            total_activity = stats['verifications'] + stats['issuances']
            institutions.append({
                'institution_id': inst_id,
                'total_activity': total_activity,
                'verifications': stats['verifications'],
                'issuances': stats['issuances'],
                'certificates': stats['total_certificates'],
                'last_activity': stats['last_activity']
            })
        
        return sorted(institutions, key=lambda x: x['total_activity'], reverse=True)[:limit]
    
    def get_weekly_trends(self) -> Dict[str, List]:
        """Get weekly trends for charts"""
        now = datetime.now()
        weekly_data = {
            'dates': [],
            'verifications': [],
            'issuances': []
        }
        
        for i in range(7):
            date = (now - timedelta(days=6-i)).strftime('%Y-%m-%d')
            weekly_data['dates'].append(date)
            
            verifications = self.analytics_data['time_series_data'].get('verifications', {}).get('daily', {}).get(date, 0)
            issuances = self.analytics_data['time_series_data'].get('issuances', {}).get('daily', {}).get(date, 0)
            
            weekly_data['verifications'].append(verifications)
            weekly_data['issuances'].append(issuances)
        
        return weekly_data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get API performance summary"""
        performance_data = {}
        for endpoint, metrics in self.analytics_data['performance_metrics'].items():
            performance_data[endpoint] = {
                'requests': metrics['total_requests'],
                'avg_response_time': round(metrics['average_response_time'], 3),
                'min_response_time': round(metrics['min_response_time'], 3),
                'max_response_time': round(metrics['max_response_time'], 3)
            }
        
        return performance_data
    
    def get_institution_analytics(self, institution_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific institution"""
        if institution_id not in self.analytics_data['institution_stats']:
            return {'error': 'Institution not found'}
        
        stats = self.analytics_data['institution_stats'][institution_id]
        
        # Get certificates issued by this institution
        institution_certificates = [
            log for log in self.analytics_data['issuance_logs']
            if log.get('institution_id') == institution_id
        ]
        
        # Get verifications for this institution's certificates
        institution_verifications = [
            log for log in self.analytics_data['verification_logs']
            if log.get('institution_id') == institution_id
        ]
        
        # Degree type distribution
        degree_distribution = Counter([cert.get('degree_type', 'Unknown') for cert in institution_certificates])
        
        return {
            'institution_id': institution_id,
            'summary': stats,
            'certificates_issued': len(institution_certificates),
            'total_verifications': len(institution_verifications),
            'degree_distribution': dict(degree_distribution),
            'recent_certificates': institution_certificates[-5:],
            'recent_verifications': institution_verifications[-5:]
        }
    
    def export_analytics_report(self) -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_dashboard_analytics(),
            'raw_data': {
                'total_verification_logs': len(self.analytics_data['verification_logs']),
                'total_issuance_logs': len(self.analytics_data['issuance_logs']),
                'total_access_logs': len(self.analytics_data['access_logs']),
                'institutions_tracked': len(self.analytics_data['institution_stats'])
            },
            'performance_metrics': self.analytics_data['performance_metrics'],
            'institution_stats': self.analytics_data['institution_stats']
        }

# Global analytics engine instance
analytics_engine = AnalyticsEngine()
