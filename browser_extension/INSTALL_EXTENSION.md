# 🛡️ Browser Extension Installation Guide

## 🚀 **QUICK INSTALLATION STEPS**

### **For Chrome/Edge/Brave:**

1. **Open Extension Management**
   - Chrome: Go to `chrome://extensions/`
   - Edge: Go to `edge://extensions/`
   - Brave: Go to `brave://extensions/`

2. **Enable Developer Mode**
   - Toggle "Developer mode" switch in the top right corner

3. **Load the Extension**
   - Click "Load unpacked" button
   - Navigate to and select this folder: `Downloads/phishing dectection aymen/browser_extension`
   - Click "Select Folder"

4. **Verify Installation**
   - You should see "Phishing Detection Shield" in your extensions list
   - A shield icon 🛡️ should appear in your browser toolbar

---

## ✅ **EXTENSION FEATURES**

### **🔍 Real-time Protection**
- **Automatic URL Analysis**: Every site you visit is checked
- **Instant Threat Detection**: Phishing sites are identified immediately
- **Desktop Notifications**: Alerts for dangerous sites
- **Visual Indicators**: Protection status in toolbar

### **📊 Protection Statistics**
- **Sites Scanned**: Total number of URLs analyzed
- **Threats Blocked**: Number of phishing attempts stopped
- **Protection Rate**: Percentage of threats detected
- **Recent Activity**: Last 5 browsing events

### **🎯 Smart Blocking**
- **Phishing Site Blocking**: Dangerous sites are blocked automatically
- **Form Protection**: Warnings for suspicious login forms
- **Link Safety**: Alerts for dangerous links before clicking
- **Safe Site Confirmation**: Green indicators for legitimate sites

---

## 🧪 **TESTING THE EXTENSION**

### **Test Safe Sites:**
1. Visit `https://www.google.com`
   - ✅ Should show green checkmark
   - ✅ No alerts or warnings
   - ✅ Extension popup shows "Safe Sites: 1"

2. Visit `https://github.com`
   - ✅ Should show green checkmark
   - ✅ Extension tracks legitimate visits

### **Test Phishing Detection:**
1. Visit suspicious URL: `http://192.168.1.1@bit.ly/phishing`
   - 🚨 Should trigger phishing alert
   - 🚨 Desktop notification appears
   - 🚨 Extension popup shows "Threats Blocked: 1"

2. Check extension popup:
   - Click the shield icon in toolbar
   - View protection statistics
   - See recent activity log

---

## 🔧 **EXTENSION CONTROLS**

### **Popup Interface:**
- **Protection Status**: Active/Inactive indicator
- **Toggle Protection**: Enable/disable button
- **Statistics**: Safe sites vs threats blocked
- **Recent Activity**: Last 5 browsing events
- **Dashboard Link**: One-click access to full dashboard
- **Settings**: Configuration options

### **Available Actions:**
- **Enable/Disable**: Toggle real-time protection
- **View Dashboard**: Open monitoring dashboard
- **Check Statistics**: View protection metrics
- **Recent Events**: See browsing history analysis

---

## ⚙️ **CONFIGURATION**

### **Default Settings (Non-Intrusive):**
- **Protection**: Enabled by default
- **Notifications**: Desktop alerts enabled
- **Blocking**: DISABLED by default (warnings only)
- **Form/Link Monitoring**: DISABLED by default
- **API Endpoint**: `http://localhost:8000`

### **Customization Options:**
- **Notification Preferences**: Enable/disable alerts
- **Blocking Behavior**: Warn vs block dangerous sites
- **API Configuration**: Change endpoint if needed
- **Whitelist Management**: Add trusted domains

---

## 🔗 **INTEGRATION WITH DASHBOARD**

### **Real-time Sync:**
- **Live Updates**: Browsing activity appears in dashboard
- **Statistics Sync**: Extension data feeds dashboard metrics
- **Alert Correlation**: Notifications match dashboard alerts
- **Performance Tracking**: Response times and accuracy

### **Dashboard Access:**
- **One-click Access**: Button in extension popup
- **URL**: http://localhost:3000
- **Live Monitoring**: Real-time browsing protection section
- **Historical Data**: Complete browsing analysis

---

## 🛠️ **TROUBLESHOOTING**

### **Extension Not Working:**
1. **Check Installation**:
   - Verify extension appears in `chrome://extensions/`
   - Ensure "Enabled" toggle is on
   - Refresh the extensions page

2. **Check API Connection**:
   - Verify ML API is running: http://localhost:8000/health
   - Test API manually: Use dashboard URL testing
   - Check browser console for errors

3. **Permissions Issues**:
   - Ensure extension has required permissions
   - Check if popup shows "Protection Active"
   - Verify no browser security restrictions

### **No Notifications:**
1. **Browser Settings**:
   - Check if notifications are allowed for the extension
   - Verify system notification settings
   - Test with a known phishing URL

2. **Extension Settings**:
   - Check if notifications are enabled in popup
   - Verify protection is active
   - Test with sample phishing URLs

### **Performance Issues:**
1. **API Response**:
   - Check if API responds quickly: http://localhost:8000/health
   - Monitor dashboard for response times
   - Verify no network connectivity issues

2. **Browser Performance**:
   - Check if extension is consuming too much memory
   - Disable and re-enable if needed
   - Clear browser cache if necessary

---

## 📊 **EXPECTED BEHAVIOR**

### **Normal Browsing:**
- **Safe Sites**: Green checkmark, no alerts
- **Response Time**: < 3 seconds per URL
- **Memory Usage**: Minimal impact on browser
- **Background Operation**: Silent protection

### **Threat Detection:**
- **Phishing Sites**: Red warning, desktop notification
- **Suspicious Links**: Click protection warnings
- **Form Protection**: Alerts for sensitive data entry
- **Blocking**: Critical threats blocked automatically

### **Statistics Tracking:**
- **Accurate Counting**: Correct site and threat counts
- **Real-time Updates**: Immediate statistics refresh
- **Historical Data**: Persistent across browser sessions
- **Dashboard Sync**: Data appears in monitoring dashboard

---

## 🎉 **SUCCESS INDICATORS**

### **✅ Extension Working Correctly:**
- Shield icon visible in browser toolbar
- Popup shows "Protection Active" status
- Safe sites show green indicators
- Phishing sites trigger alerts and notifications
- Statistics update correctly
- Dashboard integration working
- No errors in browser console

### **🚨 Protection Active:**
- Real-time URL analysis happening
- Threat detection working accurately
- Desktop notifications for dangers
- Dashboard showing live browsing events
- Performance metrics within acceptable ranges

---

## 📞 **SUPPORT**

### **Quick Checks:**
- **Extension Status**: Check popup for "Protection Active"
- **API Health**: Visit http://localhost:8000/health
- **Dashboard**: Open http://localhost:3000
- **Console**: Check browser developer tools for errors

### **Common Solutions:**
- **Restart Browser**: Close and reopen browser
- **Reload Extension**: Disable and re-enable in extensions page
- **Clear Cache**: Clear browser cache and cookies
- **Reinstall**: Remove and reinstall extension

**Your browser is now protected with real-time phishing detection!** 🛡️
