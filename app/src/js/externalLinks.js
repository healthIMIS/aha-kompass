/*
 External link handler
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */
import environment from '../js/environment.js';

let links = {
  open: function(href) {
    if (environment.isCordova()) {
      SafariViewController.isAvailable(function (available) {
        if (available) {
          linkHandlers.openSafariViewController(href);
        } else {
          linkHandlers.openSystemBrowser(href);
        }
      });
    } else {
      linkHandlers.openNewTab(href);
    }
  }
}

let linkHandlers = {
  openSafariViewController: function(href) {
    SafariViewController.show({
      url: href
    }, function(result) {
      return;
    }, function(error) {
      console.log("[ExternalLinkHandler] Unable to open SafariViewController.");
    });
  },
  openSystemBrowser: function(href) {
    window.open(href, '_system');
  },
  openNewTab: function(href) {
    window.open(href, "_blank");
  }
}

export default links;
