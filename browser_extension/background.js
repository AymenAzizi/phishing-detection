// Background script for Phishing Detection Shield
const API_BASE = 'http://localhost:8000';
const DASHBOARD_API = 'http://localhost:3000/api';

// Track analyzed URLs to avoid duplicates
const analyzedUrls = new Set();
let isEnabled = true;

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Phishing Detection Shield installed');
  
  // Set default settings - be less aggressive by default
  chrome.storage.sync.set({
    enabled: true,
    showNotifications: true,
    blockPhishing: false,  // Don't block by default, just warn
    apiEndpoint: API_BASE
  });
});

// Listen for tab updates (navigation) - be more selective
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && isEnabled) {
    // Only analyze potentially suspicious URLs
    if (isPotentiallySuspiciousUrl(tab.url)) {
      await analyzeUrl(tab.url, tabId);
    }
  }
});

// Remove web navigation listener to reduce interference
// chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
//   if (details.frameId === 0 && isEnabled) { // Main frame only
//     await analyzeUrl(details.url, details.tabId);
//   }
// });

function isPotentiallySuspiciousUrl(url) {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();

    // Skip only the most trusted major domains to reduce false positives
    const trustedDomains = [
      'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
      'linkedin.com', 'github.com', 'stackoverflow.com', 'wikipedia.org',
      'amazon.com', 'microsoft.com', 'apple.com', 'netflix.com', 'spotify.com',
      'reddit.com', 'twitch.tv', 'discord.com', 'localhost', '127.0.0.1'
    ];

    const isTrusted = trustedDomains.some(domain =>
      hostname === domain || hostname.endsWith('.' + domain)
    );

    if (isTrusted) return false;

    // Use AI analysis for MANY more potentially suspicious patterns

    // 1. Suspicious TLDs (expanded list)
    const suspiciousTlds = [
      '.tk', '.ml', '.ga', '.cf', '.pw', '.top', '.click', '.download',
      '.stream', '.science', '.racing', '.review', '.faith', '.accountant',
      '.loan', '.win', '.bid', '.trade', '.date', '.party', '.cricket'
    ];
    if (suspiciousTlds.some(tld => hostname.endsWith(tld))) {
      return true;
    }

    // 2. IP addresses (always suspicious for web browsing)
    if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      return true;
    }

    // 3. Suspicious keywords in domain
    const suspiciousKeywords = [
      'phishing', 'scam', 'fake', 'verify', 'secure', 'account', 'login',
      'update', 'suspended', 'urgent', 'confirm', 'validation', 'security',
      'banking', 'paypal', 'amazon', 'microsoft', 'apple', 'google',
      'facebook', 'instagram', 'twitter', 'linkedin', 'ebay', 'netflix'
    ];
    if (suspiciousKeywords.some(keyword => hostname.includes(keyword))) {
      return true;
    }

    // 4. Suspicious patterns
    const suspiciousPatterns = [
      /-verify/i, /-secure/i, /-login/i, /-account/i, /-update/i,
      /verify-/i, /secure-/i, /login-/i, /account-/i, /update-/i,
      /\d{4,}/,  // Long numbers in domain
      /@/,       // @ symbol in URL
      /[0-9]+[a-z]+[0-9]+/i  // Mixed numbers and letters
    ];
    if (suspiciousPatterns.some(pattern => pattern.test(hostname))) {
      return true;
    }

    // 5. Short domains (often used for phishing)
    if (hostname.length < 6 && !hostname.includes('.')) {
      return true;
    }

    // 6. Domains with many subdomains (suspicious structure)
    const parts = hostname.split('.');
    if (parts.length > 4) {
      return true;
    }

    // 7. Homograph attacks (similar looking characters)
    const homographPatterns = [
      /[а-я]/,  // Cyrillic characters
      /[αβγδε]/,  // Greek characters
      /[0-9]{2,}[a-z]/i  // Numbers mixed with letters
    ];
    if (homographPatterns.some(pattern => pattern.test(hostname))) {
      return true;
    }

    // 8. URL shorteners (always analyze)
    const shorteners = [
      'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd',
      'buff.ly', 'adf.ly', 'short.link', 'tiny.cc', 'rebrand.ly'
    ];
    if (shorteners.some(shortener => hostname.includes(shortener))) {
      return true;
    }

    // 9. Suspicious paths
    const suspiciousPaths = [
      '/login', '/verify', '/secure', '/account', '/update', '/confirm',
      '/banking', '/payment', '/billing', '/signin', '/signup'
    ];
    if (suspiciousPaths.some(path => urlObj.pathname.toLowerCase().includes(path))) {
      return true;
    }

    // 10. New or uncommon TLDs that might be suspicious
    const uncommonTlds = [
      '.buzz', '.guru', '.ninja', '.today', '.technology', '.email',
      '.website', '.online', '.site', '.space', '.world', '.live'
    ];
    if (uncommonTlds.some(tld => hostname.endsWith(tld))) {
      return true;
    }

    return false;
  } catch (error) {
    return false;
  }
}

