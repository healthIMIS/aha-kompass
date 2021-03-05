/*
 Time parse functions for CoWhere.
 © 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let timeparse = {
  addLeadingZeros: function(input) {
    return ("0" + input).slice(-2);
  }
}

export default timeparse;
