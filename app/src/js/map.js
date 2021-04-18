/*
 Map JS for CoWhere
 © 2020 - 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */
var L = require('leaflet');
const safeAreaInsets = require('safe-area-insets');
const leafBound = require('leaflet-boundary-canvas');

import filesystem from './filesystem.js';
import api from './api.js';
import my from './my.js';
import resizeEndEvent from './resizeEndEvent.js';

class map {
  constructor(container, selectionCallback, loadCallback, deselectionCallback, cityCallback) {
    this.container = container;
    this.selectionCallback = selectionCallback;
    this.deselectionCallback = deselectionCallback;
    this.loadCallback = loadCallback;
    this.cityCallback = cityCallback;
    this.bounds = null;
    this.districtData = null;
    this.center = [50.80, 10.50];
    this.initialZoom = null;
    this.selected = -1;
    this.clicked = false;
    this.desktopMargin = 0;
    this.specialCities = [];
    this.lastClick = Date.now();
    this.updateMapData();
    this.locationMarker = L.icon({
      iconUrl: "static/img/position.svg",
      iconSize:     [30, 30], // size of the icon
      iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
      popupAnchor:  [0, -20] // point from which the popup should open relative to the iconAnchor
    });
    this.map = L.map(this.container, {
      zoomControl: false,
      attributionControl: true,
      maxBounds: this.bounds,
      maxBoundsViscosity: 0.3,
      center: this.center,
      zoom: this.initialZoom,
      zoomSnap: 0,
      preferCanvas: true,
    });
    this.loadGermany();
    this.loadStates();
    this.loadDistrictData();
    this.isResizing = false;
    window.addEventListener('resize', function() {
      this.isResizing = true;
    }.bind(this));
    this.resizeEndEvent = new resizeEndEvent(this.resizeEvent.bind(this));
    if (!this.isMobile()) {
      this.map.on('zoomstart', this.mapMoveEvent.bind(this));
      L.DomEvent.on(this.map.getContainer(), 'mouseup', function() {
        this.clicked = false;
      }.bind(this));
      L.DomEvent.on(this.map.getContainer(), 'mousedown', function() {
        this.clicked = true;
      }.bind(this));
      L.DomEvent.on(this.map.getContainer(), 'mousemove', function() {
        if (this.clicked) {
          this.mapMoveEvent();
        }
      }.bind(this));
    }
  }

  // DATA HANDLING
  // Load geo.json to get district id, name and polygon bounds
  loadDistrictData() {
    filesystem.readFromAppDir("www/static/data/geo.json").then(function(result) {
      this.districtData = JSON.parse(result);
      this.renderDistricts();
    }.bind(this));
  }
  // Render districts to map
  renderDistricts() {
    for (const id in this.districtData) {
      this.districtData[id]["polygon"] = L.polygon(this.districtData[id].geo, {color: "black", fillColor: "blue", fillOpacity: 0.8, weight: 2}).addTo(this.map).on('click', function(e) {
        if (this.lastClick + 80 < Date.now()) { // Fix double fire on click
          this.lastClick = Date.now();
          this.districtSelection(id);
        }
      }.bind(this));
    }
    this.bringStatesToFront();
    this.loadCallback();
  }
  // Set color for district
  setDistrictColor(id, color) {
    this.districtData[id].polygon.setStyle({fillColor: color});
  }
  // Get PLZ list for district
  getPlz(id) {
    return this.districtData[id].plz;
  }
  // Get city list for district
  getCities(id) {
    return this.districtData[id].cities;
  }
  // Load germany polygon data
  loadGermany() {
    filesystem.readFromAppDir("www/static/data/germany.json").then(function(result) {
      this.germany = JSON.parse(result);
      let layer = new L.TileLayer.BoundaryCanvas("static/tiles/{z}/{x}/{y}.jpg", {
        maxZoom: 10,
        minZoom: 6,
        maxNativeZoom: 9,
        minNativeZoom: 7,
        attributionControl: false,
        boundary: this.germany
      }).addTo(this.map);
      this.districtViewAnimate(false);
    }.bind(this));
  }
  // Load german states
  loadStates() {
    filesystem.readFromAppDir("www/static/data/states.json").then(function(result) {
      this.states = JSON.parse(result);
      for (const state in this.states) {
        this.states[state]["polyline"] = L.polyline(this.states[state].geo, {color: "black", weight: 4}).addTo(this.map);
      }
    }.bind(this));
  }

