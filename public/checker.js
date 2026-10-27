"use strict";

/*
  Password rules for the web page.

  These rules match password_checker.py + config.json. The test suite
  compares the two sides so a change on one side does not silently
  change the other.

  The full password stays in this browser. The only network call is the
  Have I Been Pwned range lookup in hibp.js, which sends a 5-character
  SHA-1 prefix only.
*/

const DEFAULT_SETTINGS = {
  min_length: 8,
  recommended_length: 12,
  max_length: 128,
  weak_max_passed_checks: 2,
  moderate_min_passed_checks: 3,
  strong_min_passed_checks: 5,
  require_uppercase: true,
  require_lowercase: true,
  require_number: true,
  require_special: true,
  use_local_common_list: true,
  hibp_enabled: true,
  hibp_timeout_seconds: 10,
  hibp_api_url: "https://api.pwnedpasswords.com/range/",
};

// Keep this list in the same order as COMMON_PASSWORDS in password_checker.py.
const COMMON_PASSWORDS = [
  "password",
  "password1",
  "password12",
  "password123",
  "password!",
  "password1!",
  "passw0rd",
  "123456",
  "1234567",
  "12345678",
  "123456789",
  "1234567890",
  "qwerty",
  "qwerty123",
  "qwertyuiop",
  "abc123",
  "letmein",
  "admin",
  "welcome",
  "welcome1",
  "iloveyou",
  "monkey",
  "dragon",
  "master",
  "login",
  "trustno1",
  "111111",
  "000000",
  "654321",
];

const COMMON_PASSWORD_SET = {};
for (const commonPassword of COMMON_PASSWORDS) {
  COMMON_PASSWORD_SET[commonPassword] = true;
}

let activeSettings = Object.assign({}, DEFAULT_SETTINGS);

function mergeSettings(loaded) {
  const settings = Object.assign({}, DEFAULT_SETTINGS);
  if (loaded && typeof loaded === "object") {
    Object.keys(DEFAULT_SETTINGS).forEach(function (key) {
      if (Object.prototype.hasOwnProperty.call(loaded, key)) {
        settings[key] = loaded[key];
      }
    });
  }
  activeSettings = settings;
  return settings;
}

function getSettings() {
  return activeSettings;
}

function characterCount(password) {
  // Array.from counts whole characters. String.length would count
  // some symbols, such as emoji, as two, which would not match Python.
  return Array.from(password).length;
}

function charactersLabel(count) {
  if (count === 1) {
    return "1 character";
  }
  return count + " characters";
}

function emptyChecks() {
  return {
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  };
}

function emptyBreach() {
  return {
    checked: false,
    compromised: false,
    breach_count: 0,
    error: "",
    prefix: "",
  };
}

function validatePassword(password, settings) {
  const options = settings || activeSettings;

  if (typeof password !== "string") {
    return "Please enter a password made of text.";
  }

  if (password.trim() === "") {
    return "A password cannot be empty or made of only spaces.";
  }

  const length = characterCount(password);
  if (length > options.max_length) {
    return (
      "That input is " +
      charactersLabel(length) +
      ". Please use " +
      options.max_length +
      " or fewer."
    );
  }

  return null;
}

function isNumber(character) {
  return "0123456789".indexOf(character) !== -1;
}

function isLetter(character) {
  return character.toLowerCase() !== character.toUpperCase();
}

function isUppercaseLetter(character) {
  return isLetter(character) && character === character.toUpperCase();
}

function isLowercaseLetter(character) {
  return isLetter(character) && character === character.toLowerCase();
}

function isSpecialCharacter(character) {
  if (isLetter(character) || isNumber(character)) {
    return false;
  }
  if (/\s/u.test(character)) {
    return false;
  }
  return true;
}

function containsUppercase(password) {
  for (const character of Array.from(password)) {
    if (isUppercaseLetter(character)) {
      return true;
    }
  }
  return false;
}

function containsLowercase(password) {
  for (const character of Array.from(password)) {
    if (isLowercaseLetter(character)) {
      return true;
    }
  }
  return false;
}

function containsNumber(password) {
  for (const character of Array.from(password)) {
    if (isNumber(character)) {
      return true;
    }
  }
  return false;
}

