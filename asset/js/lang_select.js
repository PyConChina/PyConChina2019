(function () {
  "use strict";
  var element = document.getElementById("lang-select-wrap");
  function changeLang() {
    var lang = element.dataset.lang;
    var path = window.location.pathname.split("/");
    if (lang !== "zh-cn") {
      path.splice(path.length - 1, 0, lang);
    } else {
      path.splice(path.length - 2, 1);
    }
    location.href = path.join("/");
  }
  element.addEventListener("click", changeLang)
})();