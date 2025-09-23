#!/usr/bin/env node

/**
 * Frontend Workspace Route Authentication Test
 *
 * This script tests the complete workspace authentication flow in the browser:
 * 1. Navigates to workspace page (should show access denied)
 * 2. Performs login via API
 * 3. Navigates to workspace page again (should now show authenticated content)
 * 4. Tests refresh token functionality on workspace page
 */

const http = require("http");
const { URL } = require("url");

// Configuration
const FRONTEND_BASE = "http://localhost:5173";
const TEST_USER = {
  email: "dev@example.com",
  password: "devpassword123",
};

// Test configuration
const DEFAULT_WORKSPACE_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";

/**
 * Make HTTP request with proper error handling
 */
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);

    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === "https:" ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || "GET",
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "WorkspaceTest/1.0",
        ...options.headers,
      },
    };

    const req = http.request(requestOptions, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const result = {
            statusCode: res.statusCode,
            headers: res.headers,
            data: data,
          };

          // Try to parse JSON if content type suggests it
          const contentType = res.headers["content-type"] || "";
          if (contentType.includes("application/json") && data.trim()) {
            try {
              result.json = JSON.parse(data);
            } catch (e) {
              // Not valid JSON, keep as string
            }
          }

          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
    });

    req.on("error", (error) => {
      reject(new Error(`Request failed: ${error.message}`));
    });

    req.on("timeout", () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });

    if (options.body) {
      req.write(
        typeof options.body === "string"
          ? options.body
          : JSON.stringify(options.body)
      );
    }

    req.setTimeout(10000); // 10 second timeout
    req.end();
  });
}

/**
 * Extract cookies from response headers
 */
function extractCookies(headers) {
  const setCookieHeader = headers["set-cookie"];
  if (!setCookieHeader) return {};

  const cookies = {};
  setCookieHeader.forEach((cookie) => {
    const [nameValue] = cookie.split(";");
    const [name, value] = nameValue.split("=");
    if (name && value) {
      cookies[name.trim()] = value.trim();
    }
  });
  return cookies;
}

/**
 * Format cookies for Cookie header
 */
function formatCookies(cookies) {
  return Object.entries(cookies)
    .map(([name, value]) => `${name}=${value}`)
    .join("; ");
}

/**
 * Test workspace page before authentication
 */
async function testWorkspaceUnauthenticated() {
  console.log("\n🔍 Testing workspace page (unauthenticated)...");

  try {
    const response = await makeRequest(`${FRONTEND_BASE}/workspace`);

    if (
      response.statusCode === 200 &&
      response.data.includes("Access Denied")
    ) {
      console.log(
        "✅ PASS: Workspace correctly shows access denied for unauthenticated users"
      );
      return true;
    } else {
      console.log(
        `❌ FAIL: Expected access denied page, got status ${response.statusCode}`
      );
      console.log(`Response preview: ${response.data.substring(0, 200)}...`);
      return false;
    }
  } catch (error) {
    console.log(
      `❌ FAIL: Error testing unauthenticated workspace: ${error.message}`
    );
    return false;
  }
}

/**
 * Perform login via API
 */
async function performLogin() {
  console.log("\n🔐 Performing login...");

  try {
    const loginResponse = await makeRequest(`${FRONTEND_BASE}/api/auth/login`, {
      method: "POST",
      body: {
        email: TEST_USER.email,
        password: TEST_USER.password,
        workspace_id: DEFAULT_WORKSPACE_ID,
      },
    });

    if (loginResponse.statusCode !== 200) {
      throw new Error(
        `Login failed with status ${loginResponse.statusCode}: ${loginResponse.data}`
      );
    }

    if (!loginResponse.json) {
      throw new Error("Login response was not JSON");
    }

    const { access_token } = loginResponse.json;
    if (!access_token) {
      throw new Error("No access token in login response");
    }

    const cookies = extractCookies(loginResponse.headers);
    const refreshToken = cookies.refresh_token;

    if (!refreshToken) {
      console.log(
        "⚠️  WARNING: No refresh token cookie found in login response"
      );
    }

    console.log("✅ PASS: Login successful");
    console.log(`   Access token: ${access_token.substring(0, 20)}...`);
    console.log(
      `   Refresh token: ${
        refreshToken ? refreshToken.substring(0, 20) + "..." : "Not found"
      }`
    );

    return {
      access_token,
      refresh_token: refreshToken,
      cookies: formatCookies(cookies),
    };
  } catch (error) {
    console.log(`❌ FAIL: Login error: ${error.message}`);
    throw error;
  }
}

/**
 * Test workspace page after authentication
 */
