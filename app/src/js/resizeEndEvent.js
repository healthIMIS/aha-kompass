/*
 Resize end event JS for MarburgCode
 © 2017 - 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */

class resizeEndEvent {
  constructor(callback) {
    this.callback = callback;
    this.timeout = null;
    window.addEventListener('resize', this.onResize.bind(this));
  }
  onResize() {
    clearTimeout(this.timeout);
    this.timeout = setTimeout(this.callback, 200);
  }
}

export default resizeEndEvent;
