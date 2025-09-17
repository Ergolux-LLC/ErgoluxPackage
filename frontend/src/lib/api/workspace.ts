/**
 * Workspace API Client
 * 
 * This module provides functions for interacting with the Workspace API endpoints
 * through the BFF (Backend For Frontend) service.
 */

// Import shared API configuration
import { API_BASE_URL, DEFAULT_HEADERS, generateRequestId } from './config';

/**
 * Interface for Workspace object
 */
export interface Workspace {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  ownerId?: string;
  members?: WorkspaceMember[];
  settings?: WorkspaceSettings;
}

/**
 * Interface for Workspace Member
 */
export interface WorkspaceMember {
  id: string;
  userId: string;
  workspaceId: string;
  role: 'owner' | 'admin' | 'member' | 'guest';
  email?: string;
  name?: string;
  joinedAt: string;
}

/**
 * Interface for Workspace Settings
 */
export interface WorkspaceSettings {
  logo?: string;
  theme?: 'light' | 'dark' | 'system';
  features?: Record<string, boolean>;
  customization?: Record<string, any>;
}

/**
 * Interface for workspace search results
 */
export interface WorkspaceSearchResult {
  workspaces: Workspace[];
  total: number;
  page: number;
  limit: number;
}

/**
 * Interface for workspace name availability result
 */
export interface WorkspaceAvailabilityResult {
  workspaceName: string;
  available: boolean;
  message?: string;
}

/**
 * Interface for workspace creation parameters
 */
export interface CreateWorkspaceParams {
  name: string;
  companyName?: string;
  teamSize?: number;
}

/**
 * Interface for workspace creation response
 */
export interface CreateWorkspaceResult {
  workspace: Workspace | null;
  success: boolean;
  message?: string;
}

/**
 * Check if a workspace name is available
 * 
 * @param name - The workspace name to check
 * @returns Promise resolving to the availability result
 */
export async function checkWorkspaceAvailability(name: string): Promise<WorkspaceAvailabilityResult> {
  try {
    if (!name || name.trim().length < 3) {
      return {
        workspaceName: name,
        available: false,
        message: 'Workspace name must be at least 3 characters'
      };
    }

    // Construct the URL as a string to avoid recursion issues with SvelteKit's server fetch
    const searchUrl = `${API_BASE_URL}/workspaces?name=${encodeURIComponent(name)}`;

    console.log(`Checking workspace name availability: "${name}"`);
    console.log(`Search URL: ${searchUrl}`);

    const response = await fetch(searchUrl, {
      method: 'GET',
      headers: DEFAULT_HEADERS,
      credentials: 'include'
    });

    console.log(`Workspace search response status: ${response.status}`);

    // 404 means no workspace with this name was found - it's available
    if (response.status === 404) {
      return {
        workspaceName: name,
        available: true,
        message: `Workspace name "${name}" is available!`
      };
    }

    const responseText = await response.text();
    
    // Try to parse the response as JSON
    let data;
    try {
      if (responseText && responseText.trim()) {
        data = JSON.parse(responseText);
      }
    } catch (e) {
      console.error('Failed to parse workspace search response:', e);
    }

    if (response.ok) {
      // Check if we got any results (workspaces with this name)
      const workspaces = data?.workspaces || data?.items || data?.results || [];
      const isAvailable = workspaces.length === 0;

      return {
        workspaceName: name,
        available: isAvailable,
        message: isAvailable 
          ? `Workspace name "${name}" is available!` 
          : `The workspace name "${name}" is already taken.`
      };
    } else {
      // Handle error response
      throw new Error(`Failed to check workspace name: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error checking workspace name:', error);
    return {
      workspaceName: name,
      available: false,
      message: `Error checking workspace name: ${error instanceof Error ? error.message : 'Unknown error'}`
    };
  }
}

/**
 * Create a new workspace
 * 
 * @param params - Workspace creation parameters
 * @returns Promise resolving to the created workspace
 */
export async function createWorkspace(params: CreateWorkspaceParams): Promise<CreateWorkspaceResult> {
  try {
    const { name, companyName, teamSize } = params;
    
    // Basic validation
    if (!name || name.trim().length < 3) {
      throw new Error('Workspace name must be at least 3 characters');
    }

    // First check if the workspace name is available
    const availabilityCheck = await checkWorkspaceAvailability(name);
    if (!availabilityCheck.available) {
      throw new Error(availabilityCheck.message || 'Workspace name is not available');
    }

    // Create the workspace
    const createUrl = `${API_BASE_URL}/workspaces`;
    
    const requestBody = JSON.stringify({
      name,
      companyName: companyName || name,
      teamSize: teamSize || 1
    });

    console.log(`Creating workspace "${name}"`);
    console.log(`Request URL: ${createUrl}`);

    const response = await fetch(createUrl, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: requestBody,
      credentials: 'include'
    });

    console.log(`Workspace creation response status: ${response.status}`);

    const responseText = await response.text();
    
    // Try to parse the response as JSON
    let data;
    try {
      if (responseText && responseText.trim()) {
        data = JSON.parse(responseText);
      }
    } catch (e) {
      console.error('Failed to parse workspace creation response:', e);
      throw new Error(`Invalid response from server: ${responseText.substring(0, 100)}`);
    }

    if (response.ok) {
      return {
        workspace: data,
        success: true,
        message: 'Workspace created successfully!'
      };
    } else {
      // Handle error response
      throw new Error(data?.message || `Failed to create workspace: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error creating workspace:', error);
    return {
      workspace: null,
      success: false,
      message: `Failed to create workspace: ${error instanceof Error ? error.message : 'Unknown error'}`
    };
  }
}

/**
 * Get a workspace by ID
 * 
 * @param id - The workspace ID
 * @returns Promise resolving to the workspace
 */
export async function getWorkspace(id: string): Promise<Workspace> {
  const url = `${API_BASE_URL}/workspaces/${id}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: DEFAULT_HEADERS,
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error(`Failed to get workspace: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all workspaces the current user has access to
 * 
 * @returns Promise resolving to an array of workspaces
 */
export async function getUserWorkspaces(): Promise<Workspace[]> {
  const url = `${API_BASE_URL}/workspaces/user`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: DEFAULT_HEADERS,
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error(`Failed to get user workspaces: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.workspaces || [];
}

/**
 * Search for workspaces by name
 * 
 * @param query - Search query parameters
 * @returns Promise resolving to search results
 */
export async function searchWorkspaces(query: string): Promise<WorkspaceSearchResult> {
  // Use string URL instead of URL object to avoid recursion issues
  const searchUrl = query 
    ? `${API_BASE_URL}/workspaces?name=${encodeURIComponent(query)}`
    : `${API_BASE_URL}/workspaces`;
  
  const response = await fetch(searchUrl, {
    method: 'GET',
    headers: DEFAULT_HEADERS,
    credentials: 'include'
  });

  if (!response.ok) {
    throw new Error(`Workspace search failed: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}
