/// <reference types="@sveltejs/kit" />

declare namespace App {
    interface Locals {
        user: any | null;
        workspace: string;
        lastWorkspace?: string;
    }
}

import { redirect, type RequestEvent } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";


// Allow all subdomains and root for local development
const APPROVED_WORKSPACES: string[] = [];
const PRIMARY_LOGIN_HOST = "app.ergolux.io.localhost";
const PRIMARY_LOGIN_URL = `http://${PRIMARY_LOGIN_HOST}:5173`;

function getSubdomain(host: string): string | null {
    const hostWithoutPort = host.split(":")[0];
    const parts = hostWithoutPort.split(".");
    // For dev: workspace.app.ergolux.io.localhost (5+ parts), for prod: workspace.app.ergolux.io (4 parts)
    if (parts.length > 4) {
        // e.g. workspace2.app.ergolux.io.localhost
        console.log("[getSubdomain] Extracted subdomain:", parts[0]);
        return parts[0];
    } else if (parts.length === 4 && parts[1] === "app") {
        // e.g. workspace2.app.ergolux.io (prod)
        console.log("[getSubdomain] Extracted subdomain:", parts[0]);
        return parts[0];
    } else {
        console.log("[getSubdomain] No subdomain detected.");
        return null;
    }
}

function isPrimaryLogin(host: string): boolean {
    const result = host === PRIMARY_LOGIN_HOST;
    console.log("[isPrimaryLogin] Host:", host, "Is primary login:", result);
    return result;
}

function shouldRedirectToLogin(subdomain: string | null, host: string, pathname: string): boolean {
    // Only redirect if on a subdomain that is explicitly not allowed (never for root)
    // For local dev, allow all subdomains and root
    if (pathname === "/login") {
        console.log("[shouldRedirectToLogin] /login always allowed, no redirect.");
        return false;
    }
    // No redirect for root or any subdomain in dev
    console.log("[shouldRedirectToLogin] No redirect needed.");
    return false;
}

function getWorkspaceAccess(subdomain: string | null) {
    const isAllowed = !subdomain || APPROVED_WORKSPACES.includes(subdomain);
    console.log("[getWorkspaceAccess] Subdomain:", subdomain, "Is allowed:", isAllowed);
    return {
        workspace: subdomain,
        isAllowed,
        subdomain
    };
}


export const load: LayoutServerLoad = async (event) => {
    const { locals, request, url, cookies } = event;
    const host = request.headers.get("host") || "";
    const subdomain = getSubdomain(host);
    const access = getWorkspaceAccess(subdomain);
    locals.workspace = subdomain ?? "";
    return {
        ...access,
        user: locals.user,
    };
};
