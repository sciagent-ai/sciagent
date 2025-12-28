// Create continuous sparkles in the background
function createSparkle() {
    const sparkle = document.createElement('div');
    sparkle.className = 'sparkle';
    sparkle.style.left = Math.random() * window.innerWidth + 'px';
    sparkle.style.top = Math.random() * window.innerHeight + 'px';
    document.body.appendChild(sparkle);
    
    setTimeout(() => {
        sparkle.remove();
    }, 2000);
}

// Create sparkles continuously
setInterval(createSparkle, 300);

// Celebrate function - creates fireworks
function celebrate() {
    const fireworksContainer = document.getElementById('fireworks');
    const colors = ['#FF6B00', '#FFD700', '#FF1493', '#00CED1', '#FF4500', '#FFA500'];
    
    // Create multiple firework bursts
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createFirework(fireworksContainer, colors);
        }, i * 200);
    }
    
    // Play celebration sound (visual feedback)
    const btn = document.querySelector('.celebrate-btn');
    btn.textContent = '🎉 Celebrating! 🎉';
    setTimeout(() => {
        btn.textContent = '🎆 Celebrate! 🎆';
    }, 2000);
}

function createFirework(container, colors) {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * (window.innerHeight * 0.6);
    const color = colors[Math.floor(Math.random() * colors.length)];
    
    // Create multiple particles for each firework
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'firework';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.background = color;
        particle.style.boxShadow = `0 0 10px ${color}`;
        
        // Random direction for each particle
        const angle = (Math.PI * 2 * i) / 30;
        const velocity = 50 + Math.random() * 100;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        container.appendChild(particle);
        
        setTimeout(() => {
            particle.remove();
        }, 1000);
    }
}

// Auto-celebrate on page load
window.addEventListener('load', () => {
    setTimeout(() => {
        celebrate();
    }, 500);
});

// Add floating animation to diyas
document.addEventListener('DOMContentLoaded', () => {
    const diyas = document.querySelectorAll('.diya');
    diyas.forEach((diya, index) => {
        diya.style.animation = `float 3s ease-in-out ${index * 0.5}s infinite`;
    });
});

// Add float animation dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);

// Add interactive hover effect to rangoli
const rangoli = document.querySelector('.rangoli-pattern');
if (rangoli) {
    rangoli.addEventListener('mouseenter', () => {
        rangoli.style.animationDuration = '2s';
    });
    
    rangoli.addEventListener('mouseleave', () => {
        rangoli.style.animationDuration = '10s';
    });
}

// Create random fireworks every few seconds
setInterval(() => {
    const fireworksContainer = document.getElementById('fireworks');
    const colors = ['#FF6B00', '#FFD700', '#FF1493', '#00CED1', '#FF4500', '#FFA500'];
    createFirework(fireworksContainer, colors);
}, 5000);

console.log('🪔 Happy Diwali! May your life be filled with light and joy! 🪔');
