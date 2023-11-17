window.addEventListener("load", () => {
  const form = document.querySelector(".search-form");
  form?.addEventListener("submit", preventMultipleFormSubmission);
});