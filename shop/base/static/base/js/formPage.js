window.addEventListener("load", () => {
  const form = document.querySelector(".form-page--form");

  form?.addEventListener("submit", preventMultipleFormSubmission);
});