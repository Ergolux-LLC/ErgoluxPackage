export type AppDef = {
  id: string;
  name: string;
  icon: string; // bootstrap icon class, e.g. "bi-house"
  href?: string; // optional link target
  // explicit hex colors (do NOT rely on CSS variables)
  color?: string;     // icon color (hex)
  triggerBg?: string; // background/plate hover color (hex)
};

const APPS: AppDef[] = [
  { id: "analyze",  name: "Analyze",  icon: "bi-bar-chart",  href: "/analyze",  color: "#4DD0E1", triggerBg: "#2AA8B4" },
  { id: "plan",     name: "Plan",     icon: "bi-kanban",     href: "/plan",     color: "#FFD54F", triggerBg: "#D4A02B" },
  { id: "create",   name: "Create",   icon: "bi-plus-circle",href: "/create",   color: "#7BD389", triggerBg: "#4FA763" },
  { id: "operate",  name: "Operate",  icon: "bi-gear",       href: "/operate",  color: "#90CAF9", triggerBg: "#5A9CD8" },
  { id: "promote",  name: "Promote",  icon: "bi-megaphone",  href: "/promote",  color: "#FF8A65", triggerBg: "#E06A4E" },
  { id: "procure",  name: "Procure",  icon: "bi-cart3",      href: "/procure",  color: "#A1887F", triggerBg: "#7A5F50" },
  { id: "support",  name: "Support",  icon: "bi-headset",    href: "/support",  color: "#B39DDB", triggerBg: "#8F6FCE" },
  { id: "research", name: "Research", icon: "bi-search",      href: "/research", color: "#F48FB1", triggerBg: "#D46A8E" },
  { id: "educate",  name: "Educate",  icon: "bi-book",        href: "/educate",  color: "#FFF59D", triggerBg: "#E0CF6A" },
  { id: "review",   name: "Review",   icon: "bi-eye",         href: "/review",   color: "#80CBC4", triggerBg: "#4FAF95" },
  { id: "secure",   name: "Secure",   icon: "bi-shield-lock", href: "/secure",   color: "#F06292", triggerBg: "#D14B78" }
];

export default APPS;