window.addEventListener("load", () => {
  const filterForm = document.querySelector(".category--filter-form");
  const searchForm = document.querySelector(".search-form");
 
  filterForm?.addEventListener("submit", handleFormSubmit);
  searchForm?.addEventListener("submit", handleFormSubmit);

  setDefaultValues();
});

function handleFormSubmit(event) {
  event.preventDefault();

  if (!isFormBeingSubmitted(event.currentTarget)) {
    sendData();
  }

  preventMultipleFormSubmission(event);
}

function sendData() {
  const manufacturerCheckBoxes = document.querySelectorAll(
    ".category--manufacturer-input"
  );
  const query = document.querySelector(".search-form--query").value;
  const sort = document.querySelector(".search-form--sort").value;
  const limit = document.querySelector(".search-form--limit").value;
  const selectedManufacturers = [];

  for (const checkBox of manufacturerCheckBoxes) {
    if (checkBox.checked) {
      selectedManufacturers.push(checkBox.value);
    }
  }

  // Construct the URL with the combined values
  const url = `?query=${encodeURIComponent(
    query
  )}&sort=${sort}&limit=${limit}&manufacturers=${selectedManufacturers.join(
    ","
  )}`;

  window.location.href = url;
}

function setDefaultValues() {
  //selectedManufacturersStr is provided by the backend and taken from a template (html)
  const manufacturerCheckBoxes = document.querySelectorAll(
    ".category--manufacturer-input"
  );
  const selectedManufacturers = selectedManufacturersStr.split(",");

  for (const checkBox of manufacturerCheckBoxes) {
    if (selectedManufacturers.includes(checkBox.value)) {
      checkBox.checked = "checked";
    }
  }
}
