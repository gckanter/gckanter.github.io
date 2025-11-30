/**
 * CAROUSEL FUNCTIONALITY
 * Auto-cycles through images with manual controls
 * Pauses on hover for better UX
 */

document.addEventListener('DOMContentLoaded', () => {
    const track = document.getElementById('carousel-track');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const carousel = document.getElementById('carousel');
    
    if (!track || !prevButton || !nextButton) {
        console.error('[Carousel] Required elements not found');
        return;
    }

    const items = Array.from(track.children);
    const itemCount = items.length;
    let currentIndex = 0;
    let autoplayInterval = null;
    const AUTOPLAY_DELAY = 5000; // 5 seconds between slides

    // Function to update carousel position
    function updateCarousel(animate = true) {
        const offset = -currentIndex * 100;
        track.style.transition = animate ? 'transform 0.6s ease-in-out' : 'none';
        track.style.transform = `translateX(${offset}%)`;
        console.log(`[Carousel] Moved to slide ${currentIndex + 1} of ${itemCount}`);
    }

    // Move to next slide
    function nextSlide() {
        currentIndex = (currentIndex + 1) % itemCount;
        updateCarousel();
    }

    // Move to previous slide
    function prevSlide() {
        currentIndex = (currentIndex - 1 + itemCount) % itemCount;
        updateCarousel();
    }

    // Start autoplay
    function startAutoplay() {
        if (autoplayInterval) return; // Already running
        autoplayInterval = setInterval(nextSlide, AUTOPLAY_DELAY);
        console.log('[Carousel] Autoplay started');
    }

    // Stop autoplay
    function stopAutoplay() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
            autoplayInterval = null;
            console.log('[Carousel] Autoplay stopped');
        }
    }

    // Event listeners for manual controls
    nextButton.addEventListener('click', () => {
        stopAutoplay();
        nextSlide();
        startAutoplay(); // Restart autoplay after manual interaction
    });

    prevButton.addEventListener('click', () => {
        stopAutoplay();
        prevSlide();
        startAutoplay(); // Restart autoplay after manual interaction
    });

    // Pause on hover, resume on mouse leave
    carousel.addEventListener('mouseenter', () => {
        stopAutoplay();
    });

    carousel.addEventListener('mouseleave', () => {
        startAutoplay();
    });

    // Keyboard navigation (accessibility)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            stopAutoplay();
            prevSlide();
            startAutoplay();
        } else if (e.key === 'ArrowRight') {
            stopAutoplay();
            nextSlide();
            startAutoplay();
        }
    });

    // Touch/swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        stopAutoplay();
    });

    carousel.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
        startAutoplay();
    });

    function handleSwipe() {
        const swipeThreshold = 50; // Minimum distance for a swipe
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swiped left, go to next
                nextSlide();
            } else {
                // Swiped right, go to previous
                prevSlide();
            }
        }
    }

    // Initialize carousel
    updateCarousel(false);
    startAutoplay();

    console.log(`[Carousel] Initialized with ${itemCount} slides`);
});