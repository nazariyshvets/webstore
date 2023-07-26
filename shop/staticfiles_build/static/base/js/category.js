const filterForm = document.querySelector("#filter-form");
const searchForm = document.querySelector("#search-form");
const sortSelect = document.querySelector("#sort");
const commoditiesNumPerPageSelect = document.querySelector(
  "#commodities-num-per-page"
);
const manufacturerCheckBoxes = document.querySelectorAll(
  ".manufacturer-input"
);

//event listeners for searching and filtering
filterForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendData();
});
searchForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendData();
});
sortSelect.addEventListener("change", sendData);
commoditiesNumPerPageSelect.addEventListener("change", sendData);

setDefaultValues();

function sendData() {
  const searchInputValue = document.querySelector("#search-input").value;
  const sortValue = sortSelect.value;
  const commoditiesNumPerPageValue = commoditiesNumPerPageSelect.value;
  const selectedManufacturers = [];

  for (const checkBox of manufacturerCheckBoxes) {
    if (checkBox.checked) selectedManufacturers.push(checkBox.value);
  }

  // Construct the URL with the combined values
  const url = `?search-input=${encodeURIComponent(
    searchInputValue
  )}&sort=${sortValue}&commodities-num-per-page=${commoditiesNumPerPageValue}&manufacturers=${selectedManufacturers.join(
    ","
  )}`;

  window.location.href = url;
}

function setDefaultValues() {
  //sortSelectValue, commoditiesNumPerPageValue and selectedManufacturersStr are provided by the backend 
  //and taken from a template (html)
  sortSelect.value = sort;
  commoditiesNumPerPageSelect.value = commoditiesNumPerPage;
  const selectedManufacturers = selectedManufacturersStr.split(",");

  for(const checkBox of manufacturerCheckBoxes) {
    if(selectedManufacturers.includes(checkBox.value)) {
      checkBox.checked = "checked"
    }
  }
}