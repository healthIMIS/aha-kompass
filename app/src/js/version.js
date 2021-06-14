/*
 Version number functions for CoWhere.
 © 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */

import {version as appVersion} from '../../package.json';
import timeparse from './timeparse.js';

let version = {
  version: "",
  platform: "",
  init: function() {
    this.version = appVersion;
  },
  get: function(key) {
    switch(key) {
      case "version":
        return this.version;
      case "platform":
        return this.platform;
    }
  },
  setPlatform: function(value) {
    this.platform = value;
  }
}

export default version;
