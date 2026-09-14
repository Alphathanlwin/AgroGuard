# AgroGuard - React UI Rules

## Product experience

AgroGuard should feel like a living field command center, not an enterprise CRUD application. The first screen must answer three questions within five seconds:

1. Where is the field?
2. Is the crop safe right now?
3. What should happen next?

The UI should make the IoT-guided versus normal-control story visually obvious without pretending that the growth simulation is a measured yield prediction.

## Visual direction

### Theme

- Primary mood: trustworthy, calm, agricultural, and data-rich.
- Main surface: warm off-white or very light neutral.
- Primary color: deep field green.
- Secondary color: soil brown or warm amber.
- Accent color: sky or water blue.
- Healthy: green.
- Warning: amber.
- Critical: red.
- Neutral/simulated: slate or purple, paired with a label.

Avoid an over-saturated farm illustration style. Maps, sensor values, and actions must remain easy to scan.

### Typography and density

- Use one readable UI font family and a clear type scale.
- Use short labels and plain language.
- Keep critical values large enough to read during a presentation.
- Do not make the map or animation compete with the status and action.
- Prefer cards with one purpose over decorative panels.

## Primary dashboard layout

```text
Top bar: AgroGuard | field selector | data mode | last update | demo reset

Main row:
  Left: GIS map and selected field context
  Right: crop status, health score, primary risk, next action

Second row:
  Sensor cards: temperature | humidity | soil moisture | pH | light
  Alert stream: latest warning/critical events and Telegram delivery state

Third row:
  One-year growth comparison: IoT-guided field vs normal-control field
  Timeline controls: play | pause | reset | scenario selector
```

The main dashboard should be usable on a laptop screen without excessive scrolling. On smaller screens, stack the map, status, sensors, alerts, and growth comparison in that order.

## Routes and navigation

| Route | Purpose | MVP priority |
|---|---|---|
| `/dashboard` | Judge-facing command center | Must have |
| `/fields/:fieldId` | Field context, map detail, and crop fit | Must have |
| `/simulation` | Replay scenarios and growth comparison | Must have |
| `/alerts` | Alert history, acknowledgement, and delivery status | Should have |
| `/settings` | Demo mode and notification configuration status | If time remains |

Navigation should not hide the main demo path. Keep dashboard, field, simulation, and alerts visible. Admin or user-management screens are not part of the MVP unless required by the team.

## Core components

### Field map

- Show selected field, approximate location when privacy requires it, and a clear map legend.
- Provide a seeded fallback map state when an external map is unavailable.
- Display a source and freshness label for GIS-derived context.
- Do not show exact coordinates in a presentation screenshot unless the field owner has approved it.

### Crop status card

Always show:

- Status word: Healthy, Warning, or Critical.
- Icon and color, never color alone.
- Health score only when its meaning is clear.
- Primary risk factor.
- One recommended next action.
- Confidence and data mode.
- Last updated time.

### Evidence panel

Show the factors behind the decision in a compact format:

| Factor | Current | Target | State |
|---|---:|---:|---|
| Soil moisture | value + unit | range | Good or limiting |
| Temperature | value + unit | range | Good or limiting |
| Soil pH | value | range | Good or limiting |
| Light | value + unit | range | Good or limiting |

Use plain-language explanations such as "Soil moisture is below the crop target" rather than model jargon.

### Sensor cards

- One card per measure.
- Show value, unit, timestamp, source, and freshness.
- Use a small trend arrow only when the direction is meaningful.
- Mark potentiometer-derived values as simulated estimates.
- Show stale or invalid state explicitly.

### Alert stream

- Sort newest first.
- Use severity text, icon, and color.
- Show field, risk, action, created time, and Telegram state.
- Make acknowledgement reversible in the data model.
- Suppressed duplicates should be explainable to the user.

### Growth comparison

Use two clearly labeled visual tracks:

- `IoT-guided field`: responds to measured or simulated warning events and records interventions.
- `Normal-control field`: follows a fixed routine and misses changing conditions.

Show stages such as germination, vegetative growth, flowering, fruiting, and harvest. Use a 12-month timeline with event markers for irrigation, heat stress, pH correction, and missed action.

The visual may use a chart, stage cards, or animated plant/field illustrations, but it must remain understandable when animation is paused. Add the label "Illustrative scenario, not a yield guarantee."

## Interactions

- Selecting a field updates context, crop assessment, sensor cards, alerts, and growth comparison.
- Moving a demo potentiometer or selecting a replay scenario updates the reading state and shows a visible update timestamp.
- A critical event must show the changed status, recommendation, LED/pump state, and Telegram delivery state.
- Reset affects only demo data and returns the UI to a known healthy baseline.
- Disable repeated actions while requests are pending.
- Confirm any action that changes field selection, crop plan, or demo state when accidental changes would confuse the presentation.

## UI states

### Loading

Use a meaningful skeleton or spinner in the affected panel. Do not freeze the whole dashboard while an optional GIS, weather, model, or Telegram call is pending.

### Empty

Explain what to do next: select a field, seed the demo, or add a device. Never show a blank table or empty chart without context.

### Error

Show the user-facing consequence and a next action. Example: "Live soil context is unavailable. Showing the seeded field context." Include a retry where useful.

### Degraded or stale

Use a visible badge such as `Seeded`, `Simulated`, `Stale`, or `Provider unavailable`. Do not silently present fallback data as live data.

### Success

Confirm meaningful actions briefly, such as "Critical reading received" or "Alert sent to Telegram." Avoid noisy toasts for every polling update.

## Forms and controls

- Label every field and include units in the label or helper text.
- Mark required fields clearly.
- Validate coordinates, ranges, and crop selection before submission.
- Show field-level errors near the input.
- Keep primary actions on the right or in a consistent action area.
- Use a scenario selector for safe demo manipulation instead of exposing arbitrary hidden state.
- Add helper text explaining that potentiometer pH and moisture values are simulated.

## Accessibility

- Maintain readable contrast for healthy, warning, critical, and simulated states.
- Pair every color state with text and an icon.
- Provide accessible names for map controls, chart controls, play/pause, reset, and alert actions.
- Ensure keyboard focus is visible and the main flow works without a mouse.
- Provide text summaries for charts and animations.
- Respect reduced-motion preferences; paused static stages must still communicate the story.

## Responsive behavior

- Desktop/laptop is the judging target.
- Tablet layout must preserve status and next action above the fold.
- On small screens, stack panels and make the map height fixed and usable.
- Do not place critical alerts only inside hover or tooltip interactions.

## Data honesty rules

- Every value has a source mode: live, simulated, seeded, replay, or degraded.
- Do not display more decimal places than the measurement supports.
- Do not label the pH potentiometer as a calibrated pH probe.
- Do not call the growth animation a prediction of actual yield.
- Do not claim export approval; show export-readiness factors or checklist status instead.

## Demo polish checklist

- [ ] The dashboard has one obvious demo path.
- [ ] The field and crop are pre-seeded.
- [ ] Status, action, and evidence are visible together.
- [ ] A dry-soil scenario changes both data and visual state.
- [ ] Wokwi/LED/pump state matches the UI scenario.
- [ ] Telegram delivery or safe fallback is visible.
- [ ] Growth comparison plays, pauses, and resets.
- [ ] No fake live data is presented without a label.
- [ ] The UI remains understandable if every external provider is offline.
