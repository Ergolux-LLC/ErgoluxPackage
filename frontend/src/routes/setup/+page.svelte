<script lang="ts">
  import SetupDialog from "$lib/components/SetupDialog.svelte";
  import { apiClient } from "$lib/api/client";
  import { config, shouldLog } from "$lib/config/environment";
  import "./setup.css";

  // Helper function to log client-side events
  function logClient(event: string, data: any) {
    if (!shouldLog()) return;
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [CLIENT] [SETUP] [${event}]`, data);
  }

  // API function to check activation code
  async function apiCheckCode(code: string) {
    logClient("CheckCode", { code });

    try {
      const result = await apiClient.confirmCode(code);
      logClient("CheckCodeResponse", result);
      console.log("[SETUP PAGE] confirmCode raw result:", result);

      // The API client already transforms the response, so check for result.valid
      if (result.valid === true) {
        const returnValue = {
          valid: true,
          email: result.email,
          workspace_id: result.workspace_id,
        };
        console.log("[SETUP PAGE] Returning valid result:", returnValue);
        return returnValue;
      } else {
        const returnValue = {
          valid: false,
          error: result.error || "Invalid code",
        };
        console.log("[SETUP PAGE] Returning invalid result:", returnValue);
        return returnValue;
      }
    } catch (error) {
      logClient("CheckCodeError", error);
      console.error("[SETUP PAGE] Exception in apiCheckCode:", error);
      return { valid: false, error: "Failed to validate code" };
    }
  }

  // Get code from query params if available
  let code = "";
  if (typeof window !== "undefined") {
    const params = new URLSearchParams(window.location.search);
    code = params.get("code") || "";

    logClient("PageInit", {
      url: window.location.href,
      code: code ? "[PRESENT]" : "[MISSING]",
      config: config.app,
    });
  }
</script>

<SetupDialog {code} {apiCheckCode} />
