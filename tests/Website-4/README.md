# Form Testing Lab

A comprehensive playground for testing form automation systems. Built with pure HTML, CSS, and JavaScript — no frameworks, no backend.

## Pages

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | Landing page with cards linking to all test scenarios |
| Contact | `contact.html` | Working form, JS Error form, and Delayed form |
| Quote | `quote.html` | Broken form (button does nothing) |
| Newsletter | `newsletter.html` | Validation form (email required) |
| Feedback | `feedback.html` | Fake success form (shows success but doesn't save) |

## Ground Truth

### 1. Working Contact Form
- **Location:** `contact.html` #working
- **Fields:** Name, Email, Phone, Message
- **Expected:** Submitting shows "Successfully submitted" message
- **Behavior:** Client-side validation, displays success overlay, no actual data sent

### 2. Broken Form
- **Location:** `quote.html`
- **Fields:** Name, Email, Project Type, Budget Range
- **Expected:** Nothing happens
- **Behavior:** Button is `type="button"` with no click handler. No action, no feedback.

### 3. Validation Form
- **Location:** `newsletter.html`
- **Fields:** Name (optional), Email (required), Checkboxes
- **Expected:** "Email required" error when submitted empty
- **Behavior:** Shows inline error message, prevents submission until email is provided

### 4. Fake Success Form
- **Location:** `feedback.html`
- **Fields:** Name, Rating (stars), Message
- **Expected:** Success message displayed
- **Behavior:** Shows success overlay but **does not** save, transmit, or log any data

### 5. JS Error Form
- **Location:** `contact.html` #js-error
- **Fields:** Issue Title, Description
- **Expected:** Console error
- **Behavior:** Submit throws `Error: Intentional JavaScript error triggered by form submission`

### 6. Delayed Form
- **Location:** `contact.html` #delayed
- **Fields:** Name, Phone Number
- **Expected:** Success after 3 seconds
- **Behavior:** Shows loading spinner for 3 seconds, then displays success message

## Design

- Modern card-based layout
- Responsive navbar with mobile hamburger menu
- Sticky navigation with glassmorphism effect
- Color-coded form badges (green = working, red = broken, etc.)
- Smooth animations and transitions
- Star rating component on feedback form
- Loading spinner on delayed form
