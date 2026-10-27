"use strict";

/*
  Page behavior for the password checker.

  checker.js decides the local strength rating.
  hibp.js runs the Dark Web radar with k-anonymity.
  This file only updates the page. The full password is never uploaded.
*/

const checker = window.passwordChecker;
const hibp = window.hibpClient;

const passwordInput = document.querySelector("#password-input");
const toggleButton = document.querySelector("#toggle-visibility");
const checkButton = document.querySelector("#check-button");
const clearButton = document.querySelector("#clear-button");
const feedback = document.querySelector("#feedback");
const liveStatus = document.querySelector("#live-status");
const analysis = document.querySelector("#analysis");
const flag = document.querySelector("#flag");
const ratingText = document.querySelector("#rating-text");
const scoreText = document.querySelector("#score-text");
const summaryText = document.querySelector("#summary-text");
const detailsList = document.querySelector("#details");
const adviceTitle = document.querySelector("#advice-title");
const adviceList = document.querySelector("#advice");
const meter = document.querySelector("#meter");
const characterCountText = document.querySelector("#character-count");
const sampleButtons = document.querySelectorAll("[data-sample]");
const radar = document.querySelector("#radar");
const radarStatus = document.querySelector("#radar-status");
const radarCount = document.querySelector("#radar-count");
const thresholdNote = document.querySelector("#threshold-note");

let requestToken = 0;
let debounceTimer = null;

function clearElement(element) {
  element.textContent = "";
}

function addTextItem(list, text) {
  const item = document.createElement("li");
  item.textContent = text;
  list.appendChild(item);
  return item;
}

function setMeter(score, rating) {
  meter.dataset.rating = rating;
  const bars = meter.querySelectorAll("span");
  bars.forEach(function (bar, index) {
    if (index < score) {
      bar.classList.add("on");
    } else {
      bar.classList.remove("on");
    }
  });

  if (!rating) {
    meter.setAttribute("aria-label", "No password yet");
    return;
  }
  meter.setAttribute("aria-label", score + " of 5 checks, rated " + rating);
}

function hideAnalysis() {
  analysis.hidden = true;
  delete analysis.dataset.rating;
  flag.hidden = true;
  flag.textContent = "";
  ratingText.textContent = "";
  scoreText.textContent = "";
  summaryText.textContent = "";
  adviceTitle.textContent = "";
  clearElement(detailsList);
  clearElement(adviceList);
  setMeter(0, "");
  radar.hidden = true;
  radar.className = "radar";
  radarStatus.textContent = "";
  radarCount.textContent = "";
}

function showIdle() {
  feedback.className = "feedback";
  feedback.textContent = "Enter a password to see its strength and breach status.";
  liveStatus.textContent = feedback.textContent;
  passwordInput.setAttribute("aria-invalid", "false");
  hideAnalysis();
}

function showError(message) {
  feedback.className = "feedback error";
  feedback.textContent = message;
  liveStatus.textContent = message;
  passwordInput.setAttribute("aria-invalid", "true");
  hideAnalysis();
}

function addDetail(detail) {
  const item = document.createElement("li");
  item.className = detail.passed ? "pass" : "fail";

  const mark = document.createElement("span");
  mark.className = "mark";
  mark.textContent = detail.passed ? "Pass" : "Fail";

  const text = document.createElement("span");
  text.textContent = detail.text;

  item.appendChild(mark);
  item.appendChild(text);
  detailsList.appendChild(item);
}

function showRadar(breach) {
  radar.hidden = false;
  radarCount.textContent = "";

  if (breach.compromised) {
    radar.className = "radar compromised";
    radarStatus.textContent = "COMPROMISED";
    radarCount.textContent =
      "Seen in " +
      checker.formatBreachCount(breach.breach_count) +
      " on Have I Been Pwned.";
    return;
  }

  if (breach.checked) {
    radar.className = "radar clear";
    radarStatus.textContent = "Not found in HIBP range";
    radarCount.textContent =
      "This password was not in the returned Have I Been Pwned range.";
    return;
  }

  radar.className = "radar pending";
  radarStatus.textContent = "Breach check unavailable";
  radarCount.textContent = breach.error || "The Dark Web radar did not finish.";
}

