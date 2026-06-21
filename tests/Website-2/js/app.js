// Handle broken images
function handleBrokenImages() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            console.warn(`Broken image detected: ${this.src}`);
            this.style.display = 'none';
            // Optionally, replace with a placeholder
            // this.src = 'images/placeholder.jpg';
        });
    });
}

// Log all broken images for testing
function logBrokenImages() {
    const brokenImages = [
        'images/missing1.jpg',
        'images/missing2.png',
        'images/404-image.png',
        'images/assets/broken.jpg',
        'images/images/fake.webp',
        'images/notfound.svg',
        'images/bad-icon.ico',
        'images/team-old.jpg',
        'images/gallery999.png',
        'images/header-image.png'
    ];
    console.log('=== BROKEN IMAGES (GROUND TRUTH) ===');
    brokenImages.forEach(src => console.log(src));
}

// Log all working images for testing
function logWorkingImages() {
    const workingImages = [
        'images/logo.png',
        'images/hero.jpg',
        'images/team.jpg',
        'images/gallery1.jpg',
        'images/gallery2.jpg',
        'images/gallery3.jpg'
    ];
    console.log('=== WORKING IMAGES (GROUND TRUTH) ===');
    workingImages.forEach(src => console.log(src));
}

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    handleBrokenImages();
    logBrokenImages();
    logWorkingImages();
    console.log('=== IMAGE SCANNER TEST WEBSITE READY ===');
});

// Optional: Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});