# Frontend Worklog

This file records grouped updates introduced during the dashboard/tour/quiz/profile/shop iteration.

## Debug/Tutorial Integration
- Added explicit tutorial trigger in debug menu.
- Connected event to dashboard tutorial starter.

## Dashboard Tour Anchoring
- Added pet toggle selector as explicit tour anchor.
- Adjusted tour targeting behavior for reliability.

## Tour Overlay and Sizing
- Added viewport-safe constraints for tour cards.
- Improved overlay layering and focus behavior.

## App Routing Stability
- Removed transition wrapper around router-view to avoid stale renders during route switches.

## Quiz Navigation Fixes
- Quiz list back action now returns to challenges.
- Quiz detail back actions return deterministically to quiz list.

## Shop Card Layout
- Compacted internal card spacing to avoid clipped content for pets and sounds.

## Home Presentation
- Tightened mission text spacing for cleaner hero content density.
