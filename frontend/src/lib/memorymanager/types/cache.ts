/**
 * Cache-related type definitions for memory manager
 */

export interface CacheEntry<T = any> {
  key: string;
  data: T;
  expiry: number;
  tags: string[];
  version: number;
}

export interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  totalSize: number;
}

export interface CacheOptions {
  ttl?: number;
  priority?: number;
  tags?: string[];
  encrypt?: boolean;
}