#!/usr/bin/env python3
"""
Real-time Browser Monitoring System
Tracks browsing activity and provides live phishing alerts
"""

import asyncio
import json
import time
import requests
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import threading
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BrowsingEvent:
    """Represents a browsing event"""
    timestamp: str
    url: str
    domain: str
    is_phishing: bool
    confidence: float
    threat_level: str
    risk_factors: List[str]
    browser: str
    processing_time: float

class BrowserHistoryMonitor:
    """Monitors browser history for new URLs"""
    
    def __init__(self):
        self.last_check = datetime.now()
        self.processed_urls = set()
        
    def get_chrome_history(self) -> List[str]:
        """Extract recent URLs from Chrome history"""
        try:
            import sqlite3
            import os
            import shutil
            from pathlib import Path
            
            # Chrome history database path
            chrome_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/History"
            
            if not chrome_path.exists():
                return []
            
            # Create a temporary copy (Chrome locks the database)
            temp_path = Path.home() / "AppData/Local/Temp/Chrome_History_Temp"
            shutil.copy2(chrome_path, temp_path)
            
            urls = []
            try:
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                
                # Get URLs from last 24 hours
                query = "SELECT url FROM urls WHERE last_visit_time > ? ORDER BY last_visit_time DESC LIMIT 100"
                # Chrome stores time as microseconds since 1601-01-01
                cutoff_time = (datetime.now() - timedelta(days=1)).timestamp() * 1000000 + 11644473600000000
                
                cursor.execute(query, (cutoff_time,))
                urls = [row[0] for row in cursor.fetchall()]
                conn.close()
            finally:
                if temp_path.exists():
                    os.remove(temp_path)
            
            return urls
        except Exception as e:
            logger.debug(f"Chrome history access error: {e}")
            return []
    
    def get_firefox_history(self) -> List[str]:
        """Extract recent URLs from Firefox history"""
        try:
            import sqlite3
            import os
            import shutil
            from pathlib import Path
            
            # Firefox history database path
            firefox_profile = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
            
            if not firefox_profile.exists():
                return []
            
            urls = []
            
            # Find the default profile
            for profile_dir in firefox_profile.iterdir():
                if profile_dir.is_dir():
                    places_db = profile_dir / "places.sqlite"
                    if places_db.exists():
                        temp_path = Path.home() / "AppData/Local/Temp/Firefox_History_Temp"
                        shutil.copy2(places_db, temp_path)
                        
                        try:
                            conn = sqlite3.connect(temp_path)
                            cursor = conn.cursor()
                            
                            # Get URLs from last 24 hours
                            query = """
                                SELECT url FROM moz_places 
                                WHERE last_visit_date > ? 
                                ORDER BY last_visit_date DESC 
                                LIMIT 100
                            """
                            cutoff_time = (datetime.now() - timedelta(days=1)).timestamp() * 1000000
                            
                            cursor.execute(query, (cutoff_time,))
                            urls.extend([row[0] for row in cursor.fetchall()])
                            conn.close()
                        finally:
                            if temp_path.exists():
                                os.remove(temp_path)
                        break
            
            return urls
        except Exception as e:
            logger.debug(f"Firefox history access error: {e}")
            return []
    
    def get_new_urls(self) -> List[str]:
        """Get new URLs from all browsers"""
        new_urls = []
        
        # Check Chrome
        new_urls.extend(self.get_chrome_history())
        
        # Check Firefox
        new_urls.extend(self.get_firefox_history())
        
        # Update last check time
        self.last_check = datetime.now()
        
        # Filter out common non-web URLs
        filtered_urls = []
        for url in new_urls:
            if url.startswith(('http://', 'https://')) and not any(skip in url.lower() for skip in [
                'localhost', '127.0.0.1', 'chrome://', 'about:', 'moz-extension:', 'chrome-extension:'
            ]):
                filtered_urls.append(url)
                self.processed_urls.add(url)
        
        return filtered_urls

