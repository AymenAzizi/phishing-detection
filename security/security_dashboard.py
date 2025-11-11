#!/usr/bin/env python3
"""
Security Monitoring Dashboard
Real-time security monitoring and alerting system
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uvicorn

# Import security modules
from security.api_security import APISecurityMonitor
from security.ml_security import MLModelSecurity
from security.compliance_checker import ComplianceChecker

class SecurityDashboard:
    """Real-time security monitoring dashboard"""
    
    def __init__(self):
        self.app = FastAPI(title="Security Monitoring Dashboard")
        self.connections = []
        self.security_monitor = APISecurityMonitor()
        self.ml_security = MLModelSecurity()
        self.compliance_checker = ComplianceChecker()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup dashboard routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self.get_dashboard_html()
        
        @self.app.get("/api/security/status")
        async def get_security_status():
            return await self.get_security_status()
        
        @self.app.get("/api/security/events")
        async def get_security_events(limit: int = 100):
            return await self.get_security_events(limit)
        
        @self.app.get("/api/security/metrics")
        async def get_security_metrics():
            return await self.get_security_metrics()
        
        @self.app.get("/api/compliance/status")
        async def get_compliance_status():
            return await self.get_compliance_status()
        
        @self.app.websocket("/ws/security")
        async def websocket_endpoint(websocket: WebSocket):
            await self.websocket_handler(websocket)
    
    async def websocket_handler(self, websocket: WebSocket):
        """Handle WebSocket connections for real-time updates"""
        await websocket.accept()
        self.connections.append(websocket)
        
        try:
            while True:
                # Send real-time security updates
                security_data = await self.get_realtime_security_data()
                await websocket.send_text(json.dumps(security_data))
                await asyncio.sleep(5)  # Update every 5 seconds
        except WebSocketDisconnect:
            self.connections.remove(websocket)
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        try:
            # Get security summary
            security_summary = self.security_monitor.get_security_summary()
            
            # Get ML security status
            ml_security_report = self.ml_security.generate_security_report()
            
            # Get compliance status
            compliance_results = self.compliance_checker.check_all_frameworks()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "security_score": security_summary.get('security_score', 0),
                "threat_level": self.calculate_threat_level(security_summary),
                "active_threats": security_summary.get('recent_events', 0),
                "ml_security": {
                    "model_loaded": ml_security_report.get('model_loaded', False),
                    "security_metrics": ml_security_report.get('security_metrics', {})
                },
                "compliance": {
                    "soc2": compliance_results['frameworks'].get('SOC2', {}).get('compliance_percentage', 0),
                    "iso27001": compliance_results['frameworks'].get('ISO27001', {}).get('compliance_percentage', 0),
                    "gdpr": compliance_results['frameworks'].get('GDPR', {}).get('compliance_percentage', 0)
                },
                "recommendations": self.generate_security_recommendations(security_summary)
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def get_security_events(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent security events"""
        try:
            events = self.security_monitor.security_events[-limit:]
            
            # Categorize events
            event_categories = {}
            for event in events:
                event_type = event.get('event_type', 'unknown')
                if event_type not in event_categories:
                    event_categories[event_type] = 0
                event_categories[event_type] += 1
            
            return {
                "events": events,
                "total_events": len(self.security_monitor.security_events),
                "event_categories": event_categories,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and KPIs"""
        try:
            security_summary = self.security_monitor.get_security_summary()
            
            # Calculate metrics
            total_events = len(self.security_monitor.security_events)
            recent_events = len([e for e in self.security_monitor.security_events 
                               if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=1)])
            
            # Threat distribution
            threat_distribution = {}
            for event in self.security_monitor.security_events[-100:]:
                event_type = event.get('event_type', 'unknown')
                threat_distribution[event_type] = threat_distribution.get(event_type, 0) + 1
            
            return {
                "total_events": total_events,
                "recent_events": recent_events,
                "security_score": security_summary.get('security_score', 0),
                "threat_distribution": threat_distribution,
                "top_threats": security_summary.get('top_threats', []),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        try:
            compliance_results = self.compliance_checker.check_all_frameworks()
            
            # Calculate overall compliance
            frameworks = compliance_results['frameworks']
            overall_compliance = sum(f['compliance_percentage'] for f in frameworks.values()) / len(frameworks)
            
            return {
                "overall_compliance": overall_compliance,
                "frameworks": frameworks,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_realtime_security_data(self) -> Dict[str, Any]:
        """Get real-time security data for WebSocket"""
        try:
            security_summary = self.security_monitor.get_security_summary()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "security_score": security_summary.get('security_score', 0),
                "recent_events": security_summary.get('recent_events', 0),
                "threat_level": self.calculate_threat_level(security_summary),
                "active_connections": len(self.connections)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_threat_level(self, security_summary: Dict[str, Any]) -> str:
        """Calculate current threat level"""
        try:
            security_score = security_summary.get('security_score', 100)
            recent_events = security_summary.get('recent_events', 0)
            
            if security_score < 50 or recent_events > 50:
                return "critical"
            elif security_score < 75 or recent_events > 20:
                return "high"
            elif security_score < 90 or recent_events > 10:
                return "medium"
            else:
                return "low"
        except:
            return "unknown"
    
    def generate_security_recommendations(self, security_summary: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        try:
            security_score = security_summary.get('security_score', 100)
            recent_events = security_summary.get('recent_events', 0)
            
            if security_score < 80:
                recommendations.append("Review and strengthen security controls")
            
            if recent_events > 20:
                recommendations.append("Investigate high number of security events")
            
            if not security_summary.get('ml_security', {}).get('model_loaded', False):
                recommendations.append("Ensure ML model security monitoring is active")
            
            if not recommendations:
                recommendations.append("Security posture is good - continue monitoring")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def get_dashboard_html(self) -> str:
        """Get dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Monitoring Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                .card { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1rem; }
                .metric-card { text-align: center; border-left: 4px solid #3b82f6; }
                .metric-value { font-size: 2rem; font-weight: bold; color: #1f2937; }
                .metric-label { color: #6b7280; font-size: 0.875rem; }
                .status-healthy { color: #10b981; }
                .status-warning { color: #f59e0b; }
                .status-critical { color: #ef4444; }
            </style>
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <!-- Header -->
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900">🔒 Security Monitoring Dashboard</h1>
                    <p class="text-gray-600">Real-time security monitoring and threat detection</p>
                </div>

                <!-- Security Status -->
                <div class="card">
                    <h2 class="text-xl font-semibold mb-4">Security Status</h2>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div class="text-center">
                            <div id="overall-status" class="status-healthy text-lg font-semibold">●</div>
                            <div class="text-sm text-gray-600">Overall Status</div>
                        </div>
                        <div class="text-center">
                            <div id="threat-level" class="status-healthy text-lg font-semibold">●</div>
                            <div class="text-sm text-gray-600">Threat Level</div>
                        </div>
                        <div class="text-center">
                            <div id="security-score" class="status-healthy text-lg font-semibold">●</div>
                            <div class="text-sm text-gray-600">Security Score</div>
                        </div>
                        <div class="text-center">
                            <div id="active-threats" class="status-healthy text-lg font-semibold">●</div>
                            <div class="text-sm text-gray-600">Active Threats</div>
                        </div>
                    </div>
                </div>

                <!-- Key Metrics -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div class="card metric-card">
                        <div id="total-events" class="metric-value">0</div>
                        <div class="metric-label">Total Security Events</div>
                    </div>
                    <div class="card metric-card">
                        <div id="recent-events" class="metric-value">0</div>
                        <div class="metric-label">Recent Events (1h)</div>
                    </div>
                    <div class="card metric-card">
                        <div id="compliance-score" class="metric-value">0%</div>
                        <div class="metric-label">Compliance Score</div>
                    </div>
                    <div class="card metric-card">
                        <div id="ml-security" class="metric-value">0%</div>
                        <div class="metric-label">ML Security</div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <!-- Security Events Over Time -->
                    <div class="card">
                        <h3 class="text-lg font-semibold mb-4">Security Events Over Time</h3>
                        <canvas id="eventsChart" width="400" height="200"></canvas>
                    </div>

                    <!-- Threat Distribution -->
                    <div class="card">
                        <h3 class="text-lg font-semibold mb-4">Threat Distribution</h3>
                        <canvas id="threatChart" width="400" height="200"></canvas>
                    </div>
                </div>

                <!-- Recent Security Events -->
                <div class="card">
                    <h3 class="text-lg font-semibold mb-4">Recent Security Events</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full table-auto">
                            <thead>
                                <tr class="bg-gray-50">
                                    <th class="px-4 py-2 text-left">Timestamp</th>
                                    <th class="px-4 py-2 text-left">Event Type</th>
                                    <th class="px-4 py-2 text-left">Severity</th>
                                    <th class="px-4 py-2 text-left">Details</th>
                                </tr>
                            </thead>
                            <tbody id="security-events">
                                <!-- Dynamic content -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Compliance Status -->
                <div class="card">
                    <h3 class="text-lg font-semibold mb-4">Compliance Status</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-blue-800 mb-2">SOC2</h4>
                            <div id="soc2-compliance" class="text-sm text-blue-700">Loading...</div>
                        </div>
                        <div class="bg-green-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-green-800 mb-2">ISO27001</h4>
                            <div id="iso27001-compliance" class="text-sm text-green-700">Loading...</div>
                        </div>
                        <div class="bg-purple-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-purple-800 mb-2">GDPR</h4>
                            <div id="gdpr-compliance" class="text-sm text-purple-700">Loading...</div>
                        </div>
                    </div>
                </div>

                <!-- Security Recommendations -->
                <div class="card">
                    <h3 class="text-lg font-semibold mb-4">Security Recommendations</h3>
                    <div id="security-recommendations" class="space-y-2">
                        <div class="text-center text-gray-500">Loading recommendations...</div>
                    </div>
                </div>
            </div>

            <script>
                // WebSocket connection for real-time updates
                const ws = new WebSocket('ws://localhost:8001/ws/security');
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };

                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    loadSecurityStatus();
                    loadSecurityEvents();
                    loadSecurityMetrics();
                    loadComplianceStatus();
                    initializeCharts();
                    
                    // Update every 30 seconds
                    setInterval(loadSecurityStatus, 30000);
                    setInterval(loadSecurityEvents, 30000);
                    setInterval(loadSecurityMetrics, 30000);
                });

                async function loadSecurityStatus() {
                    try {
                        const response = await fetch('/api/security/status');
                        const data = await response.json();
                        updateSecurityStatus(data);
                    } catch (error) {
                        console.error('Failed to load security status:', error);
                    }
                }

                async function loadSecurityEvents() {
                    try {
                        const response = await fetch('/api/security/events?limit=20');
                        const data = await response.json();
                        updateSecurityEvents(data.events);
                    } catch (error) {
                        console.error('Failed to load security events:', error);
                    }
                }

                async function loadSecurityMetrics() {
                    try {
                        const response = await fetch('/api/security/metrics');
                        const data = await response.json();
                        updateSecurityMetrics(data);
                    } catch (error) {
                        console.error('Failed to load security metrics:', error);
                    }
                }

                async function loadComplianceStatus() {
                    try {
                        const response = await fetch('/api/compliance/status');
                        const data = await response.json();
                        updateComplianceStatus(data);
                    } catch (error) {
                        console.error('Failed to load compliance status:', error);
                    }
                }

                function updateSecurityStatus(data) {
                    document.getElementById('overall-status').textContent = data.overall_status === 'healthy' ? '●' : '●';
                    document.getElementById('overall-status').className = data.overall_status === 'healthy' ? 'status-healthy text-lg font-semibold' : 'status-critical text-lg font-semibold';
                    
                    document.getElementById('threat-level').textContent = data.threat_level;
                    document.getElementById('threat-level').className = getThreatLevelClass(data.threat_level);
                    
                    document.getElementById('security-score').textContent = data.security_score + '%';
                    document.getElementById('security-score').className = getScoreClass(data.security_score);
                    
                    document.getElementById('active-threats').textContent = data.active_threats;
                    document.getElementById('active-threats').className = data.active_threats > 10 ? 'status-critical text-lg font-semibold' : 'status-healthy text-lg font-semibold';
                }

                function updateSecurityEvents(events) {
                    const tbody = document.getElementById('security-events');
                    tbody.innerHTML = '';
                    
                    events.forEach(event => {
                        const row = document.createElement('tr');
                        row.className = 'border-t';
                        
                        const time = new Date(event.timestamp).toLocaleTimeString();
                        const eventType = event.event_type || 'unknown';
                        const severity = getEventSeverity(eventType);
                        
                        row.innerHTML = `
                            <td class="px-4 py-2">${time}</td>
                            <td class="px-4 py-2">${eventType}</td>
                            <td class="px-4 py-2">
                                <span class="px-2 py-1 rounded text-xs ${getSeverityClass(severity)}">
                                    ${severity}
                                </span>
                            </td>
                            <td class="px-4 py-2">${JSON.stringify(event.details || {})}</td>
                        `;
                        
                        tbody.appendChild(row);
                    });
                }

                function updateSecurityMetrics(data) {
                    document.getElementById('total-events').textContent = data.total_events || 0;
                    document.getElementById('recent-events').textContent = data.recent_events || 0;
                }

                function updateComplianceStatus(data) {
                    document.getElementById('soc2-compliance').textContent = `${data.frameworks.SOC2?.compliance_percentage || 0}%`;
                    document.getElementById('iso27001-compliance').textContent = `${data.frameworks.ISO27001?.compliance_percentage || 0}%`;
                    document.getElementById('gdpr-compliance').textContent = `${data.frameworks.GDPR?.compliance_percentage || 0}%`;
                    document.getElementById('compliance-score').textContent = `${Math.round(data.overall_compliance || 0)}%`;
                }

                function updateDashboard(data) {
                    if (data.error) {
                        console.error('Dashboard update error:', data.error);
                        return;
                    }
                    
                    // Update real-time metrics
                    document.getElementById('security-score').textContent = data.security_score + '%';
                    document.getElementById('active-threats').textContent = data.recent_events;
                }

                function getThreatLevelClass(level) {
                    switch(level) {
                        case 'critical': return 'status-critical text-lg font-semibold';
                        case 'high': return 'status-warning text-lg font-semibold';
                        case 'medium': return 'status-warning text-lg font-semibold';
                        case 'low': return 'status-healthy text-lg font-semibold';
                        default: return 'status-warning text-lg font-semibold';
                    }
                }

                function getScoreClass(score) {
                    if (score >= 90) return 'status-healthy text-lg font-semibold';
                    if (score >= 70) return 'status-warning text-lg font-semibold';
                    return 'status-critical text-lg font-semibold';
                }

                function getEventSeverity(eventType) {
                    const severityMap = {
                        'sql_injection': 'critical',
                        'xss': 'critical',
                        'rate_limit_exceeded': 'medium',
                        'authentication_failed': 'high',
                        'invalid_input': 'medium'
                    };
                    return severityMap[eventType] || 'low';
                }

                function getSeverityClass(severity) {
                    switch(severity) {
                        case 'critical': return 'bg-red-100 text-red-800';
                        case 'high': return 'bg-orange-100 text-orange-800';
                        case 'medium': return 'bg-yellow-100 text-yellow-800';
                        case 'low': return 'bg-green-100 text-green-800';
                        default: return 'bg-gray-100 text-gray-800';
                    }
                }

                function initializeCharts() {
                    // Initialize charts (simplified for demo)
                    console.log('Charts initialized');
                }
            </script>
        </body>
        </html>
        """

# Create dashboard instance
dashboard = SecurityDashboard()
app = dashboard.app

if __name__ == "__main__":
    print("🔒 Starting Security Monitoring Dashboard...")
    print("📊 Dashboard available at: http://localhost:8001")
    print("🔗 Real-time monitoring enabled")
    print("⚡ WebSocket connection for live updates")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
