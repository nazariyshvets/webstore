const hamburgerMenu = document.getElementById("hamburger-menu");
const headerNav = document.getElementById("header-nav");

hamburgerMenu.addEventListener("click", e => {
  if(hamburgerMenu.classList.contains("active")) {
    hamburgerMenu.classList.remove("active");
    headerNav.classList.remove("active");
  } else {
    hamburgerMenu.classList.add("active");
    headerNav.classList.add("active");
  }
});