  // DISTRICT SELECTION
  // Callback for district click
  districtSelection(id) {
    this.selectionCallback(id);
  }
  // Render animation bringing given district to swisher-open area
  districtViewAnimate(id) {
    let desktopMargin = (id == false) ? 10 : this.desktopMargin;
    let bounds = (id == false) ? L.geoJson(this.germany).getBounds() : this.districtData[id].polygon.getBounds();
    let navbarHeight = document.getElementsByClassName("navbar-map")[0].getBoundingClientRect().height;
    let swisherWidth = document.getElementById("swisher-container").getBoundingClientRect().width;
    let leafletContainerHeight = window.innerHeight - safeAreaInsets.bottom - navbarHeight;
    let right = this.isMobile() ? 10 : swisherWidth + 10 + desktopMargin;
    let bottom = this.isMobile() ? leafletContainerHeight - 190 : desktopMargin;
    let left = this.isMobile() ? 10 : desktopMargin;
    let top = this.isMobile() ? 10 : desktopMargin;
    if (this.isMobile() && id == false) {
      bottom -= (leafletContainerHeight - 300);
    }
    this.map.invalidateSize();
    this.map.flyToBounds(bounds, {
      paddingTopLeft: [left, top],
      paddingBottomRight: [right, bottom],
      duration: 0.5
    });
    if (id != false) {
      this.focusDistrict(id);
    }
    this.bringStatesToFront();
  }
  // Focus one district
  focusDistrict(id) {
    if (id != false) {
      this.selected = id;
    }
    for (const districtId in this.districtData) {
      if (districtId != id) {
        this.districtData[districtId].polygon.setStyle({weight: 1, opacity: 0.7, fillOpacity: 0.7});
      } else {
        this.districtData[districtId].polygon.setStyle({weight: 4, opacity: 1, fillOpacity: 0.8});
        this.districtData[districtId].polygon.bringToFront();
      }
    }
    this.stateVisibility(false);
  }
  // Show all district borders
  showAllBorders() {
    this.selected = -1;
    for (const districtId in this.districtData) {
      this.districtData[districtId].polygon.setStyle({weight: 2, opacity: 1, fillOpacity: 0.8});
    }
    this.stateVisibility(true);
    this.bringStatesToFront();
    this.clearSpecialCities();
  }
  // Show full map
  showFullMap() {
    this.districtViewAnimate(false);
  }
  // Bring states to front
  bringStatesToFront() {
    for (const state in this.states) {
      this.states[state].polyline.bringToFront();
    }
  }
  // Show / Hide states
  stateVisibility(mode) {
    const opacity = mode ? 1 : 0;
    for (const state in this.states) {
      this.states[state].polyline.setStyle({opacity: opacity});
    }
  }
  // Re-Run positioning on resize
  resizeEvent() {
    this.updateMapData();
    this.map.setMaxBounds(this.bounds);
    this.map.invalidateSize();
    setTimeout(function() {
      if (this.selected >= 0) {
        this.districtViewAnimate(this.selected);
        if (this.isMobile()) {
          this.disable();
        }
      } else {
        this.showFullMap();
      }
      if (!this.isMobile()) {
        this.enable();
      }
      this.isResizing = false;
    }.bind(this), 300);
  }
  // Update map data (bounds, zoom levels, ...) depending on screen dimensions
  updateMapData() {
    this.bounds = this.isMobile() ? [[56.00000, 4.570312], [43.52794, 16.56676]] : [[55.50000, -2.570312], [47.00000, 31]];
    this.initialZoom = this.isMobile() ? 6 : 7.5;
    this.desktopMargin = (window.innerWidth > 1200) ? 200 : 100;
  }
  // Render cities with different rules
  renderSpecialCities(data, districtId) {
    // Find the correct polygon
    let polygon;
    for (const districtId in this.districtData) {
      if (districtId == this.selected) {
        polygon = this.districtData[districtId].polygon;
      }
    }
    for (const city of data) {
      let popup = L.popup({closeButton: false, autoClose: false, closeOnEscapeKey: false, className: "popup-not-selected"})
        .setLatLng([city.position[1], city.position[0]])
        .setContent("<span class=\"map-popup\">" + city.name + "</span>");
      this.map.addLayer(popup);
      this.specialCities.push({popup: popup, name: city.name});
      popup._container.addEventListener("click", function(e) {
        this.cityCallback(city.code);
      }.bind(this));
    }
  }
  // Clear cities with different rules
  clearSpecialCities() {
    for (const popup of this.specialCities) {
      popup.popup.remove();
    }
    this.specialCities = [];
  }
  // Focus a special city
  focusCity(name) {
    for (const popup of this.specialCities) {
      if (name == popup.name) {
        // Dirty solution (private var) but works
        popup.popup._container.classList.remove("popup-not-selected");
        popup.popup.bringToFront();
      }
    }
  }

