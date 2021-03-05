/*
 DID API response parser class for CoWhere.
 © 2021 Johannes Kreutz. Alle Rechte vorbehalten.
 */

let didparser = {
  fixExternalLinks: function(input) {
    let parser = new DOMParser();
    let dom = parser.parseFromString(input, "text/html");
    this.recursiveWorker(dom.body);
    return dom.body.innerHTML;
  },
  recursiveWorker: function(element) {
    if (Array.from(element.children).length > 0) {
      for (const child of Array.from(element.children)) {
        this.recursiveWorker(child);
      }
    } else {
      if (element.nodeName == "A") {
        let url = element.href;
        element.href = "#";
        element.setAttribute("onclick", "window.externalLinkClick('" + url + "')");
      }
    }
  }
}

export default didparser;
