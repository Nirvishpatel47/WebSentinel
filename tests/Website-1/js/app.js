(function () {
  const doc = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  let theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  doc.setAttribute('data-theme', theme);

  if (toggle) {
    const updateLabel = () => {
      toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      toggle.innerHTML = '<span aria-hidden="true">' + (theme === 'dark' ? '☀' : '◐') + '</span>';
    };
    updateLabel();
    toggle.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      doc.setAttribute('data-theme', theme);
      updateLabel();
    });
  }

  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.primary-nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('is-open');
    });
  }

  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      if (!button) return;
      const original = button.textContent;
      button.textContent = 'Enquiry captured';
      button.disabled = true;
      window.setTimeout(function () {
        button.textContent = original;
        button.disabled = false;
      }, 1600);
    });
  }
})();