function containsSpecial(password) {
  for (const character of Array.from(password)) {
    if (isSpecialCharacter(character)) {
      return true;
    }
  }
  return false;
}

function isRepeatedCharacter(password) {
  const characters = Array.from(password);
  if (characters.length === 0) {
    return false;
  }
  const first = characters[0];
  for (const character of characters) {
    if (character !== first) {
      return false;
    }
  }
  return true;
}

function collectChecks(password, settings) {
  const options = settings || activeSettings;
  return {
    length: characterCount(password) >= options.min_length,
    uppercase: containsUppercase(password),
    lowercase: containsLowercase(password),
    number: containsNumber(password),
    special: containsSpecial(password),
  };
}

function countPassedChecks(checks) {
  let total = 0;
  const names = ["length", "uppercase", "lowercase", "number", "special"];
  for (const name of names) {
    if (checks[name]) {
      total = total + 1;
    }
  }
  return total;
}

function decideRating(score, checks, isCommon, settings) {
  const options = settings || activeSettings;
  if (isCommon || !checks.length || score <= options.weak_max_passed_checks) {
    return "Weak";
  }
  if (score >= options.strong_min_passed_checks) {
    return "Strong";
  }
  if (score >= options.moderate_min_passed_checks) {
    return "Moderate";
  }
  return "Weak";
}

function buildSummary(score, checks, isCommon, rating, settings) {
  const options = settings || activeSettings;

  if (isCommon) {
    return (
      "This password is on a short list of commonly leaked passwords, " +
      "so the rating is Weak. Attackers try these passwords first."
    );
  }

  if (!checks.length) {
    return (
      score +
      " of 5 checks passed, but the password is shorter than " +
      options.min_length +
      " characters, so the rating is Weak. A short password is easy to guess."
    );
  }

  if (rating === "Strong") {
    return (
      "All required checks passed, and this is not a common password, " +
      "so the rating is Strong."
    );
  }

  if (rating === "Moderate") {
    return (
      score +
      " of 5 checks passed, so the rating is Moderate. " +
      "A Moderate password still has gaps."
    );
  }

  return (
    score +
    " of 5 checks passed, so the rating is Weak. " +
    "Weak passwords are easier to guess."
  );
}

function lengthDetail(password, passed, settings) {
  const options = settings || activeSettings;
  const counted = charactersLabel(characterCount(password));
  if (passed) {
    return (
      "Length is " +
      counted +
      ", which meets the minimum of " +
      options.min_length +
      "."
    );
  }
  return (
    "Length is " +
    counted +
    ". At least " +
    options.min_length +
    " are required."
  );
}

function buildDetails(password, checks, settings) {
  const options = settings || activeSettings;
  let uppercaseText;
  if (checks.uppercase) {
    uppercaseText = "Contains an uppercase letter.";
  } else {
    uppercaseText = "Missing an uppercase letter (A-Z).";
  }

  let lowercaseText;
  if (checks.lowercase) {
    lowercaseText = "Contains a lowercase letter.";
  } else {
    lowercaseText = "Missing a lowercase letter (a-z).";
  }

  let numberText;
  if (checks.number) {
    numberText = "Contains a number.";
  } else {
    numberText = "Missing a number (0-9).";
  }

  let specialText;
  if (checks.special) {
    specialText = "Contains a special character.";
  } else {
    specialText = "Missing a special character (such as ! ? # or @).";
  }

  return [
    {
      passed: checks.length,
      text: lengthDetail(password, checks.length, options),
    },
    { passed: checks.uppercase, text: uppercaseText },
    { passed: checks.lowercase, text: lowercaseText },
    { passed: checks.number, text: numberText },
    { passed: checks.special, text: specialText },
  ];
}

function formatBreachCount(count) {
  const number = Number(count) || 0;
  const labeled = number.toLocaleString("en-US");
  if (number === 1) {
    return labeled + " time";
  }
  return labeled + " times";
}

