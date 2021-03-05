/*
 Geolocation and preference helper functions
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let geolocation = {
  get: function() {
    return new Promise(function(resolve) {
      NativeStorage.getItem("locationPermission", function(obj) {
        if (obj == "true") {
          resolve(true);
        } else if (obj == "false") {
          resolve(false);
        } else {
          resolve(false);
        }
      }, function(error) {
        console.log("[UserPreferences] Unable to read location permission setting.");
      });
    });
  },
  getWithLastDistrict: function() {
    return new Promise(function(resolve) {
      NativeStorage.getItem("locationPermission", function(obj) {
        if (obj == "true") {
          resolve(true);
        } else if (obj == "false") {
          NativeStorage.getItem("lastViewedDistrict", function(obj) {
            resolve(obj);
          }, function(error) {
            console.log("[UserPreferences] Unable to get last viewed district.");
            resolve(false);
          });
        } else {
          resolve(false);
        }
      }, function(error) {
        console.log("[UserPreferences] Unable to read location permission setting.");
      });
    });
  },
  set: function(mode) {
    let value = mode ? "true" : "false";
    NativeStorage.setItem("locationPermission", value, function(obj) {
      console.log("[UserPreferences] Successfully updated location permission setting.");
    }, function(error) {
      console.log("[UserPreferences] Unable to set location permission.");
    });
  },
  setLastLocation: function(id) {
    NativeStorage.setItem("lastViewedDistrict", id, function(obj) {
      console.log("[UserPreferences] Successfully updated last viewed district.");
    }, function (error) {
      console.log("[UserPreferences] Unable to set last viewed district.");
    })
  }
}

export default geolocation;
