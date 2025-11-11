# 🔍 Diagnostic Guide for Extension & Monitoring Issues

## 🧪 Quick Diagnostics

### **1. Check Backend API**
```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "feature_extractor_ready": true,
#   "timestamp": "...",
#   "model_info": {...}
# }
```

### **2. Check Dashboard Server**
```bash
# Test dashboard status
curl http://localhost:3000/api/system-status

# Expected response:
# {
#   "api_status": "healthy",
#   "db_status": "healthy",
#   "model_status": "healthy",
#   "email_status": "healthy",
#   "timestamp": "..."
# }
```

### **3. Check Monitoring Endpoints**
```bash
# Get monitoring status
curl http://localhost:3000/api/monitoring/status

# Get recent events
curl http://localhost:3000/api/monitoring/events

# Get live events
curl http://localhost:3000/api/monitoring/live

# Get threat summary
curl http://localhost:3000/api/monitoring/summary
```

---

## 🐛 Common Issues & Solutions

### **Issue 1: Extension Not Analyzing URLs**

**Symptoms:**
- Extension installed but no console messages
- No events appearing in dashboard
- Badge not updating

**Diagnosis:**
1. Open `chrome://extensions/`
2. Find "Phishing Detection Shield"
3. Click "Details"
4. Check if all permissions are granted
5. Open DevTools (F12) on any website
6. Check Console tab for errors

**Solutions:**
- Reload extension: Click reload icon in `chrome://extensions/`
- Check if API is running: `curl http://localhost:8000/health`
- Verify extension can reach API (check CORS errors in console)
- Try visiting a suspicious URL to trigger analysis

### **Issue 2: Dashboard Not Receiving Events**

**Symptoms:**
- Dashboard loads but shows no events
- "Real-time Monitoring" section is empty
- No data in charts

**Diagnosis:**
1. Check if extension is sending events:
   - Open DevTools (F12) on any website
   - Look for: `📊 Event sent to dashboard`
2. Check if dashboard API is receiving events:
   - Look for POST requests to `/api/extension/event`
3. Check browser console for errors

**Solutions:**
- Verify dashboard server is running: `http://localhost:3000`
- Check for CORS errors in browser console
- Verify `/api/extension/event` endpoint is working
- Try refreshing dashboard page

### **Issue 3: Real-Time Monitoring Not Working**

**Symptoms:**
- Monitoring section shows "unavailable"
- No browsing events captured
- "Start Monitoring" button doesn't work

**Diagnosis:**
1. Check if browser_monitor.py is running
2. Verify database file exists: `browsing_monitor.db`
3. Check dashboard server logs for errors
4. Test monitoring endpoints directly

**Solutions:**
- Start monitoring: `python browser_monitor.py`
- Check database permissions
- Verify browser history access is allowed
- Restart dashboard server

---

## 📊 Browser Console Messages

### **Expected Messages (Good)**
```
✅ Safe: google.com
🛡️ Phishing Detection Shield: Skipping trusted domain localhost
📊 Event sent to dashboard: example.com ✅ Safe
```

### **Error Messages (Bad)**
```
❌ Error analyzing URL: ...
⚠️ Dashboard not available, event stored locally only
Failed to fetch: ...
CORS error: ...
```

---

## 🔧 Manual Testing

### **Test 1: Direct API Call**
```bash
# Test URL prediction
curl -X POST http://localhost:8000/predict/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'

# Expected: Phishing detection result
```

### **Test 2: Extension Event Submission**
```bash
# Simulate extension sending event
curl -X POST http://localhost:3000/api/extension/event \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-01T00:00:00Z",
    "url": "https://www.google.com",
    "domain": "google.com",
    "is_phishing": false,
    "confidence": 0.95,
    "threat_level": "Low",
    "risk_factors": [],
    "browser": "extension",
    "processing_time": 100
  }'

# Expected: {"status": "success", "message": "Event received"}
```

---

## 📝 Logs to Check

### **Dashboard Server Logs**
- Check terminal running dashboard_server.py
- Look for error messages
- Check for API connection errors

### **Backend API Logs**
- Check terminal running real_api.py
- Look for prediction errors
- Check for model loading issues

### **Browser Console Logs**
- Press F12 on any website
- Go to Console tab
- Look for extension messages and errors

---

## ✅ Verification Checklist

- [ ] Backend API running on port 8000
- [ ] Dashboard running on port 3000
- [ ] Extension installed and enabled
- [ ] Extension can reach API (no CORS errors)
- [ ] Dashboard receiving extension events
- [ ] Real-time monitoring working
- [ ] Charts updating with data
- [ ] No console errors

**If all items are checked, everything is working!** 🎉

