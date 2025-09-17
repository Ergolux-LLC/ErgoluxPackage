import type { RequestHandler } from "@sveltejs/kit";

const LOGIN_API_URL = process.env.LOGIN_API_URL || "http://localhost:8600/login";

export const POST: RequestHandler = async ({ request, cookies }) => {
    const formData = await request.formData();
    const email = formData.get("email");
    const password = formData.get("password");


    let apiResponse;
    try {
        apiResponse = await fetch(LOGIN_API_URL, {
            method: "POST",
            headers: { "content-type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ email: String(email), password: String(password) })
        });
    } catch (err) {
        console.error("[POST] Network error:", err);
        return new Response(JSON.stringify({ error: "Network error" }), {
            status: 502,
            headers: { "Content-Type": "application/json" }
        });
    }

    let data;
    try {
        data = await apiResponse.json();
    } catch (err) {
        console.error("[POST] Invalid JSON from backend:", err);
        return new Response(JSON.stringify({ error: "Invalid response from login API" }), {
            status: 502,
            headers: { "Content-Type": "application/json" }
        });
    }

    if (!apiResponse.ok) {
        console.warn("[POST] Backend login failed:", data.error || "Login failed");
        return new Response(JSON.stringify({ error: data.error || "Login failed" }), {
            status: apiResponse.status,
            headers: { "Content-Type": "application/json" }
        });
    }

    // Set the session cookie using access_token
    if (data.tokens && data.tokens.access_token) {
        cookies.set("sessionid", data.tokens.access_token, {
            path: "/",
            httpOnly: true,
            sameSite: "lax",
            secure: false,
            maxAge: 60 * 60 * 24,
            domain: ".app.ergolux.io.localhost"
        });
    } else {
        console.warn("[POST] No access_token returned from API.");
    }

    // Simulate workspace info for now
    const workspace = "workspace1";
    cookies.set("current_workspace", workspace, {
        path: "/",
        httpOnly: true,
        sameSite: "lax",
        secure: false,
        maxAge: 60 * 60 * 24,
        domain: ".app.ergolux.io.localhost"
    });

    return new Response(JSON.stringify({ success: true, workspace }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
    });
};