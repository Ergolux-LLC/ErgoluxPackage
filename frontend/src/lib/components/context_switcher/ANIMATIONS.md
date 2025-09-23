# Context Switcher Animation Guide

## 🎬 Animation Details

The Context Switcher now includes delightful, user-friendly animations that make interactions feel loveable and engaging.

### Click Animation (`loveableBounce`)

**Duration:** 0.6 seconds  
**Easing:** `cubic-bezier(0.68, -0.55, 0.265, 1.55)` (bouncy)

**Button Animation:**

- Starts with a lift (`translateY(-2px) scale(1)`)
- Bounces up with scale increase (`translateY(-8px) scale(1.1)`)
- Settles with gentle oscillation
- Enhanced brightness during animation (140% peak)

**Icon Animation (`iconPulse`):**

- Icon scales up to 130% with playful rotation (±5°)
- Gentle bounce-back with micro-rotations
- Synchronized with button animation

**Ripple Effect:**

- Radial expanding circle using the button's unique color
- Starts from center and expands to 120px diameter
- Fades from 80% to 0% opacity
- Creates satisfying tactile feedback

### Celebration Animation (`celebration`)

**Duration:** 0.8 seconds  
**Trigger:** When switching to a new sub-app (becomes active)

**Button Celebration:**

- Multiple bounce phases with varying heights
- Scale variations for dynamic feel
- Longer, more pronounced than click animation

**Icon Celebration (`celebrationIcon`):**

- Dramatic scale increase (up to 140%)
- Larger rotation angles (±10°)
- Multiple celebration "beats"

### Enhanced Visual Feedback

**Click State Enhancements:**

- Enhanced glow effect with 3px border
- Increased shadow depth and spread
- Color-specific glow using `color-mix()` where supported
- Fallback to solid colors for older browsers

**Color Transitions:**

- Smooth brightness modulation during animations
- From grayscale default to full vibrant colors
- Peak brightness of 140% during click, settling to active brightness

### Technical Implementation

**JavaScript Integration:**

```javascript
function handleSubAppClick(subApp, event) {
  const button = event.currentTarget;

  // Add click animation
  button.classList.add("clicked");
  setTimeout(() => button.classList.remove("clicked"), 600);

  // Add celebration if becoming new active
  if (!wasActive && activeSubApp === subApp.id) {
    button.classList.add("newly-active");
    setTimeout(() => button.classList.remove("newly-active"), 800);
  }
}
```

**CSS Architecture:**

- Uses `:global()` selectors for dynamically added classes
- Combines multiple animation properties for rich effects
- Progressive enhancement with `@supports` queries
- Maintains performance with CSS-only animations

### User Experience Benefits

1. **Immediate Feedback:** Click animations provide instant response
2. **State Clarity:** Celebration animations highlight state changes
3. **Playful Interaction:** Bouncy easing makes interface feel friendly
4. **Visual Hierarchy:** Enhanced active states guide user attention
5. **Smooth Transitions:** All animations use consistent timing and easing

The animations are designed to be:

- ✨ **Loveable** - Bouncy, playful character
- ⚡ **Responsive** - Immediate visual feedback
- 🎯 **Purposeful** - Clear state communication
- 🛡️ **Accessible** - No motion conflicts, respects user preferences
