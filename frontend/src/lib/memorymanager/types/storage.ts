/**
 * Storage-related type definitions for memory manager
 */

export interface StorageItem<T = any> {
  data: T;
  timestamp: number;
  priority: number;
  lastAccessed: number;
  size: number;
  ttl?: number;
  version: number;
}

export interface UserProfile {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  preferences?: Record<string, any>;
  last_sync: string;
}

export interface WorkspaceSettings {
  current_workspace?: string;
  layout_preferences?: Record<string, any>;
  quick_access_contacts?: string[];
}

export interface StorageQuota {
  used: number;
  available: number;
  quota: number;
}

export interface EncryptionConfig {
  enabled: boolean;
  keyId: string;
  algorithm: string;
}