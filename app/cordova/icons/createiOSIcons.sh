#!/bin/bash

# iOS
IOSFOLDER="ios/AppIcon.appiconset"
mkdir $IOSFOLDER

# Create required icon files
cp icon-1024.png $IOSFOLDER/icon-1024.png
cp icon-1024.png $IOSFOLDER/icon-83.5@2x.png
cp icon-1024.png $IOSFOLDER/icon-76.png
cp icon-1024.png $IOSFOLDER/icon-76@2x.png
cp icon-1024.png $IOSFOLDER/icon-20.png
cp icon-1024.png $IOSFOLDER/icon-40.png
cp icon-1024.png $IOSFOLDER/icon-40@2x.png
cp icon-1024.png $IOSFOLDER/icon-29.png
cp icon-1024.png $IOSFOLDER/icon-29@2x.png
cp icon-1024.png $IOSFOLDER/icon-29@3x.png
cp icon-1024.png $IOSFOLDER/icon-60.png
cp icon-1024.png $IOSFOLDER/icon-60@2x.png
cp icon-1024.png $IOSFOLDER/icon-60@3x.png

# Scale images
sips -Z 167 $IOSFOLDER/icon-83.5@2x.png
sips -Z 76 $IOSFOLDER/icon-76.png
sips -Z 152 $IOSFOLDER/icon-76@2x.png
sips -Z 20 $IOSFOLDER/icon-20.png
sips -Z 40 $IOSFOLDER/icon-40.png
sips -Z 80 $IOSFOLDER/icon-40@2x.png
sips -Z 29 $IOSFOLDER/icon-29.png
sips -Z 58 $IOSFOLDER/icon-29@2x.png
sips -Z 87 $IOSFOLDER/icon-29@3x.png
sips -Z 60 $IOSFOLDER/icon-60.png
sips -Z 120 $IOSFOLDER/icon-60@2x.png
sips -Z 180 $IOSFOLDER/icon-60@3x.png

# Write Contents.json
cat > $IOSFOLDER/Contents.json << EOF
{
  "images" : [
    {
      "size" : "20x20",
      "idiom" : "iphone",
      "filename" : "icon-40.png",
      "scale" : "2x"
    },
    {
      "size" : "20x20",
      "idiom" : "iphone",
      "filename" : "icon-60.png",
      "scale" : "3x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "filename" : "icon-29@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "29x29",
      "idiom" : "iphone",
      "filename" : "icon-29@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "filename" : "icon-40@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "iphone",
      "filename" : "icon-60@2x.png",
      "scale" : "3x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "filename" : "icon-60@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "60x60",
      "idiom" : "iphone",
      "filename" : "icon-60@3x.png",
      "scale" : "3x"
    },
    {
      "size" : "20x20",
      "idiom" : "ipad",
      "filename" : "icon-20.png",
      "scale" : "1x"
    },
    {
      "size" : "20x20",
      "idiom" : "ipad",
      "filename" : "icon-40.png",
      "scale" : "2x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "filename" : "icon-29.png",
      "scale" : "1x"
    },
    {
      "size" : "29x29",
      "idiom" : "ipad",
      "filename" : "icon-29@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "filename" : "icon-40.png",
      "scale" : "1x"
    },
    {
      "size" : "40x40",
      "idiom" : "ipad",
      "filename" : "icon-40@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "filename" : "icon-76.png",
      "scale" : "1x"
    },
    {
      "size" : "76x76",
      "idiom" : "ipad",
      "filename" : "icon-76@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "83.5x83.5",
      "idiom" : "ipad",
      "filename" : "icon-83.5@2x.png",
      "scale" : "2x"
    },
    {
      "size" : "1024x1024",
      "idiom" : "ios-marketing",
      "filename" : "icon-1024.png",
      "scale" : "1x"
    }
  ],
  "info" : {
    "version" : 1,
    "author" : "xcode"
  }
}
EOF