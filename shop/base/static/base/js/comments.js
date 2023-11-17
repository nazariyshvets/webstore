window.addEventListener("load", () => {
  const openModalBtn = document.querySelector(".comments--open-modal");
  const closeModalBtn = document.querySelector(".comments--close-modal");
  const form = document.querySelector(".comments--form");

  openModalBtn?.addEventListener("click", openModal);
  closeModalBtn?.addEventListener("click", closeModal);
  form?.addEventListener("submit", preventMultipleFormSubmission);
  document.addEventListener("click", handleDocumentClick);
});

function openModal() {
  const modal = document.querySelector(".comments--modal");

  if (!modal.classList.contains("active")) {
    modal.classList.add("active");
  }
}

function closeModal() {
  const modal = document.querySelector(".comments--modal");

  if (modal.classList.contains("active")) {
    modal.classList.remove("active");
  }
}

function handleDocumentClick(event) {
  const openModalBtn = document.querySelector(".comments--open-modal");
  const form = document.querySelector(".comments--form");

  if (
    event.target !== form &&
    !form.contains(event.target) &&
    event.target !== openModalBtn
  ) {
    closeModal();
  }
}
