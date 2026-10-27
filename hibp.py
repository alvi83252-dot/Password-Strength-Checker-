"""
Have I Been Pwned "Dark Web" radar.

This module uses the free Pwned Passwords range API with k-anonymity:
1. Hash the password with SHA-1 on this computer.
2. Send only the first 5 characters of that hash.
3. Search the returned suffixes locally for a match.
4. Read the breach count if the password was found.

The full password is never sent to Have I Been Pwned.
No API key is required for this endpoint.
"""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request

from config import SETTINGS


def sha1_hex(password):
    """Return the uppercase SHA-1 hex digest of a UTF-8 password."""
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest()
    return digest.upper()


def parse_range_response(body, suffix):
    """Find the breach count for a hash suffix, or 0 if it is absent.

    Each line looks like SUFFIX:COUNT. Padded filler lines use count 0
    and are ignored.
    """
    target = suffix.upper()
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        found_suffix, found_count = line.split(":", 1)
        if found_suffix.upper() != target:
            continue
        try:
            count = int(found_count.strip())
        except ValueError:
            continue
        if count > 0:
            return count
    return 0


def fetch_range(prefix, settings=None):
    """Download the hash-suffix list for a five-character prefix."""
    options = settings if settings is not None else SETTINGS
    url = options["hibp_api_url"] + prefix.upper()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": options["hibp_user_agent"],
            "Add-Padding": "true",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=options["hibp_timeout_seconds"]) as response:
        return response.read().decode("utf-8", errors="replace")


def check_password(password, settings=None):
    """Check one password against Have I Been Pwned.

    Returns a dictionary:
      checked      - True when the API was queried
      compromised  - True when the password was found in breach data
      breach_count - how many times it appeared (0 if not found)
      error        - message when the check could not finish
      prefix       - the five hash characters that were sent (never the password)
    """
    options = settings if settings is not None else SETTINGS

    result = {
        "checked": False,
        "compromised": False,
        "breach_count": 0,
        "error": "",
        "prefix": "",
    }

    if not options.get("hibp_enabled", True):
        result["error"] = "Have I Been Pwned checks are turned off in config.json."
        return result

    if not isinstance(password, str) or password == "":
        result["error"] = "No password was provided for the breach check."
        return result

    full_hash = sha1_hex(password)
    prefix = full_hash[:5]
    suffix = full_hash[5:]
    result["prefix"] = prefix

    try:
        body = fetch_range(prefix, options)
        count = parse_range_response(body, suffix)
        result["checked"] = True
        result["breach_count"] = count
        result["compromised"] = count > 0
        return result
    except urllib.error.HTTPError as error:
        result["error"] = (
            "Have I Been Pwned returned HTTP "
            + str(error.code)
            + ". The strength rating below is still available."
        )
        return result
    except urllib.error.URLError:
        result["error"] = (
            "Could not reach Have I Been Pwned. Check your internet connection. "
            "The strength rating below is still available."
        )
        return result
    except TimeoutError:
        result["error"] = (
            "The Have I Been Pwned request timed out. "
            "The strength rating below is still available."
        )
        return result
    except Exception as error:  # noqa: BLE001 - surface any network failure cleanly
        result["error"] = (
            "The breach check failed ("
            + error.__class__.__name__
            + "). The strength rating below is still available."
        )
        return result
