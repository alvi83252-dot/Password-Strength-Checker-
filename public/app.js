"use strict";

/*
  Page behavior for the password checker.

  checker.js decides the rating. This file only reads the text box
  and updates the page. It does not send the password anywhere.
*/

const checker = window.passwordChecker;
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

function clearElement(element) {
  // textContent removes old items without interpreting them as HTML.
  element.textContent = "";
}

function addTextItem(list, text, className) {
  const item = document.createElement("li");
  if (className) {
    item.className = className;
  }
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
  // Drop the previous rating so a cleared box cannot keep showing it.
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
}

function showIdle() {
  feedback.className = "feedback";
  feedback.textContent = "Enter a password to see its strength.";
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
  // textContent is deliberate. A password explanation is text, not HTML.
  text.textContent = detail.text;

  item.appendChild(mark);
  item.appendChild(text);
  detailsList.appendChild(item);
}

function showResult(result) {
  feedback.className = "feedback";
  feedback.textContent = "";
  passwordInput.setAttribute("aria-invalid", "false");
  analysis.hidden = false;
  analysis.dataset.rating = result.rating.toLowerCase();

  if (result.is_common) {
    flag.hidden = false;
    flag.textContent = "Commonly leaked password";
  } else if (!result.checks.length) {
    flag.hidden = false;
    flag.textContent = "Shorter than 8 characters";
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
  if (result.rating === "Strong") {
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
}

function updateCharacterCount(password) {
  const count = checker.characterCount(password);
  characterCountText.textContent = checker.charactersLabel(count);
  if (count > checker.MAX_PASSWORD_LENGTH) {
    characterCountText.className = "count over";
  } else {
    characterCountText.className = "count";
  }
}

function update(options) {
  const password = passwordInput.value;
  updateCharacterCount(password);

  if (password === "") {
    // Clicking Check on an empty box should explain the problem.
    // Deleting the text should return to the quiet starting hint.
    if (options.fromButton) {
      showError("A password cannot be empty or made of only spaces.");
    } else {
      showIdle();
    }
    return;
  }

  showResultOrError(checker.evaluatePassword(password));
}

function showResultOrError(result) {
  if (!result.ok) {
    showError(result.error);
    return;
  }
  showResult(result);
}

function moveFocusToResult() {
  if (analysis.hidden) {
    feedback.focus();
    return;
  }
  analysis.focus();
}

passwordInput.addEventListener("input", function () {
  update({ fromButton: false });
});

passwordInput.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    event.preventDefault();
    update({ fromButton: true });
    moveFocusToResult();
  }
});

checkButton.addEventListener("click", function () {
  update({ fromButton: true });
  moveFocusToResult();
});

clearButton.addEventListener("click", function () {
  passwordInput.value = "";
  passwordInput.type = "password";
  toggleButton.textContent = "Show";
  toggleButton.setAttribute("aria-pressed", "false");
  update({ fromButton: false });
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
    // Samples are easier to read while the letters are visible.
    passwordInput.type = "text";
    toggleButton.textContent = "Hide";
    toggleButton.setAttribute("aria-pressed", "true");
    update({ fromButton: false });
    passwordInput.focus();
  });
});

update({ fromButton: false });
