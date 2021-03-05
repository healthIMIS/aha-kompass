/*
 Incidence color helper functions
 © 2020 - 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let incidence = {
  classes: ["color-incidence-500-up", "color-incidence-251-500", "color-incidence-101-250", "color-incidence-51-100", "color-incidence-6-50", "color-incidence-1-5", "color-incidence-0"],
  colorClass: function(value) {
    if (value >= 500) {
      return "color-incidence-500-up";
    } else if (value > 250) {
      return "color-incidence-251-500";
    } else if (value > 100) {
      return "color-incidence-101-250";
    } else if (value > 50) {
      return "color-incidence-51-100";
    } else if (value > 5) {
      return "color-incidence-6-50";
    } else if (value > 0) {
      return "color-incidence-1-5";
    } else {
      return "color-incidence-0";
    }
  },
  color: function(value) {
    if (value >= 500) {
      return "#d80182";
    } else if (value > 250) {
      return "#651212";
    } else if (value > 100) {
      return "#921214";
    } else if (value > 50) {
      return "#d03523";
    } else if (value > 5) {
      return "#faee7d";
    } else if (value > 0) {
      return "#faf7c9";
    } else {
      return "#ccf5c4";
    }
  },
  removeColorClasses: function(element) {
    for (const cssClass of this.classes) {
      element.classList.remove(cssClass);
    }
  }
}

export default incidence;
