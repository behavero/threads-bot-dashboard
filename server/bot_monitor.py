#!/usr/bin/env python3
"""
Bot Monitoring and Analytics System
Features:
- Real-time monitoring
- Performance metrics
- Alert system
- Analytics dashboard
- Ban risk assessment
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PostingMetrics:
    """Metrics for posting performance"""
    total_posts: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    last_post_time: Optional[datetime] = None
    posts_today: int = 0
    posts_this_week: int = 0

@dataclass
class AccountMetrics:
    """Metrics for individual accounts"""
    username: str
    posts_count: int = 0
    success_rate: float = 0.0
    last_post_time: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    ban_risk_score: float = 0.0
    error_count: int = 0

@dataclass
class Alert:
    """Alert message"""
    level: str  # 'info', 'warning', 'error', 'critical'
    message: str
    timestamp: datetime
    account: Optional[str] = None
    details: Optional[Dict] = None

class BotMonitor:
    """Monitors bot performance and generates alerts"""
    
    def __init__(self):
        self.metrics = PostingMetrics()
        self.account_metrics = {}
        self.alerts = deque(maxlen=1000)  # Keep last 1000 alerts
        self.response_times = deque(maxlen=100)
        self.error_counts = defaultdict(int)
        self.ban_risk_factors = {
            'high_frequency': 0.3,
            'repetitive_content': 0.2,
            'rapid_posting': 0.25,
            'api_errors': 0.15,
            'suspicious_patterns': 0.1
        }
        
    def record_post_attempt(self, account: str, success: bool, response_time: float = None):
        """Record a posting attempt"""
        # Update global metrics
        self.metrics.total_posts += 1
        if success:
            self.metrics.successful_posts += 1
        else:
            self.metrics.failed_posts += 1
        
        self.metrics.success_rate = self.metrics.successful_posts / self.metrics.total_posts
        self.metrics.last_post_time = datetime.now()
        
        # Update account metrics
        if account not in self.account_metrics:
            self.account_metrics[account] = AccountMetrics(username=account)
        
        account_metrics = self.account_metrics[account]
        account_metrics.posts_count += 1
        account_metrics.last_post_time = datetime.now()
        
        if success:
            account_metrics.success_rate = (account_metrics.success_rate * (account_metrics.posts_count - 1) + 1) / account_metrics.posts_count
        else:
            account_metrics.success_rate = (account_metrics.success_rate * (account_metrics.posts_count - 1)) / account_metrics.posts_count
            account_metrics.error_count += 1
        
        # Record response time
        if response_time:
            self.response_times.append(response_time)
            self.metrics.average_response_time = statistics.mean(self.response_times)
        
        # Check for alerts
        self._check_alerts(account, success)
    
    def record_error(self, account: str, error_type: str, error_message: str):
        """Record an error"""
        self.error_counts[error_type] += 1
        
        if account in self.account_metrics:
            self.account_metrics[account].error_count += 1
        
        # Create error alert
        alert = Alert(
            level='error',
            message=f"Error for {account}: {error_message}",
            timestamp=datetime.now(),
            account=account,
            details={'error_type': error_type, 'error_message': error_message}
        )
        self.alerts.append(alert)
        
        logger.error(f"❌ Error recorded: {error_message} for {account}")
    
    def set_account_cooldown(self, account: str, cooldown_until: datetime):
        """Set account cooldown"""
        if account in self.account_metrics:
            self.account_metrics[account].cooldown_until = cooldown_until
    
    def calculate_ban_risk(self, account: str) -> float:
        """Calculate ban risk score for an account"""
        if account not in self.account_metrics:
            return 0.0
        
        metrics = self.account_metrics[account]
        risk_score = 0.0
        
        # Factor 1: High frequency posting
        if metrics.posts_count > 10:
            posts_per_day = metrics.posts_count / max(1, (datetime.now() - metrics.last_post_time).days)
            if posts_per_day > 8:
                risk_score += self.ban_risk_factors['high_frequency']
        
        # Factor 2: Error rate
        if metrics.posts_count > 0:
            error_rate = metrics.error_count / metrics.posts_count
            if error_rate > 0.3:
                risk_score += self.ban_risk_factors['api_errors']
        
        # Factor 3: Success rate
        if metrics.success_rate < 0.5:
            risk_score += self.ban_risk_factors['suspicious_patterns']
        
        # Factor 4: Recent activity
        if metrics.last_post_time:
            time_since_last = datetime.now() - metrics.last_post_time
            if time_since_last.total_seconds() < 300:  # Less than 5 minutes
                risk_score += self.ban_risk_factors['rapid_posting']
        
        metrics.ban_risk_score = min(risk_score, 1.0)
        return metrics.ban_risk_score
    
    def _check_alerts(self, account: str, success: bool):
        """Check for conditions that require alerts"""
        # Check success rate
        if self.metrics.total_posts > 10:
            if self.metrics.success_rate < 0.5:
                alert = Alert(
                    level='warning',
                    message=f"Low success rate: {self.metrics.success_rate:.2%}",
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
        
        # Check account-specific issues
        if account in self.account_metrics:
            metrics = self.account_metrics[account]
            
            # High error rate
            if metrics.posts_count > 5 and metrics.error_count / metrics.posts_count > 0.5:
                alert = Alert(
                    level='warning',
                    message=f"High error rate for {account}: {metrics.error_count}/{metrics.posts_count}",
                    timestamp=datetime.now(),
                    account=account
                )
                self.alerts.append(alert)
            
            # Ban risk
            risk_score = self.calculate_ban_risk(account)
            if risk_score > 0.7:
                alert = Alert(
                    level='critical',
                    message=f"High ban risk for {account}: {risk_score:.2%}",
                    timestamp=datetime.now(),
                    account=account,
                    details={'risk_score': risk_score}
                )
                self.alerts.append(alert)
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard"""
        return {
            'metrics': asdict(self.metrics),
            'accounts': {username: asdict(metrics) for username, metrics in self.account_metrics.items()},
            'recent_alerts': [asdict(alert) for alert in list(self.alerts)[-10:]],
            'error_summary': dict(self.error_counts),
            'ban_risk_accounts': [
                username for username, metrics in self.account_metrics.items()
                if metrics.ban_risk_score > 0.5
            ]
        }
    
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        now = datetime.now()
        
        # Calculate daily/weekly stats
        posts_today = sum(1 for metrics in self.account_metrics.values()
                         if metrics.last_post_time and 
                         (now - metrics.last_post_time).days == 0)
        
        posts_this_week = sum(1 for metrics in self.account_metrics.values()
                             if metrics.last_post_time and 
                             (now - metrics.last_post_time).days <= 7)
        
        return {
            'total_posts': self.metrics.total_posts,
            'success_rate': self.metrics.success_rate,
            'average_response_time': self.metrics.average_response_time,
            'posts_today': posts_today,
            'posts_this_week': posts_this_week,
            'active_accounts': len([m for m in self.account_metrics.values() 
                                  if m.last_post_time and 
                                  (now - m.last_post_time).total_seconds() < 86400]),
            'accounts_with_high_risk': len([m for m in self.account_metrics.values() 
                                          if m.ban_risk_score > 0.5]),
            'recent_errors': sum(self.error_counts.values())
        }
    
    def export_metrics(self, filename: str = None):
        """Export metrics to JSON file"""
        if not filename:
            filename = f"bot_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(self.metrics),
            'account_metrics': {username: asdict(metrics) for username, metrics in self.account_metrics.items()},
            'alerts': [asdict(alert) for alert in self.alerts],
            'error_counts': dict(self.error_counts)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"📊 Metrics exported to {filename}")

