# LiveMirror Frontend Design System

This document is the source of truth for future LiveMirror frontend work.

## Direction

LiveMirror uses a hybrid style inspired by proven product patterns:

- Creator Studio: calm, focused, useful for anchors, content teams, and operators who need to improve scripts and decisions.
- Precision Data Workbench: clear, dense enough for operational analytics, with strong hierarchy for task status, reports, attribution, suggestions, and trends.
- Reference pattern: Linear-like dark command center plus Metabase/Amplitude-like analytics workbench. Use the pattern language, not a direct copy.

The product should feel like a working studio with reliable analytics, not a generic admin template.

## Principles

- Start with the active workflow. The first screen should help users upload, inspect the latest task, or continue analysis.
- Make analysis actionable. Pair metrics with the next useful action, such as viewing a report, filling sample data, or opening suggestions.
- Keep density intentional. KPI cards, tables, and report sections can be compact, but whitespace must separate decisions.
- Avoid decorative noise. Do not add floating blobs, ornamental gradients, or marketing-only sections.
- Keep mobile usable. Navigation, cards, forms, and tables must remain readable at 375px width.

## Visual Language

- Background: graphite black with green undertones. Never use pure white surfaces in the main app.
- Surface: layered dark panels for cards, editor panels, forms, and tables.
- Neutral panels: use green-black and graphite surfaces only. Do not use white, off-white, or light gray cards, buttons, inputs, empty states, or table backgrounds.
- Primary: luminous teal for key navigation, active states, and primary buttons.
- Accent: coral for creator/workflow emphasis and amber only for warning or conversion hints.
- Text: soft off-white for primary content, muted sage-gray for secondary text.
- Radius: 8px maximum for cards and buttons.
- Motion: subtle 150-220ms transitions only; respect reduced motion.

Recommended tokens:

```css
--app-bg: #0b1110;
--app-surface: #121b18;
--app-surface-soft: #18241f;
--app-surface-strong: #20302a;
--app-border: #2b3c35;
--app-text: #eef6f2;
--app-text-soft: #99aaa3;
--app-primary: #2dd4bf;
--app-primary-strong: #5eead4;
--app-accent: #ff7a59;
--app-warning: #f2b84b;
```

## Layout Rules

- The app shell uses a sticky topbar with compact product identity and clear workflow navigation.
- Main pages use a full-width workbench area with constrained content where helpful.
- Repeated data and workflow blocks may use cards; sections themselves should remain unframed.
- Cards should have a thin border, dark layered surface, and stable internal spacing.
- Avoid cards inside cards. Use lists, grids, dividers, or soft bands inside a card instead.

## Components

- Primary buttons: teal fill, graphite text, visible hover and focus states.
- Secondary buttons: dark surface with border and off-white text.
- Tags and statuses: use semantic colors, but keep them quieter than primary actions.
- Forms: group related inputs with spacing, labels, and helper text; do not rely on placeholder-only context when a workflow is complex.
- Reports: lead with status and summary, then transcript, segments, attribution, and suggestions.
- Analysis pages: keep sample/fill actions visible, and render empty states as useful prompts.

## Typography

- Use system fonts by default for performance and Chinese text quality.
- Titles should be confident but not oversized.
- Numeric metrics may use the same font with stronger weight; avoid mixing in monospace unless showing IDs, logs, or code-like data.
- Letter spacing stays at `0`.

## Anti-Patterns

- Dominant purple, purple-blue gradients, dark blue/slate themes, beige/tan palettes, brown/orange-heavy themes, white card islands, white form fields, or white secondary buttons.
- Decorative bokeh, gradient orbs, or unrelated illustrations.
- Marketing landing pages before the actual tool workflow.
- Low-contrast muted text, especially inside cards and table cells.
- Hover effects that resize cards, buttons, nav items, tables, or grids.

## Acceptance Checklist

- Typecheck and build pass.
- Home, upload, report, attribution, suggestions, and trends share the same visual language.
- 375px, 768px, 1024px, and 1440px layouts remain readable.
- Text does not overflow cards, buttons, or nav items.
- Keyboard focus is visible for links and buttons.
- The app can be started locally and `http://localhost:3000` returns 200.
