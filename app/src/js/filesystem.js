/*
 File system functions for CoWhere
 © 2020 - 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */
import api from './api.js';
import environment from '../js/environment.js';

let filesystem = {
  readFromAppDir: function(path) {
    return new Promise(function(resolve, reject) {
      if (environment.isCordova()) { // In cordova environment, use filesystem; in browser use ajax
        window.resolveLocalFileSystemURL(cordova.file.applicationDirectory + path, function(fileEntry) {
          fileEntry.file(function (file) {
            var reader = new FileReader();
            reader.onloadend = function() {
              console.log("[MapEngine] Successful read geo data file.");
              resolve(this.result);
            };
            reader.readAsText(file);
          }, function(err) {
            console.log("[MapEngine] Error reading geo data file: " + err);
            reject(err);
          });
        }, function(err) {
          console.log("[MapEngine] Error getting geo data file: " + err);
          reject(err);
        });
      } else {
        let ajaxPath = path.replace("www", "");
        api.send(window.location.origin + ajaxPath, "GET", {}, {disableBaseDomain: true}).then(function(response) {
          resolve(response);
        });
      }
    });
  }
}

export default filesystem;