  // POINT POLYGON RELATIONSHIP
  // Find different
  findDistrictOfPoint(latitude, longitude) {
    for (const districtId in this.districtData) {
      let polygon = this.districtData[districtId].polygon.getLatLngs();
      let first = true;
      let isInside = false;
      for (const polyPoints of polygon) {
        let inside = false;
        for (var i = 0, j = polyPoints.length - 1; i < polyPoints.length; j = i++) {
          let xi = polyPoints[i].lat;
          let yi = polyPoints[i].lng;
          let xj = polyPoints[j].lat;
          let yj = polyPoints[j].lng;
          let intersect = ((yi > longitude) != (yj > longitude)) && (latitude < (xj - xi) * (longitude - yi) / (yj - yi) + xi);
          if (intersect) {
            inside = !inside;
          }
        }
        if (first) {
          isInside = inside;
        } else if (isInside && inside) {
          isInside = false;
        }
        first = false;
      }
      if (isInside) {
        return districtId;
      }
    }
  }

  // USER INTERACTION
  // Disable map movement
  disable() {
    if (this.isMobile()) {
      this.map.dragging.disable();
      this.map.scrollWheelZoom.disable();
      this.map.touchZoom.disable();
    }
  }
  // Enable map movement
  enable() {
    this.map.dragging.enable();
    this.map.scrollWheelZoom.enable();
    this.map.touchZoom.enable();
  }
  // Detect mobile environment
  isMobile() {
    return window.innerWidth <= 1000;
  }
  // Show all districts on desktop on map move
  mapMoveEvent() {
    if (this.selected >= 0 && !this.isMobile() && !this.isResizing) {
      this.showAllBorders();
      this.deselectionCallback();
    }
  }

  // GPS POSITION
  initGpsRetrieval() {
    if (this.watcher == null) {
      this.watcher = navigator.geolocation.watchPosition(this.gotGps.bind(this), this.gpsError.bind(this), {timeout: 3000, enableHighAccuracy: false});
    }
  }
  gotGps(position) {
    if (this.circle != null){
      this.circle.remove();
    }
    if (this.point != null){
      this.point.remove();
    }
    this.circle = L.circle([position.coords.latitude, position.coords.longitude], {
      stroke: false,
      fillColor: 'blue',
      fillOpacity: 0.3,
      radius: position.coords.accuracy
    }).addTo(this.map);
    this.point = L.marker([position.coords.latitude, position.coords.longitude], {
    icon: this.locationMarker,
      zIndexOffset: -1000,
    }).addTo(this.map);
  }
  gpsError(error) {
    console.log('[GeolocationEngine] Error retrieving position. Code: ' + error.code + '; message: ' + error.message + '.');
  }
}

export default map;
