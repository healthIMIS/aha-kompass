/*
 Language selection helper functions
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

import my from './my.js';

let language = {
  available: ["de-de"],
  importer: function() {
    for (const lang of this.available) {
      require('../lang/' + lang + '.js');
    }
  },
  selector: function() {
    for (const lang of this.available) {
      if (lang == my.app.language) {
        return lang;
      }
    }
    return "de-de";
  },
  helper: function(value) {
    let path = value.split(".");
    let data = window.localizations[this.selector()];
    for (const key of path) {
      data = data[key];
    }
    return data;
  }
}

export default language;
