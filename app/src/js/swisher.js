/*
 Swisher JS for MarburgCode
 © 2017 - 2020 Johannes Kreutz. Alle Rechte vorbehalten.
 */
const safeAreaInsets = require('safe-area-insets');

class swisher {
    constructor(topId, closeCallback, openCallback) {
        this.container = document.getElementById(topId);
        this.grabber = null;
        this.controlbar = null;
        for (const child of this.container.childNodes) {
            switch(child.className) {
                case "grabber":
                    this.grabber = child;
                    break;
                case "controlbar":
                    this.controlbar = child;
                    break;
            }
        }
        this.isClicked = false;
        this.startY = 0;
        this.lastY = 0;
        this.lastMoveY = 0;
        this.willGoUp = false;
        this.isUserMovable = this.isMobile();
        this.closeCallback = closeCallback;
        this.openCallback = openCallback;
        this.grabber.addEventListener('touchstart', this.onMouseDown.bind(this), false);
        this.grabber.addEventListener('touchend', this.onMouseUp.bind(this), false);
        this.grabber.addEventListener('touchmove', this.onMouseMove.bind(this), false);
        this.grabber.addEventListener('click', this.onGrabberClick.bind(this), false);
        window.addEventListener('resize', this.resize.bind(this));
        this.wasMobile = this.isMobile();
        this.districtSelected = false;
    }
    resize() {
        if (this.wasMobile && !this.isMobile() && this.lastY != 0) {
            this.goDown(true);
        } else if (!this.wasMobile && this.isMobile() && this.districtSelected) {
            this.goUp(true);
        }
        this.wasMobile = this.isMobile()
    }
    isMobile() {
      return window.innerWidth <= 1000;
    }
    onMouseDown(event) {
        if (this.isUserMovable) {
            this.container.classList.remove('swisher-smooth');
            this.isClicked = true;
            this.startY = (typeof event.touches !== "undefined") ? event.touches[0].clientY : event.offsetY;
        }
    }
    onMouseUp(event) {
        if (this.isUserMovable) {
            this.container.classList.add('swisher-smooth');
            this.isClicked = false;
            this.lastY = this.lastMoveY - this.startY + this.lastY;
            let willUp = false;
            if (((this.lastY < (-0.35 * window.innerHeight)) && !this.willGoUp) || ((this.lastY < (-0.2 * window.innerHeight)) && this.willGoUp)) {
                willUp = true;
            }
            if (willUp) {
                this.container.style.transform = 'translate3d(0px, var(--maxUpDrive), 0px)';
                this.controlbar.classList.add('controlbar-down');
                this.lastY = (-1 * (window.innerHeight - safeAreaInsets.top - 244 - 100));
                this.openCallback();
                this.districtSelected = true;
            } else {
                this.container.style.transform = 'translate3d(0px, 0px, 0px)';
                this.controlbar.classList.remove('controlbar-down');
                this.lastY = 0;
                this.closeCallback();
                this.districtSelected = false;
            }
        }
    }
    onMouseMove(event) {
        if (this.isUserMovable && this.isClicked) {
            this.lastMoveY = (typeof event.touches !== "undefined") ? event.touches[0].clientY : event.offsetY;
            let temp = this.lastMoveY - this.startY + this.lastY;
            this.container.style.transform = 'translate3d(0px, ' + temp + 'px, 0px)';
            if ((this.lastMoveY - this.startY) > 0) {
                this.willGoUp = false;
            } else {
                this.willGoUp = true;
            }
        }
    }
    onGrabberClick() {
        if (this.lastY == 0) {
            this.goUp();
            this.openCallback();
            this.districtSelected = true;
        } else {
            this.goDown();
            this.closeCallback();
            this.districtSelected = false;
        }
    }
    goDown(force) {
      if (this.isMobile() || force) {
        this.container.style.transform = 'translate3d(0px, 0px, 0px)';
        this.controlbar.classList.remove('controlbar-down');
        this.lastY = 0;
      }
    }
    goUp(force) {
      if (this.isMobile() || force) {
        this.container.style.transform = 'translate3d(0px, var(--maxUpDrive), 0px)';
        this.controlbar.classList.add('controlbar-down');
        this.lastY = (-1 * (window.innerHeight - safeAreaInsets.top - 244 - 100));
      }
    }
    disable() {
        this.isUserMovable = false;
        this.controlbar.classList.add("invisible");
    }
    enable() {
        this.isUserMovable = true;
        this.controlbar.classList.remove("invisible");
    }
    setSelection(mode) {
        this.districtSelected = mode;
    }
}

export default swisher;
