/**
 * Account popup state and data management
 */

import { writable } from 'svelte/store';
import { memoryManager } from '$lib/memorymanager';

export const accountData = writable({
  id: '',
  firstName: '',
  lastName: '',
  email: '',
  lastSync: '',
  preferences: {}
});

export function loadAccountData() {
  const user = memoryManager.getCurrentUser();
  if (user) {
    accountData.set({
      id: user.id,
      firstName: user.first_name,
      lastName: user.last_name,
      email: user.email,
      lastSync: user.last_sync || '',
      preferences: user.preferences || {}
    });
  }
}

export function refreshAccountData() {
  loadAccountData();
}