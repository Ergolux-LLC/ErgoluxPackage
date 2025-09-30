// Sparkler animation logic for ContextSwitcher
// Extracted from ContextSwitcher.svelte.backup

export type SparkleIntensity = "low" | "medium" | "high";

export function startSparkler({
  getActiveButton,
  sparkleIntensity = "medium",
  isExpanded = () => false,
  hasNewAccess = false,
  enableSparkler = false,
}: {
  getActiveButton: () => HTMLElement | null;
  sparkleIntensity?: SparkleIntensity;
  isExpanded?: () => boolean;
  hasNewAccess?: boolean;
  enableSparkler?: boolean;
}) {
  if (!hasNewAccess || !enableSparkler) return;
  let sparklerActive = true;
  const sparklerInterval = setInterval(() => {
    if (!sparklerActive || isExpanded()) {
      clearInterval(sparklerInterval);
      return;
    }
    createSparklerBurst(getActiveButton(), sparkleIntensity);
  }, 300);
  (window as any).sparklerInterval = sparklerInterval;
  return () => {
    sparklerActive = false;
    clearInterval(sparklerInterval);
    (window as any).sparklerInterval = null;
  };
}

export function createSparklerBurst(
  container: HTMLElement | null,
  sparkleIntensity: SparkleIntensity = "medium"
) {
  if (!container) return;
  const rect = container.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const particleCount =
    sparkleIntensity === "low" ? 15 : sparkleIntensity === "medium" ? 25 : 35;
  for (let i = 0; i < particleCount; i++) {
    createSparkleParticle(centerX, centerY, i, particleCount);
  }
}

function createSparkleParticle(
  centerX: number,
  centerY: number,
  index: number,
  total: number
) {
  setTimeout(() => {
    const particle = document.createElement("div");
    particle.className = "sparkle-particle";
    const goldenColors = [
      "#FFD700", "#FFA500", "#FF8C00", "#FFB347", "#FFDF00", "#FFCC00", "#FFF700", "#F4C430",
    ];
    const baseAngle = 90;
    const spreadAngle = 70;
    const angle = baseAngle + (Math.random() - 0.5) * spreadAngle;
    const initialVelocity = 1200 + Math.random() * 800;
    const gravity = 1500;
    const lifetime = 4000 + Math.random() * 2000;
    const startX = centerX + (Math.random() - 0.5) * 20;
    const startY = centerY + (Math.random() - 0.5) * 10;
    particle.style.left = startX + "px";
    particle.style.top = startY + "px";
    const color = goldenColors[Math.floor(Math.random() * goldenColors.length)];
    particle.style.background = color;
    particle.style.boxShadow = `0 0 4px ${color}, 0 0 8px ${color}40`;
    const radians = (angle * Math.PI) / 180;
    const velocityX = Math.sin(radians) * initialVelocity;
    const velocityY = Math.cos(radians) * initialVelocity;
    particle.style.setProperty("--velocity-x", velocityX + "px");
    particle.style.setProperty("--velocity-y", velocityY + "px");
    particle.style.setProperty("--gravity", gravity + "px");
    particle.style.setProperty("--lifetime", lifetime + "ms");
    document.body.appendChild(particle);
    setTimeout(() => {
      if (particle.parentNode) particle.remove();
    }, lifetime);
    setTimeout(() => {
      if (particle.parentNode) {
        const rect = particle.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        if (
          rect.top > viewportHeight + 200 ||
          rect.left < -200 ||
          rect.left > viewportWidth + 200
        ) {
          particle.remove();
        }
      }
    }, lifetime / 2);
  }, index * 20);
}
