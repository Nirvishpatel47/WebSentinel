/**
 * NEXUS DIGITAL AGENCY
 * Shared JavaScript - QA/Testing Sandbox
 * Includes intentional edge cases for robustness testing
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('%c[NEXUS] Agency site initialized - QA mode active', 'color:#6366f1');

  // ============================================
  // 1. ACTIVE NAV LINK HIGHLIGHT
  // ============================================
  function setActiveNavLink() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      // Handle both relative and absolute style links
      if (href === currentPath || href === './' + currentPath || href.endsWith(currentPath)) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }
  setActiveNavLink();

  // ============================================
  // 2. MOBILE MENU TOGGLE
  // ============================================
  const hamburger = document.getElementById('hamburger');
  const navMenu = document.getElementById('nav-menu');
  
  if (hamburger && navMenu) {
    hamburger.addEventListener('click', function() {
      navMenu.classList.toggle('open');
      // Simple animation for hamburger
      hamburger.classList.toggle('active');
    });
    
    // Close mobile menu when clicking a link
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 900) {
          navMenu.classList.remove('open');
        }
      });
    });
  }

  // ============================================
  // 3. LINK CLICK LOGGER (for all anchors)
  // ============================================
  document.querySelectorAll('a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href') || 'javascript:void(0)';
      const text = this.textContent.trim().substring(0, 60);
      console.log(`[LINK-LOGGER] Clicked: "${text}" → ${href}`);
      
      // Do NOT preventDefault - let broken links 404 naturally for testing
    });
  });

  // ============================================
  // 4. GLOBAL IMAGE ERROR HANDLER + LOGGING
  // ============================================
  function setupImageErrorHandlers() {
    const images = document.querySelectorAll('img');
    let brokenCount = 0;
    
    images.forEach((img, index) => {
      // Log initial src for debugging
      if (!img.hasAttribute('data-logged')) {
        // console.log(`[IMG] Registered: ${img.src} (alt: ${img.alt || 'MISSING ALT'})`);
        img.setAttribute('data-logged', 'true');
      }
      
      img.addEventListener('error', function() {
        brokenCount++;
        console.warn(`[BROKEN-IMAGE #${brokenCount}]`, {
          src: this.src,
          alt: this.alt || 'NO ALT ATTRIBUTE',
          element: this.outerHTML.substring(0, 120) + '...'
        });
        
        // Visual indicator for QA (subtle red border) - does not fix the image
        this.style.border = '3px dashed #ef4444';
        this.style.opacity = '0.6';
        
        // Add a small badge for testing visibility (non-intrusive)
        if (!this.parentElement.querySelector('.img-broken-badge')) {
          const badge = document.createElement('div');
          badge.className = 'img-broken-badge';
          badge.style.cssText = 'position:absolute;top:8px;right:8px;background:#ef4444;color:white;font-size:10px;padding:1px 6px;border-radius:4px;pointer-events:none;';
          badge.textContent = '404';
          
          if (getComputedStyle(this.parentElement).position === 'static') {
            this.parentElement.style.position = 'relative';
          }
          this.parentElement.appendChild(badge);
        }
      });
      
      // Force error event if image already broken (for cached cases)
      if (img.complete && img.naturalWidth === 0) {
        img.dispatchEvent(new Event('error'));
      }
    });
  }
  setupImageErrorHandlers();

  // ============================================
  // 5. FORM HANDLING + FAKE SUBMISSION
  // ============================================
  function setupFormHandlers() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach((form, formIndex) => {
      const formId = form.id || `form-${formIndex}`;
      
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        console.log(`[FORM-SUBMIT] Form #${formIndex} (${formId}) submitted`);
        
        // Collect form data (will fail gracefully on missing name attrs)
        const formData = {};
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
          const key = input.name || input.id || input.placeholder || 'unnamed_field';
          if (input.type === 'checkbox' || input.type === 'radio') {
            formData[key] = input.checked;
          } else {
            formData[key] = input.value;
          }
        });
        
        console.log('[FORM-DATA]', formData);
        
        // Basic client validation simulation
        let hasError = false;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            hasError = true;
            field.style.borderColor = '#ef4444';
            setTimeout(() => {
              if (field) field.style.borderColor = '';
            }, 2200);
          }
        });
        
        // Show fake success or error
        const successMsg = form.querySelector('.success-message');
        
        if (hasError) {
          console.warn('[FORM] Validation errors detected (missing required fields)');
          if (successMsg) {
            successMsg.style.display = 'block';
            successMsg.style.background = 'rgba(239, 68, 68, 0.1)';
            successMsg.style.borderColor = '#ef4444';
            successMsg.style.color = '#ef4444';
            successMsg.innerHTML = '⚠️ Please fill all required fields. (This is a simulated error for testing)';
          }
        } else {
          // Fake success
          if (successMsg) {
            successMsg.style.display = 'block';
            successMsg.style.background = 'rgba(34, 197, 94, 0.1)';
            successMsg.style.borderColor = '#22c55e';
            successMsg.style.color = '#22c55e';
            successMsg.innerHTML = '✅ Thank you! Your message has been received. (Simulated - no backend)';
          }
          
          // Reset form after fake submit
          setTimeout(() => {
            form.reset();
            if (successMsg) successMsg.style.display = 'none';
          }, 2800);
        }
        
        // Log to console for QA
        console.log('%c[FORM] Submission processed (no network request made)', 'color:#64748b');
      });
    });
  }
  setupFormHandlers();

  // ============================================
  // 6. LOGIN MODAL (Client Portal)
  // ============================================
  const loginBtn = document.getElementById('login-btn');
  const loginModal = document.getElementById('login-modal');
  
  if (loginBtn && loginModal) {
    loginBtn.addEventListener('click', function(e) {
      e.preventDefault();
      loginModal.classList.add('active');
      console.log('[MODAL] Login modal opened');
    });
    
    // Close handlers
    const closeBtn = loginModal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => loginModal.classList.remove('active'));
    }
    
    loginModal.addEventListener('click', function(e) {
      if (e.target === loginModal) {
        loginModal.classList.remove('active');
      }
    });
    
    // Login form inside modal
    const loginForm = loginModal.querySelector('form');
    if (loginForm) {
      loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = loginForm.querySelector('#login-email')?.value || 'N/A';
        const pass = loginForm.querySelector('#login-password')?.value || 'N/A';
        
        console.log('[LOGIN] Fake login attempt:', { email, password: '***hidden***' });
        
        const modalSuccess = loginModal.querySelector('.success-message');
        if (modalSuccess) {
          modalSuccess.style.display = 'block';
          modalSuccess.innerHTML = '🔐 Login successful (simulated). Welcome back, QA Tester!';
        }
        
        setTimeout(() => {
          loginModal.classList.remove('active');
          if (modalSuccess) modalSuccess.style.display = 'none';
          loginForm.reset();
        }, 1600);
      });
    }
  }

  // ============================================
  // 7. PORTFOLIO FILTER (Vanilla JS)
  // ============================================
  const filterButtons = document.querySelectorAll('.filter-btn');
  const portfolioItems = document.querySelectorAll('.portfolio-item');
  
  if (filterButtons.length > 0 && portfolioItems.length > 0) {
    filterButtons.forEach(btn => {
      btn.addEventListener('click', function() {
        // Active state
        filterButtons.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const filter = this.getAttribute('data-filter');
        console.log(`[PORTFOLIO] Filter applied: ${filter}`);
        
        portfolioItems.forEach(item => {
          if (filter === 'all') {
            item.style.display = 'block';
          } else {
            if (item.getAttribute('data-category') === filter) {
              item.style.display = 'block';
            } else {
              item.style.display = 'none';
            }
          }
        });
      });
    });
  }

  // ============================================
  // 8. SIMPLE TESTIMONIALS FADE (subtle animation)
  // ============================================
  const testimonials = document.querySelectorAll('.testimonial');
  if (testimonials.length > 2) {
    let current = 0;
    
    setInterval(() => {
      testimonials.forEach((t, i) => {
        t.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        if (i === current) {
          t.style.opacity = '1';
          t.style.transform = 'translateY(0)';
        } else {
          t.style.opacity = '0.65';
          t.style.transform = 'translateY(8px)';
        }
      });
      current = (current + 1) % testimonials.length;
    }, 4200);
  }

  // ============================================
  // 9. SCROLL FADE-IN ANIMATIONS (IntersectionObserver)
  // ============================================
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.card, .testimonial, .section-header').forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px)';
      el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
      observer.observe(el);
    });
  }

  // ============================================
  // 10. DUPLICATE ID WARNING (for QA testing)
  // ============================================
  const allIds = {};
  document.querySelectorAll('[id]').forEach(el => {
    if (allIds[el.id]) {
      console.warn(`[QA-WARNING] Duplicate ID detected: #${el.id}`, el);
    } else {
      allIds[el.id] = true;
    }
  });

  // Final ready log
  console.log('%c[NEXUS] All QA handlers initialized. Broken links & images will log on interaction.', 'color:#22c55e');
});

// Bonus: Expose a global helper for manual QA testing in console
window.NEXUS_QA = {
  triggerBrokenImages: () => {
    document.querySelectorAll('img').forEach(img => img.dispatchEvent(new Event('error')));
    console.log('%c[QA] Manually triggered error handlers on all images', 'color:orange');
  },
  listAllLinks: () => {
    const links = Array.from(document.querySelectorAll('a')).map(a => a.href);
    console.table(links);
    return links;
  }
};