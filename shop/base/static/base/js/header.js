window.addEventListener("load", () => {
  const menu = document.querySelector(".header--menu");
  const nav = document.querySelector(".header--nav");

  menu?.addEventListener("click", () => {
    if (menu.classList.contains("active")) {
      menu.classList.remove("active");
      nav.classList.remove("active");
    } else {
      menu.classList.add("active");
      nav.classList.add("active");
    }
  });
});
