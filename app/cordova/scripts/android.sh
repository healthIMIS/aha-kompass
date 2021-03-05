 #!/bin/bash

rm -R platforms/android/app/src/main/res/drawable-* # Delete cordova splash screens
rm -R platforms/android/app/src/main/res/mipmap-* # Delete cordova default icons
cp -R icons/android/res/* platforms/android/app/src/main/res/ # Copy dislogshift icons
