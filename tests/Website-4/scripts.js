// ============================================
// NAVBAR TOGGLE
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // ============================================
    // WORKING CONTACT FORM
    // ============================================
    const workingForm = document.getElementById('working-form');
    if (workingForm) {
        workingForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const name = document.getElementById('contact-name').value.trim();
            const email = document.getElementById('contact-email').value.trim();
            const message = document.getElementById('contact-message').value.trim();

            if (!name || !email || !message) {
                return;
            }

            workingForm.classList.add('hidden');
            document.getElementById('working-success').classList.remove('hidden');
        });
    }

    // ============================================
    // JS ERROR FORM
    // ============================================
    const errorForm = document.getElementById('error-form');
    if (errorForm) {
        errorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Intentionally throw an error
            throw new Error('Intentional JavaScript error triggered by form submission');
        });
    }

    // ============================================
    // DELAYED FORM
    // ============================================
    const delayedForm = document.getElementById('delayed-form');
    if (delayedForm) {
        delayedForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const btn = delayedForm.querySelector('button[type="submit"]');
            const btnText = btn.querySelector('.btn-text');
            const btnSpinner = btn.querySelector('.btn-spinner');

            btn.disabled = true;
            btnText.textContent = 'Processing...';
            btnSpinner.classList.remove('hidden');

            setTimeout(function() {
                delayedForm.classList.add('hidden');
                document.getElementById('delayed-success').classList.remove('hidden');

                btn.disabled = false;
                btnText.textContent = 'Request Callback';
                btnSpinner.classList.add('hidden');
            }, 3000);
        });
    }

    // ============================================
    // VALIDATION FORM (Newsletter)
    // ============================================
    const validationForm = document.getElementById('validation-form');
    if (validationForm) {
        validationForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const emailInput = document.getElementById('newsletter-email');
            const emailError = document.getElementById('email-error');
            const email = emailInput.value.trim();

            if (!email) {
                emailError.classList.remove('hidden');
                emailInput.style.borderColor = 'var(--danger)';
                emailInput.focus();
                return;
            }

            emailError.classList.add('hidden');
            emailInput.style.borderColor = '';

            validationForm.classList.add('hidden');
            document.getElementById('validation-success').classList.remove('hidden');
        });
    }

    // ============================================
    // FAKE SUCCESS FORM (Feedback)
    // ============================================
    const fakeForm = document.getElementById('fake-form');
    if (fakeForm) {
        fakeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Shows success but does NOT actually save data
            fakeForm.classList.add('hidden');
            document.getElementById('fake-success').classList.remove('hidden');
            // No data is sent anywhere — this is the "fake" part
        });
    }

    // ============================================
    // BROKEN FORM (Quote) — intentionally no handler
    // The button is type="button" with no click listener
    // ============================================
});

// ============================================
// RESET FORM UTILITY
// ============================================
function resetForm(type) {
    if (type === 'working') {
        document.getElementById('working-success').classList.add('hidden');
        document.getElementById('working-form').classList.remove('hidden');
        document.getElementById('working-form').reset();
    } else if (type === 'delayed') {
        document.getElementById('delayed-success').classList.add('hidden');
        document.getElementById('delayed-form').classList.remove('hidden');
        document.getElementById('delayed-form').reset();
    } else if (type === 'validation') {
        document.getElementById('validation-success').classList.add('hidden');
        document.getElementById('validation-form').classList.remove('hidden');
        document.getElementById('validation-form').reset();
        document.getElementById('email-error').classList.add('hidden');
        document.getElementById('newsletter-email').style.borderColor = '';
    } else if (type === 'fake') {
        document.getElementById('fake-success').classList.add('hidden');
        document.getElementById('fake-form').classList.remove('hidden');
        document.getElementById('fake-form').reset();
    }
}