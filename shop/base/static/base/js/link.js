function handleLinkClick(event) {
  const link = event.target.closest("a");

  if(!link) {
    return;
  }

  if (link.dataset.clicked === "true") {
    event.preventDefault();
    return;
  }

  link.dataset.clicked = "true";
}

document.addEventListener("click", handleLinkClick);