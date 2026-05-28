---
name: ClearPoint Enterprise Logic
colors:
  surface: '#f7fafb'
  surface-dim: '#d7dadb'
  surface-bright: '#f7fafb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4f5'
  surface-container: '#ebeeef'
  surface-container-high: '#e6e9ea'
  surface-container-highest: '#e0e3e4'
  on-surface: '#181c1d'
  on-surface-variant: '#424655'
  inverse-surface: '#2d3132'
  inverse-on-surface: '#eef1f2'
  outline: '#737687'
  outline-variant: '#c2c6d8'
  surface-tint: '#0054d7'
  primary: '#004ecb'
  on-primary: '#ffffff'
  primary-container: '#0b65fc'
  on-primary-container: '#f6f5ff'
  inverse-primary: '#b3c5ff'
  secondary: '#585f65'
  on-secondary: '#ffffff'
  secondary-container: '#dce3ea'
  on-secondary-container: '#5e656b'
  tertiary: '#00626b'
  on-tertiary: '#ffffff'
  tertiary-container: '#007d88'
  on-tertiary-container: '#e2fbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#00184a'
  on-primary-fixed-variant: '#003fa5'
  secondary-fixed: '#dce3ea'
  secondary-fixed-dim: '#c0c7ce'
  on-secondary-fixed: '#151c21'
  on-secondary-fixed-variant: '#41484d'
  tertiary-fixed: '#8ef2ff'
  tertiary-fixed-dim: '#4fd8e8'
  on-tertiary-fixed: '#001f23'
  on-tertiary-fixed-variant: '#004f56'
  background: '#f7fafb'
  on-background: '#181c1d'
  surface-variant: '#e0e3e4'
  status-warning: '#F59E0B'
  status-ready: '#10B981'
  status-blocked: '#EF4444'
  surface-charcoal: '#1F262B'
  aqua-accent: '#43CFDF'
typography:
  headline-xl:
    fontFamily: Lexend
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Lexend
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  code-sm:
    fontFamily: Courier Prime
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 32px
  workflow-rail-height: 80px
  sidebar-width: 320px
---

## Brand & Style

The design system is engineered for the "Workforce, not Tooling" philosophy. It moves away from the ephemeral nature of "chatbots" toward the permanence of enterprise personnel management. The aesthetic is **Corporate / Modern**, heavily influenced by Material 3 but stripped of any "playful" tendencies to ensure a high-trust, regulatory-ready environment.

The brand personality is **authoritative, defensible, and institutional**. It should evoke the same emotional response as a high-security clearance process or an executive HR platform. Visuals emphasize the transition from raw AI potential to governed organizational assets through structured, evidence-focused layouts.

Key Principles:
- **Human-Parallelism:** Use visual metaphors that align with HR workflows (Passports, Personnel Files, Job Descriptions).
- **Audit-Ready Clarity:** Every AI claim must be visually grounded to a source chip or regulatory citation.
- **Fail-Closed Design:** The UI must clearly distinguish between "Ready" (Authorized) and "Blocked" (Unauthorized) states with uncompromising visual hierarchy.

## Colors

The palette is anchored by **ClearPoint Blue**, used exclusively for primary actions and the active state of the "Workflow Rail." This is contrasted against **Charcoal**, which provides the structural weight for headers and primary text, and **Aqua**, used for technical accents and AI-specific metadata.

**Functional Color Strategy:**
- **Primary Blue:** Navigation, primary buttons, and verified identity states.
- **Charcoal:** Institutional framing and high-density text components.
- **Aqua:** Secondary accents that highlight "AI-derived" insights vs. deterministic data.
- **Status Triage:** High-visibility Orange (Warning), Red (Blocked), and a sober Green (Ready) are used for decision badges. These are saturated enough to demand attention but should not feel celebratory; they are indicators of compliance status.

## Typography

