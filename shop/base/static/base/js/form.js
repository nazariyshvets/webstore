function preventMultipleFormSubmission(event) {
  const form = event.currentTarget;

  if (isFormBeingSubmitted(form)) {
    event.preventDefault();
  }

  form.classList.add("is-submitting");
}

function isFormBeingSubmitted(form) {
  return form.classList.contains("is-submitting");
}
