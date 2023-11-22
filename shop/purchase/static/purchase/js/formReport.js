window.addEventListener("load", () => {
  const form = document.querySelector(".form-report--form");

  form?.addEventListener("submit", preventMultipleFormSubmission);
});
