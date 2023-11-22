function preventMultipleFormSubmission(event) {
  const form = event.currentTarget;

  if (isFormBeingSubmitted(form)) {
    event.preventDefault();
  } else {
    setFormIsBeingSubmitted(form);
    setTimeout(() => {
      setFormIsBeingSubmitted(form, false);
    }, 2000);
  }
}

function isFormBeingSubmitted(form) {
  return form.classList.contains("is-submitting");
}

function setFormIsBeingSubmitted(form, isBeingSubmitted = true) {
  if (isBeingSubmitted) {
    form.classList.add("is-submitting");
  } else {
    form.classList.remove("is-submitting");
  }
}
