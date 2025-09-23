/**
 * localStorage operations for user profile and settings data
 * Handles key-value storage with validation and size monitoring
 */

import { browser } from '$app/environment';
import type { StorageItem, UserProfile, WorkspaceSettings } from '../types';

export class LocalStorageManager {
  private readonly maxSize = 8 * 1024 * 1024; // 8MB limit
  private readonly keyPrefix = 'ergolux_';

  /**
   * Store user profile as individual key-value pairs for maximum speed
   */
  storeUserProfile(profile: UserProfile): void {
    try {
      const timestamp = Date.now();
      const ttl = 24 * 60 * 60 * 1000; // 24 hours
      
      // Store each field as individual key for instant access
      localStorage.setItem('user_id', profile.id);
      localStorage.setItem('user_first_name', profile.first_name);
      localStorage.setItem('user_last_name', profile.last_name);
      localStorage.setItem('user_email', profile.email);
      localStorage.setItem('user_preferences', JSON.stringify(profile.preferences || {}));
      localStorage.setItem('user_last_sync', profile.last_sync || new Date().toISOString());
      localStorage.setItem('user_timestamp', timestamp.toString());
      localStorage.setItem('user_ttl', (timestamp + ttl).toString());
      
      console.log('MemoryManager: User profile stored as individual keys');
    } catch (error) {
      this.handleStorageError();
    }
  }

  /**
   * Get user profile by combining individual keys (still very fast)
   */
  getUserProfile(): UserProfile | null {
    try {
      // Check if user data exists and is not expired
      const ttl = localStorage.getItem('user_ttl');
      if (!ttl || Date.now() > parseInt(ttl)) {
        this.clearUserProfile();
        return null;
      }

      const id = localStorage.getItem('user_id');
      if (!id) return null;

      // Combine individual keys into profile object
      return {
        id,
        first_name: localStorage.getItem('user_first_name') || '',
        last_name: localStorage.getItem('user_last_name') || '',
        email: localStorage.getItem('user_email') || '',
        preferences: JSON.parse(localStorage.getItem('user_preferences') || '{}'),
        last_sync: localStorage.getItem('user_last_sync') || new Date().toISOString()
      };
    } catch (error) {
      this.handleStorageError();
      return null;
    }
  }

  /**
   * Get individual user field for instant access (sub-millisecond)
   */
  getUserField(field: keyof UserProfile): string | null {
    try {
      // Check TTL first
      const ttl = localStorage.getItem('user_ttl');
      if (!ttl || Date.now() > parseInt(ttl)) {
        return null;
      }

      return localStorage.getItem(`user_${field}`);
    } catch (error) {
      console.error(`Error getting user field ${field}:`, error);
      return null;
    }
  }

  /**
   * Clear all user profile keys
   */
  clearUserProfile(): void {
    try {
      const userKeys = [
        'user_id', 'user_first_name', 'user_last_name', 
        'user_email', 'user_preferences', 'user_last_sync',
        'user_timestamp', 'user_ttl'
      ];
      
      userKeys.forEach(key => localStorage.removeItem(key));
      console.log('MemoryManager: User profile keys cleared');
    } catch (error) {
      console.error('Error clearing user profile:', error);
    }
  }

  /**
   * Store workspace settings
   */
  storeWorkspaceSettings(settings: WorkspaceSettings): void {
    if (!browser) return;

    const storageItem: StorageItem<WorkspaceSettings> = {
      data: settings,
      timestamp: Date.now(),
      priority: 2,
      lastAccessed: Date.now(),
      size: this.getDataSize(settings),
      ttl: 7 * 24 * 60 * 60 * 1000, // 7 days
      version: 1
    };

    try {
      localStorage.setItem(
        `${this.keyPrefix}workspace_settings`,
        JSON.stringify(storageItem)
      );
    } catch (error) {
      console.error('Failed to store workspace settings:', error);
      this.handleStorageError();
    }
  }

  /**
   * Retrieve workspace settings
   */
  getWorkspaceSettings(): WorkspaceSettings | null {
    if (!browser) return null;

    try {
      const stored = localStorage.getItem(`${this.keyPrefix}workspace_settings`);
      if (!stored) return null;

      const storageItem: StorageItem<WorkspaceSettings> = JSON.parse(stored);
      
      if (this.isExpired(storageItem)) {
        localStorage.removeItem(`${this.keyPrefix}workspace_settings`);
        return null;
      }

      storageItem.lastAccessed = Date.now();
      localStorage.setItem(
        `${this.keyPrefix}workspace_settings`,
        JSON.stringify(storageItem)
      );

      return storageItem.data;
    } catch (error) {
      console.error('Failed to retrieve workspace settings:', error);
      return null;
    }
  }

  /**
   * Clear all user data (for logout)
   */
  clearUserData(): void {
    if (!browser) return;

    // Clear prefixed keys
    const keys = Object.keys(localStorage).filter(key => 
      key.startsWith(this.keyPrefix)
    );

    keys.forEach(key => {
      localStorage.removeItem(key);
    });

    // Clear individual user profile keys
    this.clearUserProfile();
  }

  /**
   * Get current storage usage
   */
  getStorageUsage(): { used: number; percentage: number } {
    if (!browser) return { used: 0, percentage: 0 };

    let used = 0;
    const keys = Object.keys(localStorage).filter(key => 
      key.startsWith(this.keyPrefix)
    );

    keys.forEach(key => {
      const value = localStorage.getItem(key);
      if (value) {
        used += key.length + value.length;
      }
    });

    return {
      used,
      percentage: (used / this.maxSize) * 100
    };
  }

  /**
   * Check if storage item is expired
   */
  private isExpired(item: StorageItem): boolean {
    if (!item.ttl) return false;
    return Date.now() - item.timestamp > item.ttl;
  }

  /**
   * Calculate data size in bytes
   */
  private getDataSize(data: any): number {
    return new Blob([JSON.stringify(data)]).size;
  }

  /**
   * Handle storage quota exceeded errors
   */
  private handleStorageError(): void {
    console.warn('localStorage quota exceeded, clearing old data');
    
    // Get all ergolux items sorted by priority and last accessed
    const items = Object.keys(localStorage)
      .filter(key => key.startsWith(this.keyPrefix))
      .map(key => {
        const value = localStorage.getItem(key);
        if (!value) return null;
        
        try {
          const parsed: StorageItem = JSON.parse(value);
          return { key, item: parsed };
        } catch {
          return null;
        }
      })
      .filter(Boolean)
      .sort((a, b) => {
        // Sort by priority (higher first) then by last accessed (older first)
        if (a!.item.priority !== b!.item.priority) {
          return b!.item.priority - a!.item.priority;
        }
        return a!.item.lastAccessed - b!.item.lastAccessed;
      });

    // Remove items until we have space (keep high priority items)
    const currentUsage = this.getStorageUsage();
    if (currentUsage.percentage > 80) {
      // Remove lowest priority, oldest items
      const itemsToRemove = items.slice(-Math.ceil(items.length * 0.3));
      itemsToRemove.forEach(item => {
        if (item && item.item.priority > 2) { // Don't remove critical user data
          localStorage.removeItem(item.key);
        }
      });
    }
  }
}

// Export singleton instance
export const localStorageManager = new LocalStorageManager();