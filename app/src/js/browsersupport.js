/*
 BrowserSupport JS for CoWhere.
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let detectors = {
  ie10OrLower: function() {
    return window.navigator.userAgent.indexOf('MSIE ') > 0;
  },
  ie11: function() {
    return window.navigator.userAgent.indexOf('Trident/') > 0;
  },
  edgeOld: function() {
    return window.navigator.userAgent.indexOf("Edge/") > 0;
  }
}

let browsersupport = {
  isSupported: function() {
    return !detectors.ie10OrLower() && !detectors.ie11() && !detectors.edgeOld();
  }
}

export default browsersupport;
