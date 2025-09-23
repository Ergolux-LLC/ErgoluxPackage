/**
 * Shared state management for navbar popups
 */

import { writable } from 'svelte/store';
import type { PopupState } from './popup.types';

export const popupState = writable<PopupState>({
  account: { 
    isOpen: false, 
    activeTab: 'profile' 
  },
  profile: { 
    isOpen: false, 
    isEditing: false 
  },
  help: { 
    isOpen: false, 
    searchTerm: '', 
    activeCategory: null 
  }
});

export function openPopup(popup: keyof PopupState) {
  popupState.update(state => {
    // Close all other popups
    Object.keys(state).forEach(key => {
      state[key as keyof PopupState].isOpen = false;
    });
    // Open the requested popup
    state[popup].isOpen = true;
    return state;
  });
}

export function closeAllPopups() {
  popupState.update(state => {
    Object.keys(state).forEach(key => {
      state[key as keyof PopupState].isOpen = false;
    });
    return state;
  });
}

export function setAccountTab(tab: PopupState['account']['activeTab']) {
  popupState.update(state => {
    state.account.activeTab = tab;
    return state;
  });
}