function buildSuggestions(password, checks, rating, isCommon, compromised, settings) {
  const options = settings || activeSettings;

  if (rating === "Strong" && !compromised) {
    return [];
  }

  const suggestions = [];

  if (compromised) {
    suggestions.push(
      "Stop using this password everywhere. It has appeared in known data breaches."
    );
    suggestions.push(
      "Create a brand-new password that you have never used before."
    );
  }

  if (isCommon) {
    suggestions.push("Choose a different password. This one is widely known.");
  }

  if (!checks.length) {
    suggestions.push(
      "Make the password at least " +
        options.min_length +
        " characters long. " +
        options.recommended_length +
        " or more is safer."
    );
  } else if (characterCount(password) < options.recommended_length) {
    suggestions.push(
      "Make it longer. Aim for " +
        options.recommended_length +
        " characters or more."
    );
  }

  if (options.require_uppercase && !checks.uppercase) {
    suggestions.push("Add at least one uppercase letter (A-Z).");
  }

  if (options.require_lowercase && !checks.lowercase) {
    suggestions.push("Add at least one lowercase letter (a-z).");
  }

  if (options.require_number && !checks.number) {
    suggestions.push("Add at least one number (0-9).");
  }

  if (options.require_special && !checks.special) {
    suggestions.push("Add at least one special character, such as ! ? # or @.");
  }

  if (isRepeatedCharacter(password)) {
    suggestions.push("Avoid using the same character over and over.");
  }

  suggestions.push(
    "Use a unique password for each account, and keep it in a password manager."
  );
  return suggestions;
}

function buildHabits(rating, compromised) {
  if (rating !== "Strong" || compromised) {
    return [];
  }
  return [
    "No changes are required for a Strong rating.",
    "Use this password on only one account.",
    "Store it in a password manager so you do not have to reuse it.",
  ];
}

function rejectedResult(password, error) {
  let length = 0;
  if (typeof password === "string") {
    length = characterCount(password);
  }

  return {
    ok: false,
    error: error,
    rating: "",
    score: 0,
    length: length,
    checks: emptyChecks(),
    is_common: false,
    summary: "",
    details: [],
    suggestions: [],
    habits: [],
    breach: emptyBreach(),
  };
}

function evaluatePassword(password, settings) {
  const options = settings || activeSettings;
  const error = validatePassword(password, options);
  if (error !== null) {
    return rejectedResult(password, error);
  }

  const checks = collectChecks(password, options);
  const score = countPassedChecks(checks);
  let isCommon = false;
  if (options.use_local_common_list) {
    isCommon = COMMON_PASSWORD_SET[password.toLowerCase()] === true;
  }
  const rating = decideRating(score, checks, isCommon, options);

  return {
    ok: true,
    error: "",
    rating: rating,
    score: score,
    length: characterCount(password),
    checks: checks,
    is_common: isCommon,
    summary: buildSummary(score, checks, isCommon, rating, options),
    details: buildDetails(password, checks, options),
    suggestions: buildSuggestions(
      password,
      checks,
      rating,
      isCommon,
      false,
      options
    ),
    habits: buildHabits(rating, false),
    breach: emptyBreach(),
  };
}

function applyBreachResult(result, breach, password, settings) {
  const options = settings || activeSettings;
  const next = Object.assign({}, result, {
    breach: breach || emptyBreach(),
  });

  if (!breach || !breach.compromised) {
    return next;
  }

  next.rating = "Weak";
  next.summary =
    "COMPROMISED: this password has appeared " +
    formatBreachCount(breach.breach_count) +
    " in Have I Been Pwned breached-password records. " +
    "Do not use it. The rule-based score was " +
    result.score +
    " of 5 before the breach check.";
  next.suggestions = buildSuggestions(
    password || "",
    result.checks,
    "Weak",
    result.is_common,
    true,
    options
  );
  next.habits = [];
  return next;
}

const passwordChecker = {
  DEFAULT_SETTINGS: DEFAULT_SETTINGS,
  COMMON_PASSWORDS: COMMON_PASSWORDS,
  characterCount: characterCount,
  charactersLabel: charactersLabel,
  mergeSettings: mergeSettings,
  getSettings: getSettings,
  evaluatePassword: evaluatePassword,
  applyBreachResult: applyBreachResult,
  formatBreachCount: formatBreachCount,
  emptyBreach: emptyBreach,
};

if (typeof window !== "undefined") {
  window.passwordChecker = passwordChecker;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = passwordChecker;
}
