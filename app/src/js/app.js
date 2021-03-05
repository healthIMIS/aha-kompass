import $$ from 'dom7';
import Framework7, { getDevice } from 'framework7/bundle';

// Import F7 Styles
import 'framework7/framework7-bundle.css';
// Import custom Styles
import '../css/theme-steiger.css';
import '../css/leaflet.css';
import '../css/swisher.css';
import '../css/incidencecolors.css';

// Import Icons and App Custom Styles
import '../css/icons.css';
import '../css/app.css';
// Import Cordova APIs
import cordovaApp from './cordova-app.js';
// Import Routes
import routes from './routes.js';

// Import main app component
import App from '../app.f7.html';

// Import helpers
import environment from './environment.js';
import my from './my.js';
import language from './language.js';
import statusbar from './statusbar.js';
import browsersupport from './browsersupport.js';
import theming from './theming.js';
import version from './version.js';
import links from '../js/externalLinks.js';

if (!browsersupport.isSupported()) {
  window.location.href = "/static/browsersupport.html";
}

version.init();

// Import translations
window.localizations = {};
language.importer();

my.app = new Framework7({
  el: '#app', // App root element
  component: App, // App main component
  id: 'com.johanneskreutz.ahakompass', // App bundle ID
  name: 'AHA-Kompass', // App name
  theme: typeof(window.cordova) == "undefined" ? 'aurora' : 'auto', // Select theme automatically in cordova environment, force aurora in browser
  autoDarkTheme: !Framework7.device.cordova,

  // App routes
  routes: routes,

  // Input settings
  input: {
    scrollIntoViewOnFocus: Framework7.device.cordova && !Framework7.device.electron,
    scrollIntoViewCentered: Framework7.device.cordova && !Framework7.device.electron,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: true,
    androidOverlaysWebView: false,
  },
  on: {
    init: function() {
      var f7 = this;
      version.setPlatform(f7.device.cordova ? f7.device.os.replace("ios", "iOS").replace("android", "Android") : "Browser");
      let mainView = this.views.create(".view-main", {
        url: "/",
        browserHistory: !f7.device.cordova,
        browserHistorySeparator: "#districtRoute"
      });
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
        // Check if we have to show welcome popup
        document.addEventListener("deviceready", function() {
          NativeStorage.getItem("welcomePopupShown", function(obj) {
            return;
          }, function(error) { // Error means, we didn't set this parameter yet
            this.popup.open(".popup-welcome");
          }.bind(this));
          theming.apply();
          statusbar.registerPopupEvents();
        }.bind(this), false);
      }
    },
  },
});

window.externalLinkClick = links.open;