class AnalyticsDashboard:
    """Simple analytics dashboard"""
    
    def __init__(self, monitor: BotMonitor):
        self.monitor = monitor
    
    def print_dashboard(self):
        """Print current dashboard"""
        print("\n" + "="*60)
        print("🤖 THREADS BOT DASHBOARD")
        print("="*60)
        
        # Overall metrics
        metrics = self.monitor.metrics
        print(f"📊 Total Posts: {metrics.total_posts}")
        print(f"✅ Success Rate: {metrics.success_rate:.2%}")
        print(f"⏱️ Avg Response Time: {metrics.average_response_time:.2f}s")
        print(f"🕐 Last Post: {metrics.last_post_time.strftime('%Y-%m-%d %H:%M:%S') if metrics.last_post_time else 'Never'}")
        
        # Account summary
        print(f"\n👥 Active Accounts: {len(self.monitor.account_metrics)}")
        for username, account_metrics in self.monitor.account_metrics.items():
            risk_score = self.monitor.calculate_ban_risk(username)
            status = "🟢" if risk_score < 0.3 else "🟡" if risk_score < 0.7 else "🔴"
            print(f"  {status} {username}: {account_metrics.posts_count} posts, {account_metrics.success_rate:.2%} success, {risk_score:.1%} risk")
        
        # Recent alerts
        recent_alerts = list(self.monitor.alerts)[-5:]
        if recent_alerts:
            print(f"\n🚨 Recent Alerts ({len(recent_alerts)}):")
            for alert in recent_alerts:
                level_icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}.get(alert.level, "ℹ️")
                print(f"  {level_icon} {alert.message}")
        
        print("="*60 + "\n")

def main():
    """Test the monitoring system"""
    monitor = BotMonitor()
    dashboard = AnalyticsDashboard(monitor)
    
    # Simulate some activity
    monitor.record_post_attempt("user1", True, 2.5)
    monitor.record_post_attempt("user1", True, 3.1)
    monitor.record_post_attempt("user2", False, 1.8)
    monitor.record_error("user2", "api_error", "Rate limit exceeded")
    
    dashboard.print_dashboard()
    
    # Export metrics
    monitor.export_metrics()

if __name__ == "__main__":
    main() 