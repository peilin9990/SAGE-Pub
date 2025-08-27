// SAGE Landing Page JavaScript

// Floating navigation scroll effect
window.addEventListener('scroll', function() {
    const floatingNav = document.getElementById('floatingNav');
    if (window.scrollY > window.innerHeight * 0.3) {
        floatingNav.classList.add('visible');
    } else {
        floatingNav.classList.remove('visible');
    }
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe feature cards and other elements
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.feature-card, .step-card, .section-animate').forEach(el => {
        // Set initial animation state
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
        
        // Check if element is already in viewport
        const rect = el.getBoundingClientRect();
        const isInViewport = rect.top < window.innerHeight && rect.bottom > 0;
        if (isInViewport) {
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
                el.classList.add('visible');
            }, 100);
        }
    });
});

// Add some interactive effects
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-3px) scale(1.02)';
    });
    
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

// Enhanced dynamic background effects
function createStreamingData() {
    const hero = document.querySelector('.hero');
    const dataNodesContainer = document.querySelector('.data-nodes');
    
    // Create additional flowing data particles
    for (let i = 0; i < 20; i++) {
        setTimeout(() => {
            const particle = document.createElement('div');
            particle.className = 'data-node';
            particle.style.cssText = `
                top: ${Math.random() * 100}%;
                left: -10px;
                background: ${['rgba(59, 130, 246, 0.8)', 'rgba(147, 51, 234, 0.8)', 'rgba(16, 185, 129, 0.8)', 'rgba(245, 158, 11, 0.8)'][Math.floor(Math.random() * 4)]};
                animation-duration: ${8 + Math.random() * 4}s;
                animation-delay: ${Math.random() * 2}s;
            `;
            dataNodesContainer.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 12000);
        }, i * 300);
    }
}

// Create starfield
function createStarfield() {
    const starfield = document.querySelector('.starfield');
    
    // Create 150 stars
    for (let i = 0; i < 150; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.cssText = `
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation-delay: ${Math.random() * 3}s;
        `;
        starfield.appendChild(star);
    }
}

// Create floating data labels with boxes
function createDataLabels() {
    const labels = [
        { text: 'RAG', class: '' },
        { text: 'Vector DB', class: 'purple' },
        { text: 'Streaming', class: 'green' },
        { text: 'AI Agent', class: 'orange' },
        { text: 'ML Pipeline', class: '' },
        { text: 'DataFlow', class: 'purple' },
        { text: 'MCP', class: 'green' },
        { text: 'Multi Agent', class: 'orange' },
        { text: 'Online Learning', class: '' },
        { text: 'Streaming Benchmark', class: 'purple' },
        { text: 'Embodied Intelligence', class: 'green' },
        { text: 'Neural Memory', class: 'orange' },
        { text: 'Real-time Analytics', class: '' },
        { text: 'Distributed Computing', class: 'purple' }
    ];
    const hero = document.querySelector('.hero');
    
    labels.forEach((label, index) => {
        setTimeout(() => {
            const labelEl = document.createElement('div');
            labelEl.textContent = label.text;
            labelEl.className = `data-label ${label.class}`;
            labelEl.style.cssText = `
                top: ${20 + Math.random() * 60}%;
                left: -200px;
                animation-delay: ${Math.random() * 3}s;
            `;
            hero.appendChild(labelEl);
            
            setTimeout(() => {
                if (labelEl.parentNode) {
                    labelEl.parentNode.removeChild(labelEl);
                }
            }, 15000);
        }, index * 2000);
    });
}

// Start all animations
createStarfield();
createStreamingData();
setInterval(createStreamingData, 10000);

createDataLabels();
setInterval(createDataLabels, 25000);

