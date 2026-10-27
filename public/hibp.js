"use strict";

/*
  Have I Been Pwned Dark Web radar for the browser.

  Steps:
  1. Hash the password with SHA-1 in this browser.
  2. Send only the first 5 hex characters to api.pwnedpasswords.com.
  3. Search the returned suffixes locally for a match.
  4. Read the breach count when a match is found.

  The full password never leaves the browser.
*/

const HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/";

function bufferToHex(buffer) {
  const bytes = new Uint8Array(buffer);
  let hex = "";
  for (let index = 0; index < bytes.length; index = index + 1) {
    hex = hex + bytes[index].toString(16).padStart(2, "0");
  }
  return hex.toUpperCase();
}

async function sha1Hex(password) {
  const data = new TextEncoder().encode(password);
  const digest = await crypto.subtle.digest("SHA-1", data);
  return bufferToHex(digest);
}

function parseRangeResponse(body, suffix) {
  const target = suffix.toUpperCase();
  const lines = body.split(/\r?\n/);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.indexOf(":") === -1) {
      continue;
    }
    const parts = line.split(":");
    const foundSuffix = parts[0];
    const foundCount = parts[1];
    if (foundSuffix.toUpperCase() !== target) {
      continue;
    }
    const count = parseInt(foundCount, 10);
    if (!Number.isNaN(count) && count > 0) {
      return count;
    }
  }
  return 0;
}

async function checkPassword(password, settings) {
  const options = settings || (window.passwordChecker
    ? window.passwordChecker.getSettings()
    : { hibp_enabled: true, hibp_api_url: HIBP_RANGE_URL });

  const result = {
    checked: false,
    compromised: false,
    breach_count: 0,
    error: "",
    prefix: "",
  };

  if (!options.hibp_enabled) {
    result.error = "Have I Been Pwned checks are turned off in config.json.";
    return result;
  }

  if (typeof password !== "string" || password === "") {
    result.error = "No password was provided for the breach check.";
    return result;
  }

  if (!window.crypto || !window.crypto.subtle) {
    result.error =
      "This browser cannot hash the password safely. Use HTTPS or localhost.";
    return result;
  }

  try {
    const fullHash = await sha1Hex(password);
    const prefix = fullHash.slice(0, 5);
    const suffix = fullHash.slice(5);
    result.prefix = prefix;

    const baseUrl = options.hibp_api_url || HIBP_RANGE_URL;
    const response = await fetch(baseUrl + prefix, {
      method: "GET",
      // Do not set custom headers. Extra headers can force a CORS preflight
      // that the range API may reject. The browser sends its own User-Agent.
      cache: "no-store",
    });

    if (!response.ok) {
      result.error =
        "Have I Been Pwned returned HTTP " +
        response.status +
        ". The strength rating below is still available.";
      return result;
    }

    const body = await response.text();
    const count = parseRangeResponse(body, suffix);
    result.checked = true;
    result.breach_count = count;
    result.compromised = count > 0;
    return result;
  } catch (error) {
    result.error =
      "Could not reach Have I Been Pwned. Check your internet connection. " +
      "The strength rating below is still available.";
    return result;
  }
}

const hibpClient = {
  checkPassword: checkPassword,
  parseRangeResponse: parseRangeResponse,
  sha1Hex: sha1Hex,
};

if (typeof window !== "undefined") {
  window.hibpClient = hibpClient;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = hibpClient;
}