// Analyze URL for phishing
async function analyzeUrl(url, tabId) {
  try {
    // Skip non-web URLs and already analyzed URLs
    if (!url.startsWith('http') || analyzedUrls.has(url)) {
      return;
    }
    
    // Skip localhost and common safe domains
    const skipDomains = ['localhost', '127.0.0.1', 'chrome://', 'about:', 'moz-extension:', 'chrome-extension:'];
    if (skipDomains.some(domain => url.includes(domain))) {
      return;
    }
    
    analyzedUrls.add(url);
    
    // Call phishing detection API
    const response = await fetch(`${API_BASE}/predict/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: url })
    });
    
    if (response.ok) {
      const result = await response.json();
      
      // Handle phishing detection
      if (result.is_phishing) {
        await handlePhishingDetection(url, result, tabId);
      } else {
        await handleSafeUrl(url, result, tabId);
      }
      
      // Update badge
      updateBadge(tabId, result.is_phishing);
      
      // Send to dashboard for real-time monitoring
      await sendToDashboard(url, result);
      
    } else {
      console.error('API request failed:', response.status);
    }
    
  } catch (error) {
    console.error('Error analyzing URL:', error);
  }
}

// Handle phishing detection
async function handlePhishingDetection(url, result, tabId) {
  const settings = await chrome.storage.sync.get(['showNotifications', 'blockPhishing']);
  
  // Show notification
  if (settings.showNotifications) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: '🚨 Phishing Threat Detected!',
      message: `Dangerous site blocked: ${new URL(url).hostname}\nConfidence: ${(result.confidence * 100).toFixed(1)}%`
    });
  }
  
  // Block the page only for high-confidence phishing with critical threat level
  if (settings.blockPhishing && result.threat_level === 'critical' && result.confidence > 0.8) {
    try {
      // Check if tab still exists before trying to update it
      const tab = await chrome.tabs.get(tabId).catch(() => null);
      if (tab) {
        await chrome.tabs.update(tabId, {
          url: chrome.runtime.getURL('warning.html') + '?blocked=' + encodeURIComponent(url)
        });
      }
    } catch (error) {
      console.error('Failed to block page:', error);
    }
  }
  
  // Update extension icon
  chrome.action.setIcon({
    tabId: tabId,
    path: {
      16: 'icons/warning16.png',
      32: 'icons/warning32.png',
      48: 'icons/warning48.png',
      128: 'icons/warning128.png'
    }
  });
}

// Handle safe URL
async function handleSafeUrl(url, result, tabId) {
  // Reset extension icon
  chrome.action.setIcon({
    tabId: tabId,
    path: {
      16: 'icons/icon16.png',
      32: 'icons/icon32.png',
      48: 'icons/icon48.png',
      128: 'icons/icon128.png'
    }
  });
}

// Update badge
function updateBadge(tabId, isPhishing) {
  try {
    if (isPhishing) {
      chrome.action.setBadgeText({
        tabId: tabId,
        text: '⚠️'
      }).catch(() => {});
      chrome.action.setBadgeBackgroundColor({
        tabId: tabId,
        color: '#ff0000'
      }).catch(() => {});
    } else {
      chrome.action.setBadgeText({
        tabId: tabId,
        text: '✓'
      }).catch(() => {});
      chrome.action.setBadgeBackgroundColor({
        tabId: tabId,
        color: '#00ff00'
      }).catch(() => {});
    }

    // Clear badge after 3 seconds
    setTimeout(() => {
      chrome.action.setBadgeText({
        tabId: tabId,
        text: ''
      }).catch(() => {});
    }, 3000);
  } catch (error) {
    // Ignore badge errors
  }
}

// Send data to dashboard
async function sendToDashboard(url, result) {
  try {
    const event = {
      timestamp: new Date().toISOString(),
      url: url,
      domain: new URL(url).hostname,
      is_phishing: result.is_phishing,
      confidence: result.confidence,
      threat_level: result.threat_level,
      risk_factors: result.risk_factors || [],
      browser: 'extension',
      processing_time: result.processing_time_ms || 0
    };

    // Store locally for extension popup
    const events = await chrome.storage.local.get(['browsingEvents']) || { browsingEvents: [] };
    events.browsingEvents = events.browsingEvents || [];
    events.browsingEvents.unshift(event);

    // Keep only last 100 events
    if (events.browsingEvents.length > 100) {
      events.browsingEvents = events.browsingEvents.slice(0, 100);
    }

    await chrome.storage.local.set(events);

    // Send to dashboard API for real-time updates
    try {
      await fetch('http://localhost:3000/api/extension/event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(event)
      });
      console.log('📊 Event sent to dashboard:', event.domain, result.is_phishing ? '🚨 Phishing' : '✅ Safe');
    } catch (dashboardError) {
      console.log('⚠️ Dashboard not available, event stored locally only');
    }

  } catch (error) {
    console.error('Failed to send to dashboard:', error);
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getStatus') {
    sendResponse({
      enabled: isEnabled,
      analyzedCount: analyzedUrls.size
    });
  } else if (request.action === 'toggleEnabled') {
    isEnabled = !isEnabled;
    chrome.storage.sync.set({ enabled: isEnabled });
    sendResponse({ enabled: isEnabled });
  } else if (request.action === 'getEvents') {
    chrome.storage.local.get(['browsingEvents']).then(data => {
      sendResponse({ events: data.browsingEvents || [] });
    });
    return true; // Async response
  }
});

// Clean up old analyzed URLs periodically
setInterval(() => {
  if (analyzedUrls.size > 1000) {
    analyzedUrls.clear();
  }
}, 300000); // Every 5 minutes
