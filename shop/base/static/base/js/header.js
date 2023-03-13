const hamburgerMenu = document.getElementById("hamburger-menu");
const headerNav = document.getElementById("header-nav");

hamburgerMenu.addEventListener("click", function(e) {
  if(this.classList.contains("active")) {
    this.classList.remove("active");
    headerNav.classList.remove("active");
  } else {
    this.classList.add("active");
    headerNav.classList.add("active");
  }
});