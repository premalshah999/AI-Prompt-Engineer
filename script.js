document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-theme');
    }
    
    themeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-theme');
        
        // Save theme preference
        if (body.classList.contains('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });
    
    // Smooth scrolling for "Try It Now" button
    const tryNowBtn = document.getElementById('try-now-btn');
    tryNowBtn.addEventListener('click', function() {
        document.getElementById('prompt-generator').scrollIntoView({ behavior: 'smooth' });
    });
    
    // Character counter for prompt input
    const promptInput = document.getElementById('prompt-input');
    const charCount = document.getElementById('char-count');
    
    promptInput.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 1000) {
            charCount.style.color = 'var(--danger)';
            this.style.borderColor = 'var(--danger)';
        } else {
            charCount.style.color = '';
            this.style.borderColor = '';
        }
    });
    
    // Testimonial slider
    const testimonialTrack = document.querySelector('.testimonial-track');
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentIndex = 0;
    
    function updateSlider() {
        testimonialTrack.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }
    
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            updateSlider();
        });
    });
    
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + testimonialCards.length) % testimonialCards.length;
        updateSlider();
    });
    
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % testimonialCards.length;
        updateSlider();
    });
    
    // Auto-rotate testimonials
    let testimonialInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % testimonialCards.length;
        updateSlider();
    }, 5000);
    
    // Pause auto-rotation on hover
    testimonialTrack.addEventListener('mouseenter', () => {
        clearInterval(testimonialInterval);
    });
    
    testimonialTrack.addEventListener('mouseleave', () => {
        testimonialInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % testimonialCards.length;
            updateSlider();
        }, 5000);
    });
    
    // Back to top button
    const backToTopButton = document.getElementById('back-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });
    
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Copy result to clipboard
    const copyResultBtn = document.getElementById('copy-result');
    const notification = document.getElementById('notification');
    
    copyResultBtn.addEventListener('click', function() {
        const resultContent = document.getElementById('result-content');
        const textToCopy = resultContent.textContent;
        
        if (textToCopy && !textToCopy.includes('Your enhanced prompt will appear here')) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show notification
                notification.classList.add('show');
                
                // Hide notification after 3 seconds
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            });
        }
    });
    
    // Form submission for prompt enhancement
    const promptForm = document.getElementById('prompt-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultContent = document.getElementById('result-content');
    const responseTimeElement = document.getElementById('response-time');
    const timestampElement = document.getElementById('timestamp');
    
    promptForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const prompt = document.getElementById('prompt-input').value;
        const domain = document.getElementById('domain-select').value;
        const style = document.getElementById('style-select').value;
        const responseLength = document.querySelector('input[name="response-length"]:checked').value;
        
        if (!prompt || !domain || !style) {
            alert('Please fill in all required fields');
            return;
        }
        
        if (prompt.length > 1000) {
            alert('Prompt exceeds 1000 characters');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        resultContent.classList.add('hidden');
        
        const startTime = new Date();
        
        try {
            // Get API key from environment or prompt user
            // In a real application, you would handle this securely
            const apiKey = "3f8a9d5e-2c7b-4e6d-a9c5-d6b8e4c7f1a2"; // Replace with your actual API key or get it from a secure source
            
            const response = await fetch('http://127.0.0.1:8000/enhance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': '3f8a9d5e-2c7b-4e6d-a9c5-d6b8e4c7f1a2' // Replace with your actual API key
                },
                body: JSON.stringify({
                    prompt,
                    domain,
                    style,
                    response_length: responseLength
                })
            });
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Calculate response time
            const endTime = new Date();
            const responseTime = (endTime - startTime) / 1000;
            
            // Update result
            resultContent.innerHTML = `<p>${data.enhanced_prompt.replace(/\n/g, '<br>')}</p>`;
            responseTimeElement.textContent = `${responseTime.toFixed(2)}s`;
            timestampElement.textContent = new Date(data.timestamp).toLocaleString();
            
        } catch (error) {
            console.error('Error:', error);
            resultContent.innerHTML = `<p class="error">Error: ${error.message}. Please try again later.</p>`;
        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            resultContent.classList.remove('hidden');
        }
    });
    
    // Add animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
});