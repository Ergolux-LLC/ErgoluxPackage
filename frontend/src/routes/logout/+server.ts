import type { RequestHandler } from "@sveltejs/kit";

export const GET: RequestHandler = async ({ cookies }) => {
    cookies.delete("sessionid", { path: "/" });
    return new Response(null, {
        status: 302,
        headers: { Location: "/logout" }
    });
};