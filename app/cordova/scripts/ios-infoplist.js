const fs = require("fs");
const plist = require("plist");

const FILEPATH = "platforms/ios/AHA-Kompass/AHA-Kompass-Info.plist";

var xml = fs.readFileSync(FILEPATH, "utf8");
var obj = plist.parse(xml);

delete obj.NSMainNibFile; // Outdated, but automatically added by cordova
delete obj["NSMainNibFile~ipad"]; // Outdated, but automatically added by cordova
obj.UIRequiresFullScreen = false; // Enable usage of slide over and split view
obj.CFBundleDevelopmentRegion = "de-DE"; // Set development language to English (United Kingdom)
obj.UILaunchStoryboardName = "LaunchScreen"; // Set launch screen file name

xml = plist.build(obj);
fs.writeFileSync(FILEPATH, xml, {encoding: "utf8"});