# Design System Specification: The Precision Architect

## 1. Overview & Creative North Star
This design system is built for the high-stakes environment of healthcare operations, where clarity saves lives and precision is the ultimate form of empathy. We are moving away from the "clunky hospital terminal" aesthetic toward a **Creative North Star: The Clinical Sentinel.**

The Sentinel is authoritative, calm, and hyper-organized. We break the "generic SaaS" mold by utilizing **Intentional Asymmetry** and **Editorial Hierarchy**. While the data density remains high for professional utility, we utilize "breathing rooms"—pockets of significant white space—to separate critical decision-making zones from routine monitoring. By overlapping high-density tables with sophisticated, glass-like overlays, we create a sense of depth and focus that guides the clinician's eye exactly where it needs to be.

---

## 2. Colors & Surface Philosophy
The palette is rooted in a deep, professional foundation of `primary` (#1a365d) and `secondary` (#2c7a7b), providing an immediate sense of institutional trust.

### The "No-Line" Rule
To achieve a premium, custom feel, **1px solid borders are prohibited for sectioning.** Conventional grids feel rigid and "templated." Instead, boundaries must be defined through:
*   **Background Shifts:** Distinguish a sidebar or header using `surface-container-low` against a `surface` background.
*   **Tonal Transitions:** Use a subtle change from `surface-container` to `surface-container-high` to define a workspace.

### Surface Hierarchy & Nesting
Think of the UI as a series of stacked, fine-milled paper sheets.
*   **Base:** `surface` (#f8f9ff)
*   **Sections:** `surface-container-low` for secondary information.
*   **Primary Work Area:** `surface-container-lowest` (pure white #ffffff) to make data "pop."
*   **Floating Context:** `surface-container-highest` for active flyouts or modals.

### The "Glass & Gradient" Rule
For floating elements (like status notifications or quick-action menus), use **Glassmorphism**. Apply `surface-tint` at 10% opacity with a `backdrop-blur` of 12px. For main CTAs, use a subtle linear gradient from `primary` (#002045) to `primary_container` (#1a365d) at a 135-degree angle to provide a "jewel" polish that flat hex codes lack.

---

## 3. Typography
Our typography strategy balances the "Display" (The Authority) with the "Label" (The Precision).

*   **The Display Scale (Manrope):** Used for headlines and dashboard summaries. Manrope’s geometric but open curves feel modern and approachable. It signals that this software is cutting-edge.
*   **The UI Scale (Inter):** Used for all data entry, tables, and labels. Inter is the workhorse. At `body-sm` (0.75rem), it remains legible even in complex audit logs.

**Hierarchy Note:** Use high contrast in weight rather than just size. A `headline-sm` in Semi-Bold paired with a `label-md` in Medium weight creates a structured, editorial feel that mimics high-end medical journals.

---

## 4. Elevation & Depth
In a data-heavy environment, shadows can create visual "mud." We use **Tonal Layering** as our primary driver of depth.

*   **Ambient Shadows:** If an element must float (e.g., a critical alert), use an extra-diffused shadow: `offset-y: 8px`, `blur: 24px`, `color: on-surface` at 6% opacity. This mimics natural light rather than a digital drop shadow.
*   **The Ghost Border:** For accessibility in form fields, use a "Ghost Border"—the `outline-variant` token at 15% opacity. This provides a "suggestion" of a boundary without cluttering the visual field.
*   **Nesting Principle:** An inner container must always be "lighter" or "heavier" than its parent. Never place a `surface-container-low` card on a `surface-container-low` background.

---

## 5. Components

### High-Density Tables
*   **Forbidden:** Vertical and horizontal grid lines.
*   **Solution:** Use `spacing.2.5` (0.5rem) for vertical cell padding. Distinguish rows using a subtle `surface-container-low` hover state.
*   **Header:** Use `label-sm` in all-caps with `0.05em` letter spacing for an authoritative, "ledger" feel.

### Status Badges
*   **Style:** Pill-shaped (`rounded-full`). 
*   **Coloring:** Use `on-error-container` (text) on `error_container` (background) for Errors. The background should be at 40% opacity to let the surface texture peek through, maintaining the "clinical" look.

### Buttons
*   **Primary:** Gradient of `primary` to `primary_container`. Radius: `md` (0.375rem).
*   **Secondary:** Ghost style. No background, `outline` token for text, and a `Ghost Border` that only appears on hover.
*   **Tertiary:** `secondary` (#13696a) text with no container, used for low-priority actions like "Cancel" or "Export."

### Audit Logs & Timelines
*   **Layout:** Avoid lines connecting timeline nodes. Use the `spacing` scale to create a "Visual Pulse." An audit entry starts with a `title-sm` timestamp in `primary` and a `body-md` description.
*   **Separation:** Use `spacing.8` (1.75rem) between log entries to allow the eye to rest between data points.

### Input Fields
*   **Structure:** Minimalist. A simple `surface-container-highest` background with a bottom-only `outline-variant` (20% opacity) "Ghost Border." Upon focus, the border transitions to `secondary` teal.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use `surface-container` tiers to group related medical data (e.g., Patient Vitals vs. Billing History).
*   **Do** prioritize `spacing.10` and `spacing.12` for top-level layout margins to ensure the "Editorial" feel isn't lost to clutter.
*   **Do** use `secondary_container` (Teal) for "Growth" or "Success" metrics to provide a calming clinical contrast to the deep blue.

### Don't
*   **Don't** use pure black (#000000) for text. Always use `on-surface` (#0b1c30) to maintain tonal harmony with the deep blues.
*   **Don't** use standard "Material Design" shadows. They are too heavy for clinical software; stick to Tonal Layering.
*   **Don't** use icons without labels in critical workflows. In healthcare, "Icon-only" is a cognitive hazard. Pair icons with `label-sm` text.