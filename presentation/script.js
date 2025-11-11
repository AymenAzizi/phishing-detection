// Universal Phishing Protection Platform - Presentation Script

class PresentationController {
    constructor() {
        this.currentSlide = 1;
        this.totalSlides = 13;
        this.slides = document.querySelectorAll('.slide');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.slideCounter = document.getElementById('slideCounter');
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateSlideDisplay();
        this.addAnimations();
        this.setupKeyboardNavigation();
        this.setupTouchNavigation();
    }

    setupEventListeners() {
        this.prevBtn.addEventListener('click', () => this.previousSlide());
        this.nextBtn.addEventListener('click', () => this.nextSlide());
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowLeft':
                case 'ArrowUp':
                    e.preventDefault();
                    this.previousSlide();
                    break;
                case 'ArrowRight':
                case 'ArrowDown':
                case ' ':
                    e.preventDefault();
                    this.nextSlide();
                    break;
                case 'Home':
                    e.preventDefault();
                    this.goToSlide(1);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToSlide(this.totalSlides);
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
            }
        });
    }

    setupTouchNavigation() {
        let startX = 0;
        let startY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;

            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const diffX = startX - endX;
            const diffY = startY - endY;

            // Check if it's a horizontal swipe
            if (Math.abs(diffX) > Math.abs(diffY)) {
                if (Math.abs(diffX) > 50) { // Minimum swipe distance
                    if (diffX > 0) {
                        this.nextSlide();
                    } else {
                        this.previousSlide();
                    }
                }
            }

            startX = 0;
            startY = 0;
        });
    }

    nextSlide() {
        if (this.currentSlide < this.totalSlides) {
            this.currentSlide++;
            this.updateSlideDisplay();
            this.addSlideAnimation('slide-in-right');
        }
    }

    previousSlide() {
        if (this.currentSlide > 1) {
            this.currentSlide--;
            this.updateSlideDisplay();
            this.addSlideAnimation('slide-in-left');
        }
    }

    goToSlide(slideNumber) {
        if (slideNumber >= 1 && slideNumber <= this.totalSlides) {
            this.currentSlide = slideNumber;
            this.updateSlideDisplay();
            this.addSlideAnimation('fade-in');
        }
    }

    updateSlideDisplay() {
        // Hide all slides
        this.slides.forEach(slide => {
            slide.classList.remove('active');
        });

        // Show current slide
        const currentSlideElement = document.querySelector(`[data-slide="${this.currentSlide}"]`);
        if (currentSlideElement) {
            currentSlideElement.classList.add('active');
        }

        // Update counter
        this.slideCounter.textContent = `${this.currentSlide} / ${this.totalSlides}`;

        // Update button states
        this.prevBtn.disabled = this.currentSlide === 1;
        this.nextBtn.disabled = this.currentSlide === this.totalSlides;

        // Add visual feedback for button states
        if (this.prevBtn.disabled) {
            this.prevBtn.style.opacity = '0.5';
        } else {
            this.prevBtn.style.opacity = '1';
        }

        if (this.nextBtn.disabled) {
            this.nextBtn.style.opacity = '0.5';
        } else {
            this.nextBtn.style.opacity = '1';
        }

        // Scroll to top of slide
        window.scrollTo(0, 0);
    }

    addSlideAnimation(animationClass) {
        const currentSlideElement = document.querySelector(`[data-slide="${this.currentSlide}"]`);
        if (currentSlideElement) {
            currentSlideElement.classList.add(animationClass);
            setTimeout(() => {
                currentSlideElement.classList.remove(animationClass);
            }, 500);
        }
    }

    addAnimations() {
        // Add staggered animations to elements
        this.slides.forEach((slide, index) => {
            const animatedElements = slide.querySelectorAll('.feature-item, .problem-item, .platform-item, .metric-card, .tech-item, .achievement-item');
            
            animatedElements.forEach((element, elementIndex) => {
                element.style.animationDelay = `${elementIndex * 0.1}s`;
                element.classList.add('fade-in');
            });
        });
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log('Error attempting to enable fullscreen:', err);
            });
        } else {
            document.exitFullscreen();
        }
    }

    // Auto-advance slides (optional)
    startAutoAdvance(interval = 30000) {
        this.autoAdvanceInterval = setInterval(() => {
            if (this.currentSlide < this.totalSlides) {
                this.nextSlide();
            } else {
                this.stopAutoAdvance();
            }
        }, interval);
    }

    stopAutoAdvance() {
        if (this.autoAdvanceInterval) {
            clearInterval(this.autoAdvanceInterval);
            this.autoAdvanceInterval = null;
        }
    }

    // Presentation mode controls
    enterPresentationMode() {
        document.body.classList.add('presentation-mode');
        this.startAutoAdvance();
    }

    exitPresentationMode() {
        document.body.classList.remove('presentation-mode');
        this.stopAutoAdvance();
    }
}

