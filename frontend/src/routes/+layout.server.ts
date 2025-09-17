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

const APPROVED_WORKSPACES = ["workspace1"];
const PRIMARY_LOGIN_HOST = "app.ergolux.io.localhost"; // Change for production
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
    if (isPrimaryLogin(host)) {
        console.log("[shouldRedirectToLogin] Primary login host, no redirect.");
        return false;
    }
    if (pathname === "/login") {
        console.log("[shouldRedirectToLogin] /login always allowed, no redirect.");
        return false;
    }
    if (subdomain && !APPROVED_WORKSPACES.includes(subdomain)) {
        console.log("[shouldRedirectToLogin] Subdomain", subdomain, "not approved. Redirecting.");
        return true;
    }
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

function hasValidAuthCookie(event: RequestEvent): boolean {
    const refreshToken = event.cookies.get("refresh_token");
    const valid = !!refreshToken;
    console.log("[hasValidAuthCookie] refresh_token:", refreshToken ? "PRESENT" : "MISSING", "Valid:", valid);
    return valid;
}

function shouldCheckAuth(pathname: string): boolean {
    const result = pathname === "/directory" || pathname === "/dashboard";
    console.log("[shouldCheckAuth] Pathname:", pathname, "Should check auth:", result);
    return result;
}

export const load: LayoutServerLoad = async (event) => {
    const { locals, request, url } = event;
    const host = request.headers.get("host") || "";
    const subdomain = getSubdomain(host);

    console.log("[load] Host:", host, "Subdomain:", subdomain, "Pathname:", url.pathname);

    if (shouldRedirectToLogin(subdomain, host, url.pathname)) {
        console.log("[load] Redirecting to PRIMARY_LOGIN_URL:", PRIMARY_LOGIN_URL + "/login");
        throw redirect(302, PRIMARY_LOGIN_URL + "/login");
    }

    if (shouldCheckAuth(url.pathname)) {
        if (!hasValidAuthCookie(event)) {
            console.log("[load] No valid auth cookie. Redirecting to /login.");
            throw redirect(302, "/login");
        }
    }

    const access = getWorkspaceAccess(subdomain);
    locals.workspace = subdomain ?? "";

    console.log("[load] Returning access info:", access, "User:", locals.user);

    return {
        ...access,
        user: locals.user,
    };
};
