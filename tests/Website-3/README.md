# GROUND TRUTH

Navbar > Services dropdown
- Hidden elements:
  - Mega menu links in index.html under "Services" mega panel:
    - pricing.html (working)
    - legacy-pricing.html (broken)
    - faq.html (working)
    - hidden404.html (broken)
    - services-old.html (broken)
    - deadpage.html (broken)
- Reveal rule:
  - Revealed by HOVER over the "Services" mega menu trigger.
  - app.js: initMegaMenus() shows links on mouseenter, hides them again on mouseleave for deterministic extraction.

legacy-pricing.html
- Hidden broken link target (in mega menu).
- Reveal rule:
  - HOVER the "Services" mega menu.

Accordion #2
- Hidden elements:
  - pricing.html (working)
  - faq.html (working)
  - deadpage.html (broken)
- Reveal rule:
  - Reveal only when the accordion with data-accordion="two" expands.
  - app.js: initAccordions() checks accordion #2 and displays links when opened.

deadpage.html
- Hidden broken link target (in Accordion #2 panel).
- Reveal rule:
  - Expand Accordion #2.

Mobile menu
- Hidden elements:
  - pricing.html (working)
  - legacy-pricing.html/services-old.html (broken)
  - faq.html (working)
  - deadpage.html (broken)
- Reveal rule:
  - The hamburger must open the mobile menu.
  - app.js: initMobileMenu() reveals links with .reveal-on-mobile-open when open.

services-old.html
- Hidden broken link target:
  - Present in mega menu (hover)
  - Present in hover menu (hover)
  - Present in mobile menu (after hamburger open)
- Reveal rules:
  - HOVER Services mega menu.
  - OR HOVER the "Hover for more" hover menu trigger.
  - OR open hamburger menu.

Mega menu
- Hidden elements:
  - pricing.html, faq.html (working)
  - legacy-pricing.html, hidden404.html, services-old.html, deadpage.html (broken)
- Reveal rule:
  - HOVER "Services" mega menu.

hidden404.html
- Hidden broken link target:
  - Present in mega menu (hover)
  - Present in hover menu (hover)
  - Present in tabs "Explore" (tab switch)
- Reveal rules:
  - HOVER Services mega menu.
  - OR HOVER "Hover for more".
  - OR switch Tabs to "Explore".

Tabs
- Hidden elements:
  - pricing.html and services-old.html (broken) revealed only in Resources tab
  - faq.html (working) and hidden404.html (broken) revealed only in Explore tab
- Reveal rule:
  - Click/switch tabs; app.js: initTabs().
