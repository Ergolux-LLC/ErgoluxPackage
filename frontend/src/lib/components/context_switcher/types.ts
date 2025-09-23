/**
 * Types for the Context Switcher component
 */

export interface SubApp {
  id: string;
  label: string;
  icon: string;
  color: string;
  href?: string;
  disabled?: boolean;
}

export type SubAppId = 
  | 'discover'
  | 'qualify' 
  | 'nurture'
  | 'commit'
  | 'onboard'
  | 'support'
  | 'expand'
  | 'renew'
  | 'advocate';

export interface ContextSwitcherProps {
  activeSubApp?: SubAppId;
  onSubAppChange?: (subApp: SubApp) => void;
}