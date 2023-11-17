window.addEventListener("load", () => {
  const form = document.querySelector(".change-profile--form");

  form?.addEventListener("submit", preventMultipleFormSubmission);
});