This design system utilizes a dual-font strategy to balance character with utility. **Lexend** is used for all headings; its geometric clarity provides a modern, "Google-aligned" feel while maintaining the authoritative posture required for an enterprise-grade tool. **Inter** is the workhorse for all body copy, UI labels, and data visualizations, chosen for its exceptional legibility in high-density information environments.

**Specialized Usage:**
- **Lexend Bold:** Reserved for top-level Page Titles and "Candidate Card" headers.
- **Inter Semi-Bold:** Used for table headers, labels, and grounded source chips to ensure they remain legible at small sizes.
- **Monospace (Courier Prime):** Strictly for "Evidence Event" logs and "AI BOM" raw data views to signal deterministic, machine-read information.

## Layout & Spacing

The layout is built on a **12-column fixed grid** for desktop, centering the core "Artifact Workspace" while reserving the right-hand column for the "Decision Panel." The system employs a "Workforce-Parallel" layout model:

- **Workflow Rail:** A persistent horizontal anchor at the top of the workspace tracking the stage (Discovery to Decision).
- **Artifact Workspace:** A tabbed central area for deep-dives. Use standard 24px gutters to maintain an airy, legible feel even when data density is high.
- **Mobile Reflow:** On mobile, the "Workflow Rail" collapses into a step-indicator, and the "Decision Panel" becomes a sticky bottom sheet to ensure the "Ready/Blocked" status is always visible.

Spacing follows a strict 4px (0.25rem) base unit, with most component-to-component spacing defaulting to 16px (4 units) or 24px (6 units) for section-level separation.

## Elevation & Depth

In alignment with Material 3 principles, the design system uses **Tonal Layers** rather than aggressive shadows. Surfaces are used to group related artifacts and "Personnel Files."

- **Level 0 (Surface):** The application background, utilizing a very subtle cool gray or white.
- **Level 1 (Card/Container):** Main content containers (Candidate Cards, Artifact Panels) use a subtle low-opacity shadow (4-8% opacity Charcoal) to lift them from the background.
- **Level 2 (Interaction):** Hover states on "Evidence Chips" and "Workflow Stages" increase the lift and add a Primary Blue border (1px) to indicate focus.
- **The "Decision Overlay":** When a status is "Blocked," a high-contrast modal or panel uses a higher elevation to interrupt the workflow, signaling a hard-stop compliance requirement.

## Shapes

The shape language reflects the system's "Professional" and "Regulatory" nature. It uses **Rounded (0.5rem)** corners for most structural elements, providing a modern but structured appearance.

- **Standard Elements:** Buttons, cards, and input fields use a 0.5rem (8px) radius.
- **Status Badges:** Use "Pill-shaped" (full-round) geometry to differentiate functional status indicators from structural layout cards.
- **The "Artifact Suite":** Document-based metaphors (Passports, Policies) should retain the standard rounded-lg (1rem) corners to suggest a distinct object that can be "exported" or "filed."

## Components

### Buttons
- **Primary:** ClearPoint Blue background, white text, 8px radius. High-emphasis for "Approve Agent" or "Generate Passport."
- **Secondary:** Charcoal outline or Aqua text on transparent background. Used for "View Evidence" or "Download BOM."

### Status Badges (The Decision Suite)
- **Ready:** Solid Green background, white Lexend text.
- **Conditional:** Solid Orange background, white Lexend text.
- **Blocked:** Solid Red background, white Lexend text.
- *Shape:* Always pill-shaped with uppercase label-md typography.

### Input Fields & Selects
- Follow a "System-SaaS" style: 1px Charcoal border (30% opacity), Inter body-md text, 8px radius. Focus state uses 2px Primary Blue border.

### Grounding Chips
- Unique to this system: Small, compact badges (Aqua or Neutral) that contain a reference to a regulatory body (e.g., "EU AI ACT ART. 13"). These appear inline with AI-generated summaries to provide immediate "Evidence Grounding."

### Candidate Cards
- The primary "Identity" component. Features a headshot or agent-icon on the left, Name/Role in Lexend Headline-md, and metadata (Model, Version, Risk Score) in Inter Body-sm.