(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Click outside helper
  function onDocClick(fn) {
    document.addEventListener('click', fn, { capture: true });
  }

  // Dropdown (click)
  function initDropdowns() {
    $$('.nav-item[data-dropdown]').forEach((item) => {
      const btn = $('button.nav-link', item) || item.querySelector('button');
      const panel = item.querySelector('.dropdown-panel');
      if (!btn || !panel) return;

      const setExpanded = (v) => {
        btn.setAttribute('aria-expanded', String(v));
        panel.setAttribute('aria-hidden', String(!v));
        panel.style.display = v ? 'block' : 'none';
      };

      setExpanded(false);

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = btn.getAttribute('aria-expanded') === 'true';
        setExpanded(!isOpen);
      });

      onDocClick((e) => {
        if (!item.contains(e.target)) setExpanded(false);
      });
    });
  }

  // Mega menu (hover)
  function initMegaMenus() {
    $$('.nav-item[data-mega]').forEach((item) => {
      const panel = item.querySelector('.mega-panel');
      if (!panel) return;

      const links = $$('[data-reveal="hover"]', panel);

      function revealLinks() {
        links.forEach(a => { a.style.display = 'block'; });
      }

      item.addEventListener('mouseenter', () => {
        revealLinks();
        const btn = item.querySelector('button');
        if (btn) btn.setAttribute('aria-expanded', 'true');
        panel.setAttribute('aria-hidden', 'false');
      });

      item.addEventListener('mouseleave', () => {
        const btn = item.querySelector('button');
        if (btn) btn.setAttribute('aria-expanded', 'false');
        panel.setAttribute('aria-hidden', 'true');
        // links remain visible while hovering; Playwright usually checks after action,
        // so we keep them hidden again to make reveal deterministic.
        links.forEach(a => { a.style.display = 'none'; });
      });
    });
  }

  // Mobile menu (hamburger open) + reveal hidden links inside accordion panel
  function initMobileMenu() {
    const menu = $('#mobileMenu');
    if (!menu) return;

    const openBtn = $('.hamburger');
    const closeBtn = $('.mobile-close');

    function setOpen(v) {
      menu.classList.toggle('open', v);
      menu.setAttribute('aria-hidden', String(!v));
      if (openBtn) openBtn.setAttribute('aria-expanded', String(v));
      if (!v) {
        // reset accordions
        $$('.mobile-accordion-panel', menu).forEach(p => {
          p.hidden = true;
        });
      }
      // Reveal rule: links become visible only after hamburger menu opening
      if (v) {
        $$('.reveal-on-mobile-open', menu).forEach(a => { a.style.display = 'block'; });
      } else {
        $$('.reveal-on-mobile-open', menu).forEach(a => { a.style.display = 'none'; });
      }
    }

    if (openBtn) openBtn.addEventListener('click', (e) => { e.stopPropagation(); setOpen(true); });
    if (closeBtn) closeBtn.addEventListener('click', (e) => { e.stopPropagation(); setOpen(false); });

    menu.addEventListener('click', (e) => {
      // clicking backdrop closes
      if (e.target === menu) setOpen(false);
    });

    // Mobile accordion within mobile menu
    $$('.mobile-accordion[data-acc]').forEach((btn) => {
      const key = btn.getAttribute('data-acc');
      const panel = $(`[data-acc-panel="${key}"]`, menu) || $(`[data-acc-panel="${key}"]`, document);

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!isOpen));
        if (panel) panel.hidden = isOpen;
        if (panel) panel.hidden = !isOpen;
      });
    });
  }

  // Accordion toggle
  function initAccordions() {
    $$('.accordion').forEach((acc) => {
      $$('.acc-item', acc).forEach((item) => {
        const btn = $('.acc-btn', item);
        const panel = $('.acc-panel', item);
        if (!btn || !panel) return;

        btn.addEventListener('click', () => {
          const open = btn.getAttribute('aria-expanded') === 'true';
          btn.setAttribute('aria-expanded', String(!open));
          panel.hidden = open;

          // Accordion #2 reveal targets
          // We reveal when accordion with id accordion2 is expanded.
          const isAcc2 = acc.getAttribute('data-accordion') === 'two' || acc.id === 'accordion2' || acc.closest('#accordion2');
          if (isAcc2 && !open) {
            // Reveal only after expansion of Accordion #2 panel
            const revealAnchors = $$('[data-reveal="acc2"]', panel);
            revealAnchors.forEach(a => { a.style.display = 'block'; });
          } else if (isAcc2 && open) {
            const revealAnchors = $$('[data-reveal="acc2"]', panel);
            revealAnchors.forEach(a => { a.style.display = 'none'; });
          }
        });
      });
    });
  }

  // Tabs switching reveal targets
  function initTabs() {
    $$('.tabs[data-tabs]').forEach((tabsWrap) => {
      const tablist = $('.tablist', tabsWrap);
      const panels = $$('.tab-panel', tabsWrap);
      const tabs = $$('[role="tab"]', tablist);

      function setActive(tabValue) {
        tabs.forEach(t => {
          const isActive = t.getAttribute('data-tab') === tabValue;
          t.setAttribute('aria-selected', String(isActive));
          if (isActive) t.classList.add('active');
          else t.classList.remove('active');
        });

        panels.forEach(p => {
          const isOverview = p.id === 'tab-panel-overview';
          p.hidden = !(
            (p.getAttribute('aria-labelledby') === `tab-${tabValue}`) ||
            (p.id === 'tab-panel-overview' && tabValue === 'overview')
          );
        });

        // Reveal by tab switching (explicit reveal ids)
        if (tabValue === 'resources') {
          $$('[data-reveal="tab:resources"]', tabsWrap).forEach(a => a.style.display = 'block');
          $$('[data-reveal="tab:explore"]', tabsWrap).forEach(a => a.style.display = 'none');
        } else if (tabValue === 'explore') {
          $$('[data-reveal="tab:explore"]', tabsWrap).forEach(a => a.style.display = 'block');
          $$('[data-reveal="tab:resources"]', tabsWrap).forEach(a => a.style.display = 'none');
        } else {
          $$('[data-reveal="tab:resources"]', tabsWrap).forEach(a => a.style.display = 'none');
          $$('[data-reveal="tab:explore"]', tabsWrap).forEach(a => a.style.display = 'none');
        }
      }

      tabs.forEach((t) => {
        t.addEventListener('click', () => {
          const v = t.getAttribute('data-tab');
          setActive(v);
        });
      });

      // initial state: overview; hide all
      setActive('overview');
    });
  }

  // Hover menu reveal targets: only on hover
  function initHoverMenus() {
    $$('.hover-wrap[data-hover-menu]').forEach((wrap) => {
      const panel = $('.hover-panel', wrap);
      if (!panel) return;
      const links = $$('[data-reveal="hovermenu"]', panel);

      // ensure hidden initially (some markup sets display:none, keep deterministic)
      links.forEach(a => { a.style.display = 'none'; });

      wrap.addEventListener('mouseenter', () => links.forEach(a => { a.style.display = 'block'; }));
      wrap.addEventListener('mouseleave', () => links.forEach(a => { a.style.display = 'none'; }));
    });
  }

  initDropdowns();
  initMegaMenus();
  initMobileMenu();
  initAccordions();
  initTabs();
  initHoverMenus();
})();
