// LinkedIn Content Bank Scripts

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Confirm before marking content as posted
    const markPostedButtons = document.querySelectorAll('.mark-as-posted');
    markPostedButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to mark this content as posted? This will remove it from your feed.')) {
                e.preventDefault();
            }
        });
    });

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function () {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }

    // Handle datetime-local inputs for older browsers
    const scheduledInputs = document.querySelectorAll('input[type="datetime-local"]');
    scheduledInputs.forEach(input => {
        // Check if the browser supports datetime-local
        const testInput = document.createElement('input');
        testInput.type = 'datetime-local';
        const supportsDatetimeLocal = testInput.type === 'datetime-local';

        if (!supportsDatetimeLocal) {
            // Fallback for browsers that don't support datetime-local
            input.type = 'text';
            input.placeholder = 'YYYY-MM-DD HH:MM';
        }
    });

    // Add animation to content cards
    const contentCards = document.querySelectorAll('.content-card');
    contentCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.15)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}); 