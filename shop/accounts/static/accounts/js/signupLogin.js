window.addEventListener("load", () => {
  const form = document.querySelector(".signup-login--form");

  form?.addEventListener("submit", preventMultipleFormSubmission);
});