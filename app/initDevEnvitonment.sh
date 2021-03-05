#!/bin/bash

# Load framework7 dependencies.
npm install

# Create empty www folder. Required to make cordova happy.
mkdir cordova/www

# Setup local cordova project.
cd cordova
cordova prepare
cd ../
