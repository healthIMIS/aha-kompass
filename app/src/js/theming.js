/*
 Theming JS for CoWhere
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

import my from './my.js';
import statusbar from './statusbar.js';

let theming = {
  isDarkMode: function() {
    return new Promise(function(resolve) {
      NativeStorage.getItem("darkModePreference", function(result) {
        if (result == "dark") {
          resolve(true);
        } else if (result == "light") {
          resolve(false);
        } else {
          resolve(window.matchMedia("(prefers-color-scheme: dark)").matches);
        }
      }, function(error) {
        console.log("[UserPreferences] Failed to load dark mode preference.");
        this.setPreference("system");
        resolve(window.matchMedia("(prefers-color-scheme: dark)").matches);
      }.bind(this));
    }.bind(this));
  },
  setPreference: function(preference) {
    NativeStorage.setItem("darkModePreference", preference, function(result) {
      this.apply();
      console.log("[UserPreferences] Successfully stored dark mode preference.");
    }.bind(this), function(error) {
      console.log("[UserPreferences] Failed to store dark mode preference.");
    })
  },
  getPreference: function() {
    return new Promise(function(resolve) {
      NativeStorage.getItem("darkModePreference", function(result) {
        resolve(result);
      }, function(error) {
        console.log("[UserPreferences] Failed to load dark mode preference. Will restore default.");
        this.setPreference("system");
        resolve("system");
      }.bind(this));
    }.bind(this));
  },
  apply: function() {
    this.isDarkMode().then(function(result) {
      statusbar.reset();
      if (result) {
        document.documentElement.classList.add("theme-dark");
      } else {
        document.documentElement.classList.remove("theme-dark");
      }
    });
  }
}

export default theming;
