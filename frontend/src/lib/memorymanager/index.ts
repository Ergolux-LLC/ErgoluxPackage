/**
 * Main Memory Manager class that orchestrates all caching operations
 * Entry point for memory management functionality
 */

import { userCache } from './cache';
import { localStorageManager } from './storage';
import type { UserProfile, WorkspaceSettings, CacheOptions } from './types';

export class MemoryManager {
  /**
   * Initialize user data after successful login
   */
  onLoginSuccess(loginResponse: any): void {
    console.log('MemoryManager: Processing login success');
    
    // Store user profile data from login response
    if (loginResponse.user) {
      userCache.storeUserProfile(loginResponse.user);
    }

    // If workspace info is provided, store it
    if (loginResponse.workspace) {
      const workspaceSettings: WorkspaceSettings = {
        current_workspace: loginResponse.workspace.id,
        layout_preferences: loginResponse.workspace.preferences || {},
        quick_access_contacts: []
      };
      userCache.storeWorkspaceSettings(workspaceSettings);
    }
  }

  /**
   * Handle user logout - clear all cached data
   */
  onLogout(): void {
    console.log('MemoryManager: Clearing all user data');
    userCache.clearUserData();
  }

  /**
   * Get current user profile
   */
  getCurrentUser(): UserProfile | null {
    return userCache.getUserProfile();
  }

  /**
   * Get individual user field instantly (sub-millisecond access)
   */
  getUserField(field: keyof UserProfile): string | null {
    return userCache.getUserField(field);
  }

  /**
   * Get user's full name instantly
   */
  getUserFullName(): string | null {
    return userCache.getUserFullName();
  }

  /**
   * Get user email instantly
   */
  getUserEmail(): string | null {
    return userCache.getUserEmail();
  }

  /**
   * Get user ID instantly
   */
  getUserId(): string | null {
    return userCache.getUserId();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return userCache.isAuthenticated();
  }

  /**
   * Update user profile data
   */
  updateUserProfile(updates: Partial<UserProfile>): void {
    userCache.updateUserProfile(updates);
  }

  /**
   * Get memory manager status for debugging
   */
  getStatus(): {
    authenticated: boolean;
    userProfile: UserProfile | null;
    storageUsage: { used: number; percentage: number };
    cacheHealth: any;
  } {
    return {
      authenticated: this.isAuthenticated(),
      userProfile: this.getCurrentUser(),
      storageUsage: localStorageManager.getStorageUsage(),
      cacheHealth: userCache.getCacheStatus()
    };
  }

  /**
   * Initialize memory manager (called on app startup)
   */
  initialize(): void {
    console.log('MemoryManager: Initializing...');
    
    // Log current status
    const status = this.getStatus();
    console.log('MemoryManager: Current status:', status);
    
    // Check storage health
    if (status.storageUsage.percentage > 80) {
      console.warn('MemoryManager: Storage usage high:', status.storageUsage.percentage + '%');
    }
  }
}

// Export singleton instance
export const memoryManager = new MemoryManager();

// Re-export types for convenience
export type { UserProfile, WorkspaceSettings, CacheOptions } from './types';