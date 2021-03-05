/*
 Clipboard JS for CoWhere.
 © 2020 - 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let clipboard = {
  add: function(text) {
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
  }
}

export default clipboard;
