/**
 * Main JavaScript file for the Chess Game with AI web application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle difficulty selection
    const difficultyButtons = document.querySelectorAll('.difficulty-btn');
    if (difficultyButtons.length > 0) {
        difficultyButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                difficultyButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Update hidden input value
                const difficultyInput = document.getElementById('difficulty');
                if (difficultyInput) {
                    difficultyInput.value = this.dataset.difficulty;
                }
            });
        });
    }

    // Handle game history filtering
    const filterSelect = document.getElementById('history-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const filter = this.value;
            const historyItems = document.querySelectorAll('.game-history-item');
            
            historyItems.forEach(item => {
                if (filter === 'all' || item.dataset.result === filter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}); 