class PhishingAnalyzer:
    """Analyzes URLs using the ML API"""
    
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
    
    async def analyze_url(self, url: str) -> Optional[Dict]:
        """Analyze URL using ML API"""
        try:
            response = requests.post(
                f"{self.api_base}/predict/url",
                json={"url": url},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API error for {url}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {e}")
            return None

class RealTimeMonitor:
    """Main real-time monitoring system"""
    
    def __init__(self):
        self.browser_monitor = BrowserHistoryMonitor()
        self.analyzer = PhishingAnalyzer()
        self.event_queue = queue.Queue()
        self.running = False
        self.db_path = "browsing_monitor.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS browsing_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    is_phishing BOOLEAN NOT NULL,
                    confidence REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    risk_factors TEXT NOT NULL,
                    browser TEXT NOT NULL,
                    processing_time REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def store_event(self, event: BrowsingEvent):
        """Store event in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO browsing_events 
                (timestamp, url, domain, is_phishing, confidence, threat_level, risk_factors, browser, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp,
                event.url,
                event.domain,
                event.is_phishing,
                event.confidence,
                event.threat_level,
                json.dumps(event.risk_factors),
                event.browser,
                event.processing_time
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing event: {e}")
    
    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get recent events from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT * FROM browsing_events 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''', (cutoff_time,))
            
            columns = [description[0] for description in cursor.description]
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return events
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            return []
    
    def get_threat_summary(self) -> Dict:
        """Get threat summary statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()

            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_phishing THEN 1 ELSE 0 END) as phishing,
                       AVG(processing_time) as avg_time
                FROM browsing_events
                WHERE timestamp > ?
            ''', (cutoff_time,))

            result = cursor.fetchone()
            conn.close()

            total = result[0] or 0
            phishing = result[1] or 0
            avg_time = result[2] or 0

            return {
                "total_visits": total,
                "phishing_blocked": phishing,
                "legitimate_visits": total - phishing,
                "avg_processing_time": round(avg_time, 2),
                "protection_rate": round((phishing / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            logger.error(f"Error getting threat summary: {e}")
            return {
                "total_visits": 0,
                "phishing_blocked": 0,
                "legitimate_visits": 0,
                "avg_processing_time": 0,
                "protection_rate": 0
            }

    def clear_events(self):
        """Clear all browsing events from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM browsing_events')
            conn.commit()
            conn.close()
            logger.info("Browsing events cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing events: {e}")
            return False
    
    async def process_url(self, url: str):
        """Process a single URL"""
        try:
            domain = urlparse(url).netloc
            analysis = await self.analyzer.analyze_url(url)
            
            if analysis:
                event = BrowsingEvent(
                    timestamp=datetime.now().isoformat(),
                    url=url,
                    domain=domain,
                    is_phishing=analysis.get('is_phishing', False),
                    confidence=analysis.get('confidence', 0.0),
                    threat_level=analysis.get('threat_level', 'unknown'),
                    risk_factors=analysis.get('risk_factors', []),
                    browser='auto-detected',
                    processing_time=analysis.get('processing_time', 0.0)
                )
                
                self.store_event(event)
                self.event_queue.put(asdict(event))
                
                if event.is_phishing:
                    logger.warning(f"🚨 PHISHING DETECTED: {url} (Confidence: {event.confidence:.2f})")
                else:
                    logger.info(f"✅ Safe site: {domain}")
                    
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting real-time browser monitoring...")
        
        while self.running:
            try:
                new_urls = self.browser_monitor.get_new_urls()
                
                for url in new_urls:
                    await self.process_url(url)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        
        def run_monitor():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.monitor_loop())
        
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()
        
        logger.info("🚀 Real-time browser monitoring started!")
        
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        logger.info("🛑 Real-time browser monitoring stopped!")
        
    def get_live_events(self) -> List[Dict]:
        """Get live events from queue and recent database events"""
        events = []

        # Get events from queue first (most recent)
        while not self.event_queue.empty():
            try:
                events.append(self.event_queue.get_nowait())
            except queue.Empty:
                break

        # If queue is empty, get recent events from database
        if not events:
            events = self.get_recent_events(hours=1)

        # Return only the most recent 10 events
        return events[:10]

# Global monitor instance
monitor = RealTimeMonitor()

if __name__ == "__main__":
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
            
            events = monitor.get_live_events()
            for event in events:
                if event['is_phishing']:
                    print(f"🚨 THREAT DETECTED: {event['url']} (Confidence: {event['confidence']:.2f})")
                else:
                    print(f"✅ Safe: {event['domain']}")
                    
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n🛑 Monitoring stopped by user")

