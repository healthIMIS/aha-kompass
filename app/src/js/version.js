/*
 Version number functions for CoWhere.
 © 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */

import * as appVersion from '../version.json';
import timeparse from './timeparse.js';

let version = {
  version: "",
  build: "",
  compile: "",
  platform: "",
  init: function() {
    const countAtNewVersion = 0;
    const compileDate = new Date(appVersion.buildDate);
    const versionParts = appVersion.version.split(".");
    this.version = appVersion.version;
    this.build = versionParts[0] + "ABCDEFGHIJKLMNOPQRSTUVWYXZ".charAt(versionParts[1]) + (appVersion.numCommits - countAtNewVersion);
    this.compile = timeparse.addLeadingZeros(compileDate.getDate()) + "." + timeparse.addLeadingZeros((compileDate.getMonth() + 1)) + "." + compileDate.getFullYear() + " " + timeparse.addLeadingZeros(compileDate.getHours()) + ":" + timeparse.addLeadingZeros(compileDate.getMinutes()) + ":" + timeparse.addLeadingZeros(compileDate.getSeconds());
  },
  get: function(key) {
    switch(key) {
      case "version":
        return this.version;
      case "build":
        return this.build;
      case "compile":
        return this.compile;
      case "platform":
        return this.platform;
    }
  },
  setPlatform: function(value) {
    this.platform = value;
  }
}

export default version;
