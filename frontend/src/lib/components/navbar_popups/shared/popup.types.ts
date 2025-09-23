/**
 * Shared types for navbar popups
 */

export interface PopupState {
  account: {
    isOpen: boolean;
    activeTab: 'profile' | 'settings' | 'billing' | 'security';
  };
  profile: {
    isOpen: boolean;
    isEditing: boolean;
  };
  help: {
    isOpen: boolean;
    searchTerm: string;
    activeCategory: string | null;
  };
}

export interface PopupProps {
  onClose?: () => void;
}