// Initialize presentation when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const presentation = new PresentationController();
    
    // Add presentation mode toggle
    const presentationModeBtn = document.createElement('button');
    presentationModeBtn.innerHTML = '<i class="fas fa-play"></i> Presentation Mode';
    presentationModeBtn.className = 'presentation-mode-btn';
    presentationModeBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        z-index: 1000;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    `;
    
    presentationModeBtn.addEventListener('click', () => {
        if (document.body.classList.contains('presentation-mode')) {
            presentation.exitPresentationMode();
            presentationModeBtn.innerHTML = '<i class="fas fa-play"></i> Presentation Mode';
        } else {
            presentation.enterPresentationMode();
            presentationModeBtn.innerHTML = '<i class="fas fa-pause"></i> Exit Mode';
        }
    });
    
    document.body.appendChild(presentationModeBtn);

    // Add slide navigation dots
    const slideDots = document.createElement('div');
    slideDots.className = 'slide-dots';
    slideDots.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 10px;
        z-index: 1000;
    `;

    for (let i = 1; i <= 13; i++) {
        const dot = document.createElement('button');
        dot.className = 'slide-dot';
        dot.dataset.slide = i;
        dot.style.cssText = `
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.5);
            background: transparent;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        dot.addEventListener('click', () => {
            presentation.goToSlide(i);
        });
        
        slideDots.appendChild(dot);
    }
    
    document.body.appendChild(slideDots);

    // Update dots when slide changes
    const updateDots = () => {
        const dots = document.querySelectorAll('.slide-dot');
        dots.forEach((dot, index) => {
            if (index + 1 === presentation.currentSlide) {
                dot.style.background = '#ffd700';
                dot.style.borderColor = '#ffd700';
            } else {
                dot.style.background = 'transparent';
                dot.style.borderColor = 'rgba(255, 255, 255, 0.5)';
            }
        });
    };

    // Override the updateSlideDisplay method to include dot updates
    const originalUpdateSlideDisplay = presentation.updateSlideDisplay.bind(presentation);
    presentation.updateSlideDisplay = function() {
        originalUpdateSlideDisplay();
        updateDots();
    };

    // Add progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        z-index: 1001;
        transition: width 0.3s ease;
    `;
    document.body.appendChild(progressBar);

    // Update progress bar
    const updateProgressBar = () => {
        const progress = (presentation.currentSlide / presentation.totalSlides) * 100;
        progressBar.style.width = `${progress}%`;
    };

    // Override updateSlideDisplay to include progress bar
    const originalUpdateSlideDisplayWithProgress = presentation.updateSlideDisplay.bind(presentation);
    presentation.updateSlideDisplay = function() {
        originalUpdateSlideDisplayWithProgress();
        updateProgressBar();
    };

    // Add slide transition effects
    const addTransitionEffects = () => {
        const style = document.createElement('style');
        style.textContent = `
            .slide {
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .slide.active {
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .presentation-mode .nav-bar {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .presentation-mode .slide-dots {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .presentation-mode .presentation-mode-btn {
                opacity: 0.7;
            }
        `;
        document.head.appendChild(style);
    };

    addTransitionEffects();

    // Add keyboard shortcuts info
    const shortcutsInfo = document.createElement('div');
    shortcutsInfo.className = 'shortcuts-info';
    shortcutsInfo.innerHTML = `
        <div style="position: fixed; top: 50%; right: 20px; transform: translateY(-50%); 
                    background: rgba(0, 0, 0, 0.8); color: white; padding: 15px; 
                    border-radius: 10px; font-size: 12px; z-index: 1000; opacity: 0.7;
                    transition: opacity 0.3s ease;">
            <div style="font-weight: bold; margin-bottom: 8px;">Keyboard Shortcuts:</div>
            <div>← → : Navigate slides</div>
            <div>Home/End : First/Last slide</div>
            <div>Esc : Toggle fullscreen</div>
            <div>Space : Next slide</div>
        </div>
    `;
    document.body.appendChild(shortcutsInfo);

    // Hide shortcuts info in presentation mode
    const originalEnterPresentationMode = presentation.enterPresentationMode.bind(presentation);
    presentation.enterPresentationMode = function() {
        originalEnterPresentationMode();
        shortcutsInfo.style.opacity = '0';
    };

    const originalExitPresentationMode = presentation.exitPresentationMode.bind(presentation);
    presentation.exitPresentationMode = function() {
        originalExitPresentationMode();
        shortcutsInfo.style.opacity = '0.7';
    };

    // Add click-to-advance functionality
    document.addEventListener('click', (e) => {
        if (document.body.classList.contains('presentation-mode') && 
            !e.target.closest('.nav-controls') && 
            !e.target.closest('.slide-dots') &&
            !e.target.closest('.presentation-mode-btn')) {
            presentation.nextSlide();
        }
    });

    // Add mouse wheel navigation
    let wheelTimeout;
    document.addEventListener('wheel', (e) => {
        clearTimeout(wheelTimeout);
        wheelTimeout = setTimeout(() => {
            if (e.deltaY > 0) {
                presentation.nextSlide();
            } else if (e.deltaY < 0) {
                presentation.previousSlide();
            }
        }, 100);
    }, { passive: true });

    // Add slide counter with percentage
    const slidePercentage = document.createElement('div');
    slidePercentage.className = 'slide-percentage';
    slidePercentage.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        z-index: 1000;
    `;
    document.body.appendChild(slidePercentage);

    const updateSlidePercentage = () => {
        const percentage = Math.round((presentation.currentSlide / presentation.totalSlides) * 100);
        slidePercentage.textContent = `${percentage}%`;
    };

    // Override updateSlideDisplay to include percentage
    const originalUpdateSlideDisplayWithPercentage = presentation.updateSlideDisplay.bind(presentation);
    presentation.updateSlideDisplay = function() {
        originalUpdateSlideDisplayWithPercentage();
        updateSlidePercentage();
    };

    // Initialize everything
    updateDots();
    updateProgressBar();
    updateSlidePercentage();

    console.log('🚀 Universal Phishing Protection Platform Presentation Ready!');
    console.log('📊 Use arrow keys, mouse wheel, or touch gestures to navigate');
    console.log('🎯 Click "Presentation Mode" for auto-advance slideshow');
    console.log('⌨️ Press Esc for fullscreen mode');
});

// Add CSS for presentation mode
const presentationStyles = document.createElement('style');
presentationStyles.textContent = `
    .presentation-mode {
        cursor: none;
    }
    
    .presentation-mode .nav-bar,
    .presentation-mode .slide-dots,
    .presentation-mode .shortcuts-info {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .presentation-mode:hover .nav-bar,
    .presentation-mode:hover .slide-dots,
    .presentation-mode:hover .shortcuts-info {
        opacity: 1;
    }
    
    .slide-dot:hover {
        transform: scale(1.2);
        border-color: #ffd700 !important;
    }
    
    .presentation-mode-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
`;
document.head.appendChild(presentationStyles);
