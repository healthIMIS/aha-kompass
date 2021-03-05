/*
 Statusbar JS for CoWhere
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

import my from './my.js';
import theming from './theming.js';

let statusbar = {
  popupOpen: false,
  reset: function() {
    theming.isDarkMode().then(function(isDarkMode) {
      if (device.platform == "iOS") {
        if (isDarkMode) {
          setTimeout(function() {
            StatusBar.styleLightContent();
          }, 500);
        } else if (!this.popupOpen) {
          setTimeout(function() {
            StatusBar.styleDefault();
          }, 500);
        }
      } else {
        if (isDarkMode) {
          setTimeout(function() {
            StatusBar.backgroundColorByHexString("#000");
            StatusBar.styleLightContent();
          }, 500);
        } else {
          setTimeout(function() {
            StatusBar.backgroundColorByHexString("#EEE");
            StatusBar.styleDefault();
          }, 500);
        }
      }
    }.bind(this));
  },
  registerPopupEvents: function() {
    if (device.platform == "iOS") {
      my.app.on("popupOpen", function(popup) {
        theming.isDarkMode().then(function(result) {
          this.popupOpen = true;
          if (!result) {
            setTimeout(function() {
              StatusBar.styleLightContent();
            }, 200);
          }
        }.bind(this));
      }.bind(this));
      my.app.on("popupClose", function(popup) {
        theming.isDarkMode().then(function(result) {
          this.popupOpen = false;
          if (!result) {
            setTimeout(function() {
              StatusBar.styleDefault();
            }, 200);
          }
        }.bind(this));
      }.bind(this));
    }
  }
}

export default statusbar;
