/**
 * User profile data cache with automatic storage management
 * Handles user authentication status and personal settings
 */

import { localStorageManager } from '../storage';
import type { UserProfile, WorkspaceSettings, CacheOptions } from '../types';

export class UserCache {
  private readonly defaultTTL = 24 * 60 * 60 * 1000; // 24 hours

  /**
   * Store user profile after login
   */
  storeUserProfile(userData: any, options: CacheOptions = {}): void {
    // Transform API response to our UserProfile format
    const userProfile: UserProfile = {
      id: userData.id || userData.user_id,
      first_name: userData.first_name || userData.name?.split(' ')[0] || '',
      last_name: userData.last_name || userData.name?.split(' ')[1] || '',
      email: userData.email,
      preferences: userData.preferences || {},
      last_sync: new Date().toISOString()
    };

    localStorageManager.storeUserProfile(userProfile);
    console.log('User profile cached:', userProfile.email);
  }

  /**
   * Get user profile (combines individual keys)
   */
  getUserProfile(): UserProfile | null {
    return localStorageManager.getUserProfile();
  }

  /**
   * Get individual user field for instant access (sub-millisecond)
   */
  getUserField(field: keyof UserProfile): string | null {
    return localStorageManager.getUserField(field);
  }

  /**
   * Get user's full name instantly
   */
  getUserFullName(): string | null {
    const firstName = this.getUserField('first_name');
    const lastName = this.getUserField('last_name');
    
    if (!firstName && !lastName) return null;
    return `${firstName || ''} ${lastName || ''}`.trim();
  }

  /**
   * Get user email instantly
   */
  getUserEmail(): string | null {
    return this.getUserField('email');
  }

  /**
   * Get user ID instantly
   */
  getUserId(): string | null {
    return this.getUserField('id');
  }

  /**
   * Update user profile partially
   */
  updateUserProfile(updates: Partial<UserProfile>): void {
    const currentProfile = this.getUserProfile();
    if (!currentProfile) return;

    const updatedProfile: UserProfile = {
      ...currentProfile,
      ...updates,
      last_sync: new Date().toISOString()
    };

    localStorageManager.storeUserProfile(updatedProfile);
  }

  /**
   * Store workspace settings
   */
  storeWorkspaceSettings(settings: WorkspaceSettings): void {
    localStorageManager.storeWorkspaceSettings(settings);
  }

  /**
   * Get workspace settings
   */
  getWorkspaceSettings(): WorkspaceSettings | null {
    return localStorageManager.getWorkspaceSettings();
  }

  /**
   * Check if user is authenticated based on cached data
   */
  isAuthenticated(): boolean {
    const userId = this.getUserId();
    return userId !== null && userId !== '';
  }

  /**
   * Get current user ID (instant access)
   */
  getCurrentUserId(): string | null {
    return this.getUserId();
  }

  /**
   * Clear all user data (for logout)
   */
  clearUserData(): void {
    localStorageManager.clearUserData();
    console.log('User data cleared from cache');
  }

  /**
   * Get cache health status
   */
  getCacheStatus(): {
    hasUserProfile: boolean;
    lastSync: string | null;
    storageUsage: { used: number; percentage: number };
  } {
    const profile = this.getUserProfile();
    const usage = localStorageManager.getStorageUsage();

    return {
      hasUserProfile: profile !== null,
      lastSync: profile?.last_sync || null,
      storageUsage: usage
    };
  }
}

// Export singleton instance
export const userCache = new UserCache();