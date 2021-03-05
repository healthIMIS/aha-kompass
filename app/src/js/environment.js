/*
 Environment checks for CoWhere.
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let environment = {
  isCordova: function() {
    return typeof window.cordova !== "undefined";
  },
  httpPlugin: function() {
    return this.isCordova() && typeof window.cordova.plugin !== "undefined" && typeof window.cordova.plugin.http !== "undefined";
  }
}

export default environment;
