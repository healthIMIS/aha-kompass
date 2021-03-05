/*
 Favourite storage functions for CoWhere
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let favourites = {
  add: function(id) {
    return new Promise(function(resolve, reject) {
      NativeStorage.getItem("favouriteDistricts", function(obj) {
        let oldList = JSON.parse(obj);
        oldList.push(id);
        favouritesPrivate.store(oldList).then(function() {
          resolve();
        });
      }.bind(this), function(error) {
        console.log("[FavouriteManager] Failed to read stored favourites. Creating new list.");
        favouritesPrivate.store([id]).then(function() {
          resolve();
        });
      }.bind(this));
    }.bind(this));
  },
  delete: function(id) {
    return new Promise(function(resolve, reject) {
      NativeStorage.getItem("favouriteDistricts", function(obj) {
        let oldList = JSON.parse(obj);
        oldList.splice(oldList.indexOf(id), 1);
        favouritesPrivate.store(oldList).then(function() {
          resolve();
        });
      }.bind(this), function(error) {
        console.log("[FavouriteManager] Failed to read stored favourites. Creating empty list.");
        favouritesPrivate.store([]).then(function() {
          resolve();
        });
      }.bind(this));
    }.bind(this));
  },
  get: function() {
    return new Promise(function(resolve, reject) {
      NativeStorage.getItem("favouriteDistricts", function(obj) {
        resolve(JSON.parse(obj));
      }, function(error) {
        console.log("[FavouriteManager] Failed to read stored favourites.");
        reject();
      });
    });
  }
}

let favouritesPrivate = {
  store: function(list) {
    return new Promise(function(resolve, reject) {
      NativeStorage.setItem("favouriteDistricts", JSON.stringify(list), function(obj) {
        console.log("[FavouriteManager] Successfully updated favourite district list.");
        resolve();
      }, function(error) {
        console.log("[FavouriteManager] Failed to update favourite district list.");
        reject();
      });
    }.bind(this));
  },
}

export default favourites;
