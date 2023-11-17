window.addEventListener("load", () =>
  setTimeout(() => {
    const messages = document.querySelector(".messages");
    if (messages) {
      messages.remove();
    }
  }, 8000)
);
