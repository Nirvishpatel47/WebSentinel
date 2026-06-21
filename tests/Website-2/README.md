# Image Scanner Test Website - Ground Truth

This website is designed for testing image scanners. It contains a mix of **working** and **broken** images across multiple pages and sections.

---

## Working Images

These images are guaranteed to load successfully:

- `images/logo.png`
- `images/hero.jpg`
- `images/team.jpg`
- `images/gallery1.jpg`
- `images/gallery2.jpg`
- `images/gallery3.jpg`

---

## Broken Images

These images are **intentionally broken** and will fail to load:

- `images/missing1.jpg`
- `images/missing2.png`
- `images/404-image.png`
- `images/assets/broken.jpg`
- `images/images/fake.webp`
- `images/notfound.svg`
- `images/bad-icon.ico`
- `images/team-old.jpg`
- `images/gallery999.png`
- `images/header-image.png`

---

## Broken Image Locations


| **Image**           | **Location**                          |
| ------------------- | ------------------------------------- |
| `header-image.png`  | Hero section (hidden in `index.html`) |
| `gallery999.png`    | Gallery card #3 in `index.html`       |
| `bad-icon.ico`      | Footer icon in all pages              |
| `missing1.jpg`      | Gallery preview in `index.html`       |
| `missing2.png`      | Gallery grid in `gallery.html`        |
| `404-image.png`     | Gallery grid in `gallery.html`        |
| `assets/broken.jpg` | Gallery grid in `gallery.html`        |
| `images/fake.webp`  | Footer icon in `gallery.html`         |
| `notfound.svg`      | Footer icon in `about.html`           |
| `team-old.jpg`      | Team section in `index.html`          |


---

## Folder Structure

```
Website-2/
├── index.html
├── about.html
├── gallery.html
├── services.html
├── contact.html
├── css/
│   └── style.css
├── js/
│   └── app.js
├── images/
│   ├── logo.png
│   ├── hero.jpg
│   ├── team.jpg
│   ├── gallery1.jpg
│   ├── gallery2.jpg
│   └── gallery3.jpg
└── README.md
```

---

## Usage

1. **Deploy the website** on a local or remote server.
2. **Run your image scanner** to detect broken images.
3. **Compare results** with the ground truth provided in this file.

---

## Notes

- Broken images are styled with a **red dashed border** and a light red background for visual identification.
- The JavaScript console logs all working and broken images for debugging.
- The website is fully responsive and works on all modern browsers.