async function testWorkspaceAuthenticated(authData) {
  console.log("\n🏠 Testing workspace page (authenticated)...");

  try {
    const response = await makeRequest(`${FRONTEND_BASE}/workspace`, {
      headers: {
        Authorization: `Bearer ${authData.access_token}`,
        Cookie: authData.cookies,
      },
    });

    if (response.statusCode === 200) {
      // Check if we're still seeing access denied (auth not working)
      if (response.data.includes("Access Denied")) {
        console.log(
          "❌ FAIL: Workspace still shows access denied despite authentication"
        );
        console.log(
          "   This suggests the frontend is not properly checking authentication"
        );
        return false;
      } else {
        console.log(
          "✅ PASS: Workspace page loaded successfully with authentication"
        );
        console.log(`   Status: ${response.statusCode}`);

        // Check for common workspace elements
        const hasWorkspaceContent =
          response.data.includes("Workspace") ||
          response.data.includes("workspace") ||
          response.data.includes("Dashboard");

        if (hasWorkspaceContent) {
          console.log("✅ PASS: Page appears to contain workspace content");
        } else {
          console.log(
            "⚠️  WARNING: Page loaded but may not contain expected workspace content"
          );
        }

        return true;
      }
    } else {
      console.log(
        `❌ FAIL: Workspace page returned status ${response.statusCode}`
      );
      console.log(`Response preview: ${response.data.substring(0, 200)}...`);
      return false;
    }
  } catch (error) {
    console.log(
      `❌ FAIL: Error testing authenticated workspace: ${error.message}`
    );
    return false;
  }
}

/**
 * Test refresh token functionality on workspace
 */
async function testWorkspaceRefresh(authData) {
  console.log("\n🔄 Testing refresh token functionality...");

  try {
    // Test the refresh endpoint
    const refreshResponse = await makeRequest(
      `${FRONTEND_BASE}/api/auth/refresh`,
      {
        method: "POST",
        headers: {
          Cookie: authData.cookies,
        },
      }
    );

    if (refreshResponse.statusCode !== 200) {
      console.log(
        `❌ FAIL: Refresh failed with status ${refreshResponse.statusCode}`
      );
      return false;
    }

    if (!refreshResponse.json) {
      console.log("❌ FAIL: Refresh response was not JSON");
      return false;
    }

    const { access_token: newAccessToken } = refreshResponse.json;
    if (!newAccessToken) {
      console.log("❌ FAIL: No new access token in refresh response");
      return false;
    }

    console.log("✅ PASS: Refresh token endpoint works");
    console.log(`   New access token: ${newAccessToken.substring(0, 20)}...`);

    // Test workspace with new token
    const newCookies = extractCookies(refreshResponse.headers);
    const updatedAuthData = {
      access_token: newAccessToken,
      refresh_token: newCookies.refresh_token || authData.refresh_token,
      cookies: formatCookies({
        ...extractCookies({ cookie: [authData.cookies] }),
        ...newCookies,
      }),
    };

    const workspaceResponse = await makeRequest(`${FRONTEND_BASE}/workspace`, {
      headers: {
        Authorization: `Bearer ${updatedAuthData.access_token}`,
        Cookie: updatedAuthData.cookies,
      },
    });

    if (
      workspaceResponse.statusCode === 200 &&
      !workspaceResponse.data.includes("Access Denied")
    ) {
      console.log("✅ PASS: Workspace accessible with refreshed token");
      return true;
    } else {
      console.log("❌ FAIL: Workspace not accessible with refreshed token");
      return false;
    }
  } catch (error) {
    console.log(`❌ FAIL: Error testing refresh: ${error.message}`);
    return false;
  }
}

/**
 * Main test execution
 */
async function runTests() {
  console.log("🚀 Starting Frontend Workspace Authentication Tests");
  console.log(`   Frontend URL: ${FRONTEND_BASE}`);
  console.log(`   Test User: ${TEST_USER.email}`);
  console.log(`   Workspace ID: ${DEFAULT_WORKSPACE_ID}`);

  const results = {
    unauthenticated: false,
    login: false,
    authenticated: false,
    refresh: false,
  };

  try {
    // Test 1: Unauthenticated workspace access
    results.unauthenticated = await testWorkspaceUnauthenticated();

    // Test 2: Login
    let authData;
    try {
      authData = await performLogin();
      results.login = true;
    } catch (error) {
      console.log("❌ Login failed, skipping remaining tests");
      printSummary(results);
      process.exit(1);
    }

    // Test 3: Authenticated workspace access
    results.authenticated = await testWorkspaceAuthenticated(authData);

    // Test 4: Refresh token functionality
    results.refresh = await testWorkspaceRefresh(authData);
  } catch (error) {
    console.log(`\n💥 Unexpected error: ${error.message}`);
    console.log(error.stack);
  }

  // Print summary
  printSummary(results);

  // Exit with appropriate code
  const allPassed = Object.values(results).every(Boolean);
  process.exit(allPassed ? 0 : 1);
}

/**
 * Print test summary
 */
function printSummary(results) {
  console.log("\n📊 TEST SUMMARY");
  console.log("================");

  const tests = [
    ["Unauthenticated Access Denied", results.unauthenticated],
    ["Login Process", results.login],
    ["Authenticated Access", results.authenticated],
    ["Refresh Token Function", results.refresh],
  ];

  tests.forEach(([name, passed]) => {
    const status = passed ? "✅ PASS" : "❌ FAIL";
    console.log(`${status} ${name}`);
  });

  const passedCount = Object.values(results).filter(Boolean).length;
  const totalCount = Object.keys(results).length;

  console.log(`\n📈 OVERALL: ${passedCount}/${totalCount} tests passed`);

  if (passedCount === totalCount) {
    console.log(
      "🎉 ALL TESTS PASSED - Frontend workspace authentication is working correctly!"
    );
  } else {
    console.log("⚠️  SOME TESTS FAILED - Please check the authentication flow");
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runTests().catch((error) => {
    console.error("💥 Script error:", error);
    process.exit(1);
  });
}

module.exports = { runTests };
