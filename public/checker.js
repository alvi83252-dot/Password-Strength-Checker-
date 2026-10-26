"use strict";

/*
  Password rules for the web page.

  These rules match password_checker.py. The test suite compares the
  two files so a change on one side does not silently change the other.

  The password is only examined in this browser. This file does not
  send it anywhere. Do not add fetch(), XMLHttpRequest, or a form
  action that would upload the password.
*/

// Keep this number the same as MAX_PASSWORD_LENGTH in password_checker.py.
const MAX_PASSWORD_LENGTH = 128;

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

// A lookup object makes the common-password test a single check.
const COMMON_PASSWORD_SET = {};
for (const commonPassword of COMMON_PASSWORDS) {
  COMMON_PASSWORD_SET[commonPassword] = true;
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

function validatePassword(password) {
  // Same order as the Python version. Spaces-only wins over "too long".
  if (typeof password !== "string") {
    return "Please enter a password made of text.";
  }

  if (password.trim() === "") {
    return "A password cannot be empty or made of only spaces.";
  }

  const length = characterCount(password);
  if (length > MAX_PASSWORD_LENGTH) {
    return (
      "That input is " +
      charactersLabel(length) +
      ". Please use " +
      MAX_PASSWORD_LENGTH +
      " or fewer."
    );
  }

  return null;
}

function isNumber(character) {
  return "0123456789".indexOf(character) !== -1;
}

function isLetter(character) {
  // A letter has a different uppercase and lowercase form.
  // Digits and symbols do not, so they are not letters.
  return character.toLowerCase() !== character.toUpperCase();
}

function isUppercaseLetter(character) {
  return isLetter(character) && character === character.toUpperCase();
}

function isLowercaseLetter(character) {
  return isLetter(character) && character === character.toLowerCase();
}

function isSpecialCharacter(character) {
  // Letters and numbers do not count. Spaces do not count.
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

function collectChecks(password) {
  return {
    length: characterCount(password) >= 8,
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

function decideRating(score, checks, isCommon) {
  if (isCommon || !checks.length || score <= 2) {
    return "Weak";
  }
  if (score >= 5) {
    return "Strong";
  }
  return "Medium";
}

function buildSummary(score, checks, isCommon) {
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
      "8 characters, so the rating is Weak. A short password is easy to guess."
    );
  }

  if (score === 5) {
    return (
      "All 5 checks passed, and this is not a common password, " +
      "so the rating is Strong."
    );
  }

  if (score >= 3) {
    return (
      score +
      " of 5 checks passed, so the rating is Medium. " +
      "A Medium password still has gaps."
    );
  }

  return (
    score +
    " of 5 checks passed, so the rating is Weak. " +
    "Weak passwords are easier to guess."
  );
}

function lengthDetail(password, passed) {
  const counted = charactersLabel(characterCount(password));
  if (passed) {
    return "Length is " + counted + ", which meets the minimum of 8.";
  }
  return "Length is " + counted + ". At least 8 are required.";
}

function buildDetails(password, checks) {
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
    { passed: checks.length, text: lengthDetail(password, checks.length) },
    { passed: checks.uppercase, text: uppercaseText },
    { passed: checks.lowercase, text: lowercaseText },
    { passed: checks.number, text: numberText },
    { passed: checks.special, text: specialText },
  ];
}

function buildSuggestions(password, checks, rating, isCommon) {
  if (rating === "Strong") {
    return [];
  }

  const suggestions = [];

  if (isCommon) {
    suggestions.push("Choose a different password. This one is widely known.");
  }

  if (!checks.length) {
    suggestions.push(
      "Make the password at least 8 characters long. 12 or more is safer."
    );
  } else if (characterCount(password) < 12) {
    suggestions.push("Make it longer. Aim for 12 characters or more.");
  }

  if (!checks.uppercase) {
    suggestions.push("Add at least one uppercase letter (A-Z).");
  }

  if (!checks.lowercase) {
    suggestions.push("Add at least one lowercase letter (a-z).");
  }

  if (!checks.number) {
    suggestions.push("Add at least one number (0-9).");
  }

  if (!checks.special) {
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

function buildHabits(rating) {
  if (rating !== "Strong") {
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
  };
}

function evaluatePassword(password) {
  const error = validatePassword(password);
  if (error !== null) {
    return rejectedResult(password, error);
  }

  const checks = collectChecks(password);
  const score = countPassedChecks(checks);
  const isCommon = COMMON_PASSWORD_SET[password.toLowerCase()] === true;
  const rating = decideRating(score, checks, isCommon);

  return {
    ok: true,
    error: "",
    rating: rating,
    score: score,
    length: characterCount(password),
    checks: checks,
    is_common: isCommon,
    summary: buildSummary(score, checks, isCommon),
    details: buildDetails(password, checks),
    suggestions: buildSuggestions(password, checks, rating, isCommon),
    habits: buildHabits(rating),
  };
}

const passwordChecker = {
  MAX_PASSWORD_LENGTH: MAX_PASSWORD_LENGTH,
  COMMON_PASSWORDS: COMMON_PASSWORDS,
  characterCount: characterCount,
  charactersLabel: charactersLabel,
  evaluatePassword: evaluatePassword,
};

// The browser page reads window.passwordChecker.
// Node tests read module.exports. Either way, the rules are this file.
if (typeof window !== "undefined") {
  window.passwordChecker = passwordChecker;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = passwordChecker;
}
