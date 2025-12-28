// Fireworks animation
function createFirework(x, y) {
    const fireworksContainer = document.getElementById('fireworks');
    const colors = ['#ff6600', '#ff9900', '#ffd700', '#ff3300', '#ffcc00'];
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'firework';
        
        const angle = (Math.PI * 2 * i) / particleCount;
        const velocity = 100 + Math.random() * 100;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        fireworksContainer.appendChild(particle);
        
        setTimeout(() => {
            particle.remove();
        }, 1000);
    }
}

// Random fireworks
function randomFireworks() {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight * 0.7;
    createFirework(x, y);
}

// Start random fireworks
setInterval(randomFireworks, 2000);

// Celebrate button function
function celebrateDiwali() {
    // Create multiple fireworks
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight * 0.7;
            createFirework(x, y);
        }, i * 200);
    }
    
    // Play celebration sound (visual feedback)
    const btn = document.querySelector('.celebrate-btn');
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        btn.style.transform = 'scale(1)';
    }, 100);
    
    // Show celebration message
    showCelebrationMessage();
}

// Show celebration message
function showCelebrationMessage() {
    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 102, 0, 0.95);
        color: white;
        padding: 30px 50px;
        border-radius: 20px;
        font-size: 2rem;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
        animation: popIn 0.5s ease-out;
    `;
    message.textContent = '🎊 Happy Diwali! 🎊';
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.style.animation = 'fadeOut 0.5s ease-out';
        setTimeout(() => {
            message.remove();
        }, 500);
    }, 2000);
}

// Add CSS animations for message
const style = document.createElement('style');
style.textContent = `
    @keyframes popIn {
        0% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.5);
        }
        100% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
    }
    
    @keyframes fadeOut {
        0% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        100% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
        }
    }
`;
document.head.appendChild(style);

// Add click effect to diyas
document.querySelectorAll('.diya-lamp').forEach(diya => {
    diya.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        createFirework(x, y);
    });
});

// Initial firework on load
window.addEventListener('load', () => {
    setTimeout(() => {
        createFirework(window.innerWidth / 2, window.innerHeight / 3);
    }, 500);
});

// Add sparkle effect on mouse move
document.addEventListener('mousemove', (e) => {
    if (Math.random() > 0.95) {
        const sparkle = document.createElement('div');
        sparkle.textContent = '✨';
        sparkle.style.cssText = `
            position: fixed;
            left: ${e.clientX}px;
            top: ${e.clientY}px;
            pointer-events: none;
            font-size: 1rem;
            animation: sparkleFloat 1s ease-out forwards;
            z-index: 1000;
        `;
        document.body.appendChild(sparkle);
        
        setTimeout(() => {
            sparkle.remove();
        }, 1000);
    }
});

// Add sparkle float animation
const sparkleStyle = document.createElement('style');
sparkleStyle.textContent = `
    @keyframes sparkleFloat {
        0% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        100% {
            opacity: 0;
            transform: translateY(-50px) scale(0.5);
        }
    }
`;
document.head.appendChild(sparkleStyle);

console.log('🪔 Happy Diwali! May your code be bug-free and your life be filled with joy! 🪔');
