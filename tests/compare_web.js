"use strict";

// Reads a JSON list of passwords from stdin and writes the web checker's
// results as JSON. The Python tests compare that output with password_checker.py.

const fs = require("fs");
const path = require("path");
const checker = require(path.join(__dirname, "..", "public", "checker.js"));

const cases = JSON.parse(fs.readFileSync(0, "utf8"));
const output = cases.map(function (password) {
  return checker.evaluatePassword(password);
});

process.stdout.write(JSON.stringify(output));