// Mouse move parallax effect
document.addEventListener('mousemove', function(e) {
    const hero = document.querySelector('.hero');
    const nodes = document.querySelectorAll('.data-node');
    const stars = document.querySelectorAll('.star');
    const mouseX = e.clientX / window.innerWidth;
    const mouseY = e.clientY / window.innerHeight;
    
    nodes.forEach((node, index) => {
        const speed = (index % 3 + 1) * 0.5;
        const x = (mouseX - 0.5) * speed * 20;
        const y = (mouseY - 0.5) * speed * 20;
        node.style.transform += ` translate(${x}px, ${y}px)`;
    });
    
    // Add subtle parallax to stars
    stars.forEach((star, index) => {
        if (index % 10 === 0) { // Only affect every 10th star for performance
            const speed = 0.1;
            const x = (mouseX - 0.5) * speed * 10;
            const y = (mouseY - 0.5) * speed * 10;
            star.style.transform = `translate(${x}px, ${y}px)`;
        }
    });
});

// Parallax effect for hero section (reduced intensity)
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero && scrolled < window.innerHeight) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Tab switching functionality for Quick Start section
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});

// Video placeholder click handlers
document.addEventListener('DOMContentLoaded', function() {
    const videoPlaceholders = document.querySelectorAll('.video-placeholder');
    
    videoPlaceholders.forEach(placeholder => {
        placeholder.addEventListener('click', function() {
            // Add a simple click effect
            const playButton = this.querySelector('.play-button');
            playButton.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                playButton.style.transform = 'scale(1.1)';
            }, 150);
            
            setTimeout(() => {
                playButton.style.transform = 'scale(1)';
            }, 300);
            
            // You can add actual video loading logic here
            console.log('Video placeholder clicked - implement video loading');
        });
    });
});

// Enhanced hover effects for cards
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to various card elements
    const cards = document.querySelectorAll('.feature-card, .why-card, .example-card, .contribute-card, .opportunity-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });
    
    // Add click effects to contribute links
    const contributeLinks = document.querySelectorAll('.contribute-link');
    contributeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(59, 130, 246, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            this.style.position = 'relative';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Add CSS animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes nodeFloat {
        0%, 100% { transform: translateX(0) translateY(0); }
        25% { transform: translateX(100vw) translateY(-20px); }
        50% { transform: translateX(100vw) translateY(20px); }
        75% { transform: translateX(100vw) translateY(-10px); }
    }
    
    @keyframes labelFlow {
        0% { transform: translateX(0); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateX(calc(100vw + 200px)); opacity: 0; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.8; }
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    
    @keyframes streamFlow {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
`;
document.head.appendChild(style);

// Performance optimization: Throttle scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Apply throttling to scroll events
const throttledScrollHandler = throttle(function() {
    const floatingNav = document.getElementById('floatingNav');
    if (window.scrollY > window.innerHeight * 0.3) {
        floatingNav.classList.add('visible');
    } else {
        floatingNav.classList.remove('visible');
    }
    
    // Parallax effect
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero && scrolled < window.innerHeight) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
}, 16); // ~60fps

// Replace the existing scroll event listener
window.removeEventListener('scroll', arguments.callee);
window.addEventListener('scroll', throttledScrollHandler);

// Add missing playVideo function
function playVideo(videoId) {
    console.log('Playing video:', videoId);
    // Add actual video implementation here
    // For now, just show an alert or console message
    const videoElement = document.querySelector(`[onclick="playVideo('${videoId}')"]`);
    if (videoElement) {
        const overlay = videoElement.querySelector('.video-overlay h4');
        if (overlay) {
            const originalText = overlay.textContent;
            overlay.textContent = '正在加载视频...';
            setTimeout(() => {
                overlay.textContent = originalText;
            }, 2000);
        }
    }
}

// Fix section animation visibility issues
document.addEventListener('DOMContentLoaded', function() {
    // Ensure all section-animate elements are visible initially
    const sectionElements = document.querySelectorAll('.section-animate');
    sectionElements.forEach(el => {
        // Set initial state for better visibility
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
    });
});
