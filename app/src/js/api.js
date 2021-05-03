/*
 API JS for CoWhere.
 © 2020 - 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */
import environment from './environment.js';
import my from './my.js';
import language from './language.js';

let endpointConfig = {
  baseDomain: "https://aha-kompass.de",
  useBaseDomainInWeb: false // Set this to true for browser testing with an external api server
}

let api = {
  send: function(url, type, data, requestOptions = {disableBaseDomain: false, formData: false, disableLanguage: false}) {
    return new Promise(function(resolve, reject) {
      if (!requestOptions.disableLanguage) data["language"] = language.selector();
      if (environment.httpPlugin()) { // Use cordova-plugin-advanced-http
        if (!requestOptions.disableBaseDomain) url = endpointConfig.baseDomain + url;
        let options = {}
        if (type == "GET") {
          let params = "";
          for (let key in data) {
            if (params != "") {
              params += "&";
            }
            params += key + "=" + data[key];
          }
          url += "?" + params;
        } else {
          options["data"] = data;
        }
        switch(type) {
          case "POST":
            options["method"] = "post";
            break;
          case "GET":
            options["method"] = "get";
            break;
          case "PUT":
            options["method"] = "put";
            break;
          case "DELETE":
            options["method"] = "delete";
            break;
        }
        cordova.plugin.http.sendRequest(url, options, function(response) {
          resolve(response.data, response.status);
        }, function(response) {
          this.processError(response.status, response.error);
        }.bind(this));
      } else { // Use AJAX
        if (endpointConfig.useBaseDomainInWeb && !requestOptions.disableBaseDomain) {
          url = endpointConfig.baseDomain + url;
        }
        let request = new XMLHttpRequest;
        request.addEventListener("load", function(event) {
          if (event.target.status >= 200 && event.target.status < 300) {
            resolve(event.target.responseText, event.target.status);
          } else {
            this.processError(event.target.status, event.target.responseText);
          }
        }.bind(this));
        request.addEventListener("error", function(event) {
          this.processError(event.target.status, event.target.responseText);
        }.bind(this));
        let requestData = null;
        if (requestOptions.formData) {
          requestData = new FormData();
          for (let key in data) {
            requestData.append(key, data[key])
          }
        } else if (type == "GET") {
          let params = "";
          for (let key in data) {
            if (params != "") {
              params += "&";
            }
            params += key + "=" + data[key];
          }
          if (params != "") url += "?" + params;
        } else {
          requestData = "";
          for (let key in data) {
            if (requestData != "") {
              requestData += "&";
            }
            requestData += key + "=" + data[key];
          }
          request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        }
        request.open(type, url, true);
        request.send(requestData);
      }
    }.bind(this));
  },
  processError: function(code, data) {
    my.app.preloader.hide();
    my.app.dialog.close();
    if (code == 404) {
      this.fire404Error();
    } else if (code == 503) {
      my.app.popup.open(".popup-maintenance");
    } else if (code == 403) {
      this.fire403Error();
    } else {
      this.fallbackError();
    }
  },
  fireBackendConnectionError: function() {
    my.app.dialog.alert(language.helper('errors.backend'));
  },
  fire404Error: function() {
    my.app.dialog.alert(language.helper('errors.notfound'));
  },
  fire403Error: function() {
    my.app.dialog.alert(language.helper('errors.forbidden'), "AHA-Kompass", function() {
      window.location.href = "/";
    });
  },
  fallbackError: function() {
    my.app.dialog.alert(language.helper('errors.fallback'));
  }
}

export default api;
