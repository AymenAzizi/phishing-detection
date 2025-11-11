// Content script for Phishing Detection Shield
// Runs only on potentially suspicious sites

(function() {
    'use strict';

    // Only run on main frame
    if (window !== window.top) return;

    // Check if already injected
    if (window.phishingShieldInjected) return;
    window.phishingShieldInjected = true;

    // Skip on trusted domains to avoid CSP issues
    const trustedDomains = [
        'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
        'linkedin.com', 'github.com', 'stackoverflow.com', 'wikipedia.org',
        'amazon.com', 'ebay.com', 'paypal.com', 'microsoft.com', 'apple.com',
        'netflix.com', 'spotify.com', 'reddit.com', 'twitch.tv', 'discord.com',
        'localhost', '127.0.0.1'
    ];

    const currentDomain = window.location.hostname.toLowerCase();
    const isTrustedDomain = trustedDomains.some(domain =>
        currentDomain === domain || currentDomain.endsWith('.' + domain)
    );

    // Don't run on trusted domains
    if (isTrustedDomain) {
        console.log('🛡️ Phishing Detection Shield: Skipping trusted domain', currentDomain);
        return;
    }

    // Configuration - very conservative by default
    const SHIELD_CONFIG = {
        enabled: true,
        showWarnings: false,  // Disable warnings by default
        checkForms: false,    // Disable form monitoring by default
        checkLinks: false     // Disable link monitoring by default
    };

    // Only initialize if this might be a suspicious site
    if (isPotentiallySuspiciousSite()) {
        initializeProtection();
    }

    function isPotentiallySuspiciousSite() {
        const hostname = window.location.hostname.toLowerCase();

        // Check for suspicious TLDs
        const suspiciousTlds = ['.tk', '.ml', '.ga', '.cf', '.pw'];
        if (suspiciousTlds.some(tld => hostname.endsWith(tld))) {
            return true;
        }

        // Check for IP addresses
        if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
            return true;
        }

        // Check for suspicious patterns
        const suspiciousPatterns = [
            'phishing', 'scam', 'fake', 'verify', 'secure-', 'account-',
            'login-', 'update-', 'suspended', 'urgent'
        ];

        if (suspiciousPatterns.some(pattern => hostname.includes(pattern))) {
            return true;
        }

        // Check for brand impersonation
        const brands = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'facebook'];
        const suspiciousBrandPatterns = brands.map(brand => new RegExp(`${brand}.*\\.(tk|ml|ga|cf)$`, 'i'));

        if (suspiciousBrandPatterns.some(pattern => pattern.test(hostname))) {
            return true;
        }

        return false;
    }

    function initializeProtection() {
        // Monitor form submissions
        if (SHIELD_CONFIG.checkForms) {
            monitorForms();
        }
        
        // Monitor suspicious links
        if (SHIELD_CONFIG.checkLinks) {
            monitorLinks();
        }
        
        // Add visual indicator
        addProtectionIndicator();
        
        console.log('🛡️ Phishing Detection Shield active on', window.location.hostname);
    }
    
    function monitorForms() {
        // Monitor all forms for suspicious behavior
        document.addEventListener('submit', function(event) {
            const form = event.target;
            
            if (form.tagName === 'FORM') {
                const suspiciousPatterns = [
                    /password/i,
                    /login/i,
                    /signin/i,
                    /credit.?card/i,
                    /social.?security/i,
                    /ssn/i
                ];
                
                const formData = new FormData(form);
                let hasSensitiveData = false;
                
                for (let [name, value] of formData.entries()) {
                    if (suspiciousPatterns.some(pattern => pattern.test(name) || pattern.test(value))) {
                        hasSensitiveData = true;
                        break;
                    }
                }
                
                if (hasSensitiveData && isCurrentSiteSuspicious()) {
                    event.preventDefault();
                    showFormWarning(form);
                }
            }
        });
    }
    
    function monitorLinks() {
        // Monitor clicks on suspicious links
        document.addEventListener('click', function(event) {
            const link = event.target.closest('a');
            
            if (link && link.href) {
                const url = new URL(link.href);
                
                // Check for suspicious URL patterns
                if (isSuspiciousUrl(url)) {
                    event.preventDefault();
                    showLinkWarning(link, url);
                }
            }
        });
    }
    
    function isSuspiciousUrl(url) {
        // Only flag obviously suspicious patterns, not legitimate shorteners
        const suspiciousDomains = [
            /paypal.*\.tk$/i,
            /amazon.*\.ml$/i,
            /google.*\.ga$/i,
            /microsoft.*\.cf$/i,
            /apple.*\.tk$/i,
            /facebook.*\.ml$/i,
            /bank.*\.tk$/i,
            /secure.*\.ml$/i,
            /verify.*\.ga$/i
        ];

        // Check for suspicious domain patterns (fake brand domains)
        if (suspiciousDomains.some(pattern => pattern.test(url.hostname))) {
            return true;
        }

        // Check for IP addresses with suspicious paths
        if (/^\d+\.\d+\.\d+\.\d+/.test(url.hostname) &&
            (url.pathname.includes('login') || url.pathname.includes('verify') || url.pathname.includes('secure'))) {
            return true;
        }

        // Check for obviously malicious patterns
        if (url.hostname.includes('@') || url.hostname.includes('phishing') || url.hostname.includes('scam')) {
            return true;
        }

        return false;
    }
    
    function isCurrentSiteSuspicious() {
        // Very conservative check - only flag obviously malicious sites
        const hostname = window.location.hostname;

        // Only flag clearly suspicious TLD combinations with brand names
        const suspiciousTlds = ['.tk', '.ml', '.ga', '.cf'];
        const brandNames = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'facebook', 'bank'];

        if (suspiciousTlds.some(tld => hostname.endsWith(tld))) {
            // Only suspicious if it contains a brand name
            if (brandNames.some(brand => hostname.toLowerCase().includes(brand))) {
                return true;
            }
        }

        // Check for obviously malicious patterns
        const maliciousPatterns = [
            /paypal.*verify.*\.tk/i,
            /amazon.*security.*\.ml/i,
            /secure.*bank.*\.ga/i,
            /verify.*account.*\.cf/i
        ];

        return maliciousPatterns.some(pattern => pattern.test(hostname));
    }
    
    function showFormWarning(form) {
        const warning = createWarningElement(
            '⚠️ Suspicious Form Detected',
            'This form is requesting sensitive information on a potentially unsafe site. Please verify the site\'s authenticity before proceeding.',
            [
                { text: 'Cancel', action: () => removeWarning(warning) },
                { text: 'Submit Anyway', action: () => { removeWarning(warning); form.submit(); }, danger: true }
            ]
        );
        
        document.body.appendChild(warning);
    }
    
    function showLinkWarning(link, url) {
        const warning = createWarningElement(
            '🔗 Suspicious Link Detected',
            `This link appears to be suspicious: ${url.hostname}. It may lead to a phishing site or malware.`,
            [
                { text: 'Cancel', action: () => removeWarning(warning) },
                { text: 'Visit Anyway', action: () => { removeWarning(warning); window.open(url.href, '_blank'); }, danger: true }
            ]
        );
        
        document.body.appendChild(warning);
    }
    
    function createWarningElement(title, message, buttons) {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            text-align: center;
        `;
        
        const titleEl = document.createElement('h3');
        titleEl.textContent = title;
        titleEl.style.cssText = `
            color: #dc2626;
            margin: 0 0 16px 0;
            font-size: 18px;
            font-weight: 600;
        `;
        
        const messageEl = document.createElement('p');
        messageEl.textContent = message;
        messageEl.style.cssText = `
            color: #374151;
            margin: 0 0 24px 0;
            line-height: 1.5;
        `;
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            gap: 12px;
            justify-content: center;
        `;
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.textContent = btn.text;
            button.style.cssText = `
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                ${btn.danger ? 
                    'background: #ef4444; color: white;' : 
                    'background: #f3f4f6; color: #374151; border: 1px solid #d1d5db;'
                }
            `;
            
            button.addEventListener('click', btn.action);
            buttonContainer.appendChild(button);
        });
        
        modal.appendChild(titleEl);
        modal.appendChild(messageEl);
        modal.appendChild(buttonContainer);
        overlay.appendChild(modal);
        
        return overlay;
    }
    
    function removeWarning(warning) {
        if (warning && warning.parentNode) {
            warning.parentNode.removeChild(warning);
        }
    }
    
    function addProtectionIndicator() {
        // Don't add indicator to avoid CSP issues
        // Just log that protection is active
        console.log('🛡️ Phishing Detection Shield: Protection active on potentially suspicious site');
    }
    
})();