function showResult(result) {
  feedback.className = "feedback";
  feedback.textContent = "";
  passwordInput.setAttribute("aria-invalid", "false");
  analysis.hidden = false;
  analysis.dataset.rating = result.rating.toLowerCase();

  if (result.breach && result.breach.compromised) {
    flag.hidden = false;
    flag.textContent = "Compromised in known data breaches";
  } else if (result.is_common) {
    flag.hidden = false;
    flag.textContent = "Commonly leaked password";
  } else if (!result.checks.length) {
    flag.hidden = false;
    flag.textContent =
      "Shorter than " + checker.getSettings().min_length + " characters";
  } else {
    flag.hidden = true;
    flag.textContent = "";
  }

  ratingText.textContent = result.rating;
  scoreText.textContent = result.score + " of 5 checks";
  summaryText.textContent = result.summary;
  liveStatus.textContent = result.rating + ". " + result.summary;

  clearElement(detailsList);
  result.details.forEach(addDetail);

  clearElement(adviceList);
  if (result.rating === "Strong" && !(result.breach && result.breach.compromised)) {
    adviceTitle.textContent = "Good habits";
    result.habits.forEach(function (habit) {
      addTextItem(adviceList, habit);
    });
  } else {
    adviceTitle.textContent = "Suggestions";
    result.suggestions.forEach(function (suggestion) {
      addTextItem(adviceList, suggestion);
    });
  }

  setMeter(result.score, result.rating.toLowerCase());
  showRadar(result.breach || checker.emptyBreach());
}

function updateCharacterCount(password) {
  const count = checker.characterCount(password);
  characterCountText.textContent = checker.charactersLabel(count);
  if (count > checker.getSettings().max_length) {
    characterCountText.className = "count over";
  } else {
    characterCountText.className = "count";
  }
}

async function runCheck(password, options) {
  const token = ++requestToken;
  const local = checker.evaluatePassword(password);

  if (!local.ok) {
    if (token === requestToken) {
      showError(local.error);
    }
    return;
  }

  // Show the local rating immediately, then fill in the radar.
  if (token === requestToken) {
    showResult(
      Object.assign({}, local, {
        breach: {
          checked: false,
          compromised: false,
          breach_count: 0,
          error: "Scanning Have I Been Pwned...",
          prefix: "",
        },
      })
    );
  }

  const breach = await hibp.checkPassword(password, checker.getSettings());
  if (token !== requestToken) {
    return;
  }

  const finalResult = checker.applyBreachResult(local, breach, password);
  showResult(finalResult);

  if (options && options.moveFocus) {
    moveFocusToResult();
  }
}

function update(options) {
  const password = passwordInput.value;
  updateCharacterCount(password);

  if (password === "") {
    if (options.fromButton) {
      showError("A password cannot be empty or made of only spaces.");
    } else {
      showIdle();
    }
    return;
  }

  runCheck(password, options);
}

function moveFocusToResult() {
  if (analysis.hidden) {
    feedback.focus();
    return;
  }
  analysis.focus();
}

function scheduleCheck() {
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(function () {
    update({ fromButton: false, moveFocus: false });
  }, 550);
}

passwordInput.addEventListener("input", function () {
  updateCharacterCount(passwordInput.value);
  if (passwordInput.value === "") {
    requestToken = requestToken + 1;
    showIdle();
    return;
  }
  scheduleCheck();
});

passwordInput.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    window.clearTimeout(debounceTimer);
    update({ fromButton: true, moveFocus: true });
  }
});

checkButton.addEventListener("click", function () {
  window.clearTimeout(debounceTimer);
  update({ fromButton: true, moveFocus: true });
});

clearButton.addEventListener("click", function () {
  window.clearTimeout(debounceTimer);
  requestToken = requestToken + 1;
  passwordInput.value = "";
  passwordInput.type = "password";
  toggleButton.textContent = "Show";
  toggleButton.setAttribute("aria-pressed", "false");
  showIdle();
  passwordInput.focus();
});

toggleButton.addEventListener("click", function () {
  const willShow = passwordInput.type === "password";
  passwordInput.type = willShow ? "text" : "password";
  toggleButton.textContent = willShow ? "Hide" : "Show";
  toggleButton.setAttribute("aria-pressed", willShow ? "true" : "false");
  passwordInput.focus();
});

sampleButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    passwordInput.value = button.getAttribute("data-sample");
    passwordInput.type = "text";
    toggleButton.textContent = "Hide";
    toggleButton.setAttribute("aria-pressed", "true");
    window.clearTimeout(debounceTimer);
    update({ fromButton: false, moveFocus: false });
    passwordInput.focus();
  });
});

async function boot() {
  try {
    const response = await fetch("config.json", { cache: "no-store" });
    if (response.ok) {
      const loaded = await response.json();
      checker.mergeSettings(loaded);
    } else {
      checker.mergeSettings({});
    }
  } catch (error) {
    checker.mergeSettings({});
  }

  const settings = checker.getSettings();
  if (thresholdNote) {
    thresholdNote.textContent =
      "Thresholds: min length " +
      settings.min_length +
      ", Weak if score ≤ " +
      settings.weak_max_passed_checks +
      ", Moderate if score ≥ " +
      settings.moderate_min_passed_checks +
      ", Strong if score ≥ " +
      settings.strong_min_passed_checks +
      ". Edit public/config.json to change them.";
  }

  showIdle();
}

boot();
