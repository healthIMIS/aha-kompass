const xcode = require("xcode");
const fs = require("fs");

const PROJECTPATH = "platforms/ios/AHA-Kompass.xcodeproj/project.pbxproj";

const project = xcode.project(PROJECTPATH);

project.parse(function (err) {
  project.removeResourceFile("CDVLaunchScreen.storyboard");
  project.addResourceFile("LaunchScreen.storyboard");
  project.addResourceFile("launchicon.png");
  fs.writeFileSync(PROJECTPATH, project.writeSync());
});