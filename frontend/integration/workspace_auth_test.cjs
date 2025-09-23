#!/usr/bin/env node

/**
 * Workspace Authentication Integration Test
 * 
 * This script replicates the exact frontend workspace test flow:
 * 1. Login using the same process as logintest route  
 * 2. Perform comprehensive token refresh tests as done by workspace route
 * 3. Provide detailed logging for both requests and responses
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// Configuration
const FRONTEND_URL = 'http://localhost:5173';
const TEST_EMAIL = 'dev@example.com';
const TEST_PASSWORD = 'devpassword123';

// Logging utilities
function log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level}]`;
    console.log(`${prefix} ${message}`);
}

function logRequest(method, url, headers, body) {
    log(`🔄 REQUEST: ${method} ${url}`, 'REQ');
    log(`  Headers: ${JSON.stringify(headers, null, 2)}`, 'REQ');
    if (body) {
        log(`  Body: ${body}`, 'REQ');
    }
}

function logResponse(statusCode, statusMessage, headers, body) {
    const level = statusCode >= 400 ? 'ERROR' : 'RESP';
    log(`📥 RESPONSE: ${statusCode} ${statusMessage}`, level);
    log(`  Headers: ${JSON.stringify(headers, null, 2)}`, level);
    if (body) {
        log(`  Body: ${body}`, level);
    }
}

// HTTP client utility
function makeRequest(method, url, options = {}) {
    return new Promise((resolve, reject) => {
        const parsedUrl = new URL(url);
        const isHttps = parsedUrl.protocol === 'https:';
        const client = isHttps ? https : http;
        
        const reqOptions = {
            hostname: parsedUrl.hostname,
            port: parsedUrl.port || (isHttps ? 443 : 80),
            path: parsedUrl.pathname + parsedUrl.search,
            method: method,
            headers: {
                'User-Agent': 'Integration-Test-Script/1.0',
                ...options.headers
            }
        };

        // Log the request
        logRequest(method, url, reqOptions.headers, options.body);

        const req = client.request(reqOptions, (res) => {
            let responseBody = '';
            
            res.on('data', (chunk) => {
                responseBody += chunk;
            });
            
            res.on('end', () => {
                // Log the response
                logResponse(res.statusCode, res.statusMessage, res.headers, responseBody);
                
                resolve({
                    statusCode: res.statusCode,
                    statusMessage: res.statusMessage,
                    headers: res.headers,
                    body: responseBody,
                    ok: res.statusCode >= 200 && res.statusCode < 300
                });
            });
        });

        req.on('error', (err) => {
            log(`❌ Request Error: ${err.message}`, 'ERROR');
            reject(err);
        });

        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

// Parse cookies from response headers
function parseCookies(headers) {
    const cookies = {};
    const setCookieHeaders = headers['set-cookie'] || [];
    
    setCookieHeaders.forEach(cookie => {
        const parts = cookie.split(';')[0].split('=');
        if (parts.length === 2) {
            cookies[parts[0].trim()] = parts[1].trim();
        }
    });
    
    return cookies;
}

// Build cookie header from cookie object
function buildCookieHeader(cookies) {
    return Object.entries(cookies)
        .map(([name, value]) => `${name}=${value}`)
        .join('; ');
}

// Test state
let cookies = {};
let accessToken = null;
let refreshAttempts = 0;
const MAX_REFRESH_ATTEMPTS = 3;

// Step 1: Login using same process as logintest route
async function performLogin() {
    log('🔐 Starting login process (replicating logintest route)', 'TEST');
    
    const requestId = Math.random().toString(36).substring(0, 8);
    log(`Login request ID: ${requestId}`);
    log(`Email: ${TEST_EMAIL}`);
    log(`Password: ${'*'.repeat(TEST_PASSWORD.length)}`);
    
    const startTime = Date.now();
    
    try {
        const response = await makeRequest('POST', `${FRONTEND_URL}/api/auth/login`, {
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: TEST_EMAIL,
                password: TEST_PASSWORD
            })
        });
        
        const duration = Date.now() - startTime;
        log(`Login response received in ${duration}ms`);
        
        // Parse cookies from response
        const responseCookies = parseCookies(response.headers);
        Object.assign(cookies, responseCookies);
        log(`Cookies received: ${JSON.stringify(responseCookies, null, 2)}`);
        
        if (response.ok) {
            const responseData = JSON.parse(response.body);
            accessToken = responseData.access_token;
            
            log('✅ Login successful!', 'SUCCESS');
            log(`User ID: ${responseData.user?.id || 'missing'}`);
            log(`User Name: ${responseData.user?.first_name || ''} ${responseData.user?.last_name || ''}`);
            log(`Access Token Present: ${!!responseData.access_token}`);
            log(`Token Type: ${responseData.token_type || 'missing'}`);
            log(`Expires In: ${responseData.expires_in || 'missing'} seconds`);
            log(`Workspaces: ${responseData.workspaces?.length || 0}`);
            
            if (accessToken) {
                log(`Access token (first 20 chars): ${accessToken.substring(0, 20)}...`);
            }
            
            return { success: true, data: responseData };
        } else {
            const errorData = JSON.parse(response.body || '{}');
            log(`❌ Login failed: ${response.statusCode} ${response.statusMessage}`, 'ERROR');
            log(`Error details: ${JSON.stringify(errorData, null, 2)}`, 'ERROR');
            return { success: false, error: errorData };
        }
        
    } catch (error) {
        log(`❌ Login network error: ${error.message}`, 'ERROR');
        return { success: false, error: error.message };
    }
}

// Refresh access token (replicating workspace route logic)
async function refreshAccessToken() {
    if (refreshAttempts >= MAX_REFRESH_ATTEMPTS) {
        log(`Max refresh attempts (${MAX_REFRESH_ATTEMPTS}) reached`, 'WARN');
        return false;
    }
    
    refreshAttempts++;
    log(`🔄 Attempting to refresh access token (attempt ${refreshAttempts}/${MAX_REFRESH_ATTEMPTS})...`);
    
    try {
        const response = await makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
            headers: {
                'Cookie': buildCookieHeader(cookies)
            }
        });
        
        if (response.ok) {
            const data = JSON.parse(response.body);
            if (data.access_token) {
                const oldToken = accessToken;
                accessToken = data.access_token;
                
                // Update cookies from response
                const responseCookies = parseCookies(response.headers);
                Object.assign(cookies, responseCookies);
                
                log(`✅ Token refreshed successfully: ${oldToken?.substring(0, 8)}... → ${data.access_token?.substring(0, 8)}...`, 'SUCCESS');
                refreshAttempts = 0;
                return true;
            }
        } else {
            const errorData = JSON.parse(response.body || '{}');
            log(`❌ Token refresh failed: ${response.statusCode} ${errorData.detail || errorData.error}`, 'ERROR');
            if (response.statusCode === 401) {
                accessToken = null;
            }
        }
    } catch (err) {
        log(`❌ Network error during token refresh: ${err.message}`, 'ERROR');
    }
    
    return false;
}

// Validate token (replicating workspace route logic)
async function validateToken() {
    if (!accessToken) {
        log('No access token available for validation', 'WARN');
        return false;
    }
    
    try {
        const response = await makeRequest('GET', `${FRONTEND_URL}/api/auth/validate`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                'Cookie': buildCookieHeader(cookies)
            }
        });
        
        if (response.ok) {
            const validationData = JSON.parse(response.body);
            log('✅ User validation successful', 'SUCCESS');
            log(`Validated user: ${JSON.stringify(validationData.user, null, 2)}`);
            return true;
        } else {
            const errorData = JSON.parse(response.body || '{}');
            log(`❌ Token validation failed: ${response.statusCode} ${errorData.detail || errorData.error}`, 'ERROR');
            return false;
        }
    } catch (err) {
        log(`❌ Network error during token validation: ${err.message}`, 'ERROR');
        return false;
    }
}

// Test 1: Basic refresh functionality (replicating workspace route)
async function testBasicRefresh() {
    log('🧪 Test 1: Basic refresh functionality', 'TEST');
    
    const oldToken = accessToken;
    
    const response = await makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
        headers: {
            'Cookie': buildCookieHeader(cookies)
        }
    });
    
    if (!response.ok) {
        const errorData = JSON.parse(response.body || '{}');
        return {
            success: false,
            error: `HTTP ${response.statusCode}: ${errorData.detail || errorData.error}`
        };
    }
    
    const data = JSON.parse(response.body);
    if (!data.access_token) {
        return { success: false, error: 'No access token in response' };
    }
    
    if (data.access_token === oldToken) {
        return { success: false, error: 'New token is same as old token' };
    }
    
    // Update cookies from response
    const responseCookies = parseCookies(response.headers);
    Object.assign(cookies, responseCookies);
    
    return {
        success: true,
        oldToken: oldToken?.substring(0, 8) + '...',
        newToken: data.access_token?.substring(0, 8) + '...',
        tokenType: data.token_type,
        expiresIn: data.expires_in,
        note: 'Test verified refresh mechanism works'
    };
}

// Test 2: Simulate expired access token scenario
async function testExpiredTokenSimulation() {
    log('🧪 Test 2: Expired token simulation', 'TEST');
    
    // Create a test token that will definitely be invalid
    const testInvalidToken = 'TEST_EXPIRED_TOKEN_' + Date.now();
    
    // Test the validation with invalid token (should fail)
    const response = await makeRequest('GET', `${FRONTEND_URL}/api/auth/validate`, {
        headers: {
            'Authorization': `Bearer ${testInvalidToken}`,
            'Content-Type': 'application/json',
            'Cookie': buildCookieHeader(cookies)
        }
    });
    
    if (response.ok) {
        return {
            success: false,
            error: 'Invalid token was unexpectedly accepted'
        };
    }
    
    if (response.statusCode !== 401) {
        return { success: false, error: `Expected 401, got ${response.statusCode}` };
    }
    
    // Now test that refresh still works with our valid refresh token
    const refreshResponse = await makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
        headers: {
            'Cookie': buildCookieHeader(cookies)
        }
    });
    
    if (!refreshResponse.ok) {
        const errorData = JSON.parse(refreshResponse.body || '{}');
        return {
            success: false,
            error: `Refresh failed: ${errorData.detail || errorData.error}`
        };
    }
    
    const refreshData = JSON.parse(refreshResponse.body);
    if (!refreshData.access_token) {
        return { success: false, error: 'No access token in refresh response' };
    }
    
    // Update cookies and token
    const responseCookies = parseCookies(refreshResponse.headers);
    Object.assign(cookies, responseCookies);
    accessToken = refreshData.access_token;
    
    return {
        success: true,
        invalidTokenRejected: true,
        refreshWorked: true,
        newToken: refreshData.access_token?.substring(0, 8) + '...'
    };
}

// Test 3: Multiple concurrent refresh attempts
async function testMultipleConcurrentRefresh() {
    log('🧪 Test 3: Multiple concurrent refresh attempts', 'TEST');
    
    const originalRefreshAttempts = refreshAttempts;
    refreshAttempts = 0;
    
    try {
        // Start multiple refresh attempts simultaneously
        const promises = [
            makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
                headers: { 'Cookie': buildCookieHeader(cookies) }
            }),
            makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
                headers: { 'Cookie': buildCookieHeader(cookies) }
            }),
            makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
                headers: { 'Cookie': buildCookieHeader(cookies) }
            })
        ];
        
        const results = await Promise.all(promises);
        
        // All should succeed (server should handle concurrent requests)
        const successCount = results.filter(r => r.ok).length;
        
        if (successCount === 0) {
            return { success: false, error: 'No refresh requests succeeded' };
        }
        
        // Update with latest successful response
        const successfulResponse = results.find(r => r.ok);
        if (successfulResponse) {
            const data = JSON.parse(successfulResponse.body);
            if (data.access_token) {
                accessToken = data.access_token;
                const responseCookies = parseCookies(successfulResponse.headers);
                Object.assign(cookies, responseCookies);
            }
        }
        
        return {
            success: true,
            totalRequests: promises.length,
            successfulRequests: successCount,
            allSucceeded: successCount === promises.length
        };
    } finally {
        refreshAttempts = originalRefreshAttempts;
    }
}

// Test 4: Edge cases and error handling
async function testEdgeCases() {
    log('🧪 Test 4: Edge cases and error handling', 'TEST');
    
    const tests = [];
    
    // Test that refresh endpoint is accessible
    try {
        const refreshResponse = await makeRequest('POST', `${FRONTEND_URL}/api/auth/refresh`, {
            headers: {
                'Cookie': buildCookieHeader(cookies)
            }
        });
        
        tests.push({
            name: 'refresh_endpoint_accessible',
            success: refreshResponse.statusCode === 200 || refreshResponse.statusCode === 401,
            result: `HTTP ${refreshResponse.statusCode}`
        });
    } catch (error) {
        tests.push({
            name: 'refresh_endpoint_accessible',
            success: false,
            result: `Network error: ${error.message}`
        });
    }
    
    // Test validate endpoint accessibility
    try {
        const validateResponse = await makeRequest('GET', `${FRONTEND_URL}/api/auth/validate`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                'Cookie': buildCookieHeader(cookies)
            }
        });
        
        tests.push({
            name: 'validate_endpoint_accessible',
            success: validateResponse.statusCode === 200 || validateResponse.statusCode === 401,
            result: `HTTP ${validateResponse.statusCode}`
        });
    } catch (error) {
        tests.push({
            name: 'validate_endpoint_accessible',
            success: false,
            result: `Network error: ${error.message}`
        });
    }
    
    const allEdgeTestsPassed = tests.every(t => t.success);
    
    return {
        success: allEdgeTestsPassed,
        edgeTests: tests,
        error: allEdgeTestsPassed ? null : 'Some edge case tests failed'
    };
}

// Main test execution
async function runWorkspaceAuthTests() {
    log('🚀 Starting Workspace Authentication Integration Tests', 'MAIN');
    log('=' .repeat(80), 'MAIN');
    
    const results = {};
    let overallSuccess = true;
    
    // Step 1: Login
    log('\n' + '='.repeat(40), 'MAIN');
    log('STEP 1: LOGIN PROCESS', 'MAIN');
    log('='.repeat(40), 'MAIN');
    
    const loginResult = await performLogin();
    results.login = loginResult;
    
    if (!loginResult.success) {
        log('❌ Login failed - cannot proceed with tests', 'ERROR');
        return { success: false, results };
    }
    
    // Step 2: Initial validation
    log('\n' + '='.repeat(40), 'MAIN');
    log('STEP 2: INITIAL TOKEN VALIDATION', 'MAIN');
    log('='.repeat(40), 'MAIN');
    
    const initialValidation = await validateToken();
    results.initialValidation = { success: initialValidation };
    
    if (!initialValidation) {
        log('❌ Initial token validation failed', 'ERROR');
        overallSuccess = false;
    }
    
    // Step 3: Run comprehensive tests (replicating workspace route)
    log('\n' + '='.repeat(40), 'MAIN');
    log('STEP 3: COMPREHENSIVE TOKEN REFRESH TESTS', 'MAIN');
    log('='.repeat(40), 'MAIN');
    
    const tests = [
        { name: 'basicRefresh', fn: testBasicRefresh },
        { name: 'expiredTokenSimulation', fn: testExpiredTokenSimulation },
        { name: 'multipleConcurrentRefresh', fn: testMultipleConcurrentRefresh },
        { name: 'edgeCases', fn: testEdgeCases }
    ];
    
    for (const test of tests) {
        log(`\n--- Running ${test.name} ---`, 'TEST');
        try {
            const testResult = await test.fn();
            results[test.name] = testResult;
            
            if (testResult.success) {
                log(`✅ ${test.name} PASSED`, 'SUCCESS');
                log(`Result: ${JSON.stringify(testResult, null, 2)}`, 'SUCCESS');
            } else {
                log(`❌ ${test.name} FAILED`, 'ERROR');
                log(`Error: ${testResult.error}`, 'ERROR');
                overallSuccess = false;
            }
        } catch (error) {
            log(`❌ ${test.name} CRASHED: ${error.message}`, 'ERROR');
            results[test.name] = { success: false, error: error.message };
            overallSuccess = false;
        }
    }
    
    // Final summary
    log('\n' + '='.repeat(80), 'MAIN');
    log('FINAL SUMMARY', 'MAIN');
    log('='.repeat(80), 'MAIN');
    
    Object.entries(results).forEach(([testName, result]) => {
        const status = result.success ? '✅ PASS' : '❌ FAIL';
        log(`${testName}: ${status}`, result.success ? 'SUCCESS' : 'ERROR');
    });
    
    log(`\nOverall Result: ${overallSuccess ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`, overallSuccess ? 'SUCCESS' : 'ERROR');
    
    return { success: overallSuccess, results };
}

// Run the tests
if (require.main === module) {
    runWorkspaceAuthTests()
        .then(result => {
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            log(`💥 Test suite crashed: ${error.message}`, 'FATAL');
            console.error(error);
            process.exit(1);
        });
}

module.exports = { runWorkspaceAuthTests };