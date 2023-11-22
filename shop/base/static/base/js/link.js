function handleLinkClick(event) {
  const link = event.target.closest("a");

  if (!link) {
    return;
  }

  if (link.dataset.clicked === "true") {
    event.preventDefault();
  } else {
    link.dataset.clicked = "true";
    setTimeout(() => (link.dataset.clicked = "false"), 2000);
  }
}

document.addEventListener("click", handleLinkClick);
