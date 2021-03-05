#!/bin/bash

rm -R platforms/ios/AHA-Kompass/Images.xcassets/LaunchImage.launchimage # Remove lanuch image set (hopeless outdated)
cp -R icons/ios/LaunchImage.launchimage platforms/ios/AHA-Kompass/Images.xcassets/ # Copy empty launch image set to make xcode happy
#rm -R platforms/ios/AHA-Kompass/Images.xcassets/LaunchStoryboard.imageset # Remove launch stroyboard image set (cordovas "workaround" for newer ios version launch images)
rm -R platforms/ios/AHA-Kompass/Images.xcassets/AppIcon.appiconset # Remove default icon set
#rm -R platforms/ios/AHA-Kompass/CDVLaunchScreen.storyboard # Remove cordova default launch screen stroyboard
cp -R icons/ios/AppIcon.appiconset platforms/ios/AHA-Kompass/Images.xcassets/ # Copy app icon set
#mkdir platforms/ios/AHA-Kompass/Resources
cp -R icons/ios/LaunchScreen.storyboard platforms/ios/AHA-Kompass/Resources/ # Copy launch screen file
cp -R icons/ios/launchicon.png platforms/ios/AHA-Kompass/Resources/ # Copy launch screen image set

node scripts/ios-infoplist.js

node scripts/ios-prepare-xcodeproject.js