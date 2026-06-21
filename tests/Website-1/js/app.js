/* =============================================
   Nexus Consulting — app.js
   ============================================= */

(function () {
  'use strict';

  /* ── Navbar scroll effect ─────────────────── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Hamburger menu ───────────────────────── */
  const hamburger = document.querySelector('.hamburger');
  const navMenu   = document.querySelector('.navbar__nav');
  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      const open = navMenu.style.display === 'flex';
      navMenu.style.cssText = open
        ? ''
        : 'display:flex;flex-direction:column;position:absolute;top:72px;left:0;right:0;background:var(--navy);padding:16px 24px;gap:4px;z-index:999;';
      hamburger.setAttribute('aria-expanded', String(!open));
    });
  }

  /* ── Active nav link ──────────────────────── */
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.navbar__nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* ── Intersection observer for fade-in ────── */
  const fadeEls = document.querySelectorAll(
    '.service-card, .portfolio-card, .testimonial-card, .blog-card, ' +
    '.service-detail-card, .blog-list-card, .team-card'
  );
  if ('IntersectionObserver' in window && fadeEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });

    fadeEls.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity .45s ease, transform .45s ease';
      io.observe(el);
    });
  }

  /* ── Counter animation (hero stats) ────────── */
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el  = e.target;
        const end = parseInt(el.dataset.count, 10);
        const dur = 1400;
        const step = 16;
        const inc  = end / (dur / step);
        let cur = 0;
        const tick = () => {
          cur = Math.min(cur + inc, end);
          el.textContent = Math.floor(cur) + (el.dataset.suffix || '');
          if (cur < end) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        cio.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(c => cio.observe(c));
  }

  /* ── Portfolio filter (portfolio.html) ──────── */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const portfolioCards = document.querySelectorAll('.portfolio-full-grid .portfolio-card');
  if (filterBtns.length && portfolioCards.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        portfolioCards.forEach(card => {
          const match = filter === 'all' || card.dataset.cat === filter;
          card.style.display = match ? '' : 'none';
        });
      });
    });
  }

  /* ── Contact form ───────────────────────────── */
  const form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      const original = btn.textContent;
      btn.textContent = 'Sending…';
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = '✓ Message Sent!';
        btn.style.background = '#22C55E';
        setTimeout(() => {
          btn.textContent = original;
          btn.style.background = '';
          btn.disabled = false;
          form.reset();
        }, 3000);
      }, 1200);
    });
  }

})();