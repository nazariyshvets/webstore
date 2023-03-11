/*SEND DATA AFTER 'FILTER' OR 'SEARCH' FORM SUBMITTING*/
const searchForm = document.getElementById("search-form");
const filterForm = document.getElementById("filter-form");
const manufacturerCheckBoxes = document.getElementsByClassName("manufacturer-input");
const sortSelect = document.getElementById("sort");
const commoditiesNumPerPageSelect = document.getElementById("commodities-num-per-page");

searchForm.addEventListener("submit", e => {
  e.preventDefault();
  sendData();
});

filterForm.addEventListener("submit", e => {
  e.preventDefault();
  sendData();
});

sortSelect.addEventListener("change", e => {
  sendData();
});

commoditiesNumPerPageSelect.addEventListener("change", e => {
  sendData();
});

function sendData() {
  const selectedManufacturers = [];

  Array.from(manufacturerCheckBoxes).forEach(checkBox => {
    if(checkBox.checked)
      selectedManufacturers.push(checkBox.value);
  });

  document.getElementById("selected-manufacturers").value = selectedManufacturers;
  searchForm.submit();
}

/*SET CURRENT VALUES FOR 'FILTER' AND 'SEARCH' FORM WIDGETS*/
const sortOptions = document.getElementById("sort").children;
const commoditiesNumPerPageOptions = document.getElementById("commodities-num-per-page").children;

Array.from(sortOptions).forEach(option => {
  if(option.value == sort)option.selected = "selected";
});

Array.from(commoditiesNumPerPageOptions).forEach(option => {
  if(option.value == commoditiesNumPerPage)option.selected = "selected";
});

Array.from(manufacturerCheckBoxes).forEach(checkBox => {
  if(selectedManufacturers.includes(checkBox.value))checkBox.checked = true;
});

/*SEND DATA AFTER 'ADD TO CART' BUTTON WAS CLICKED*/
const addToCartBtns = document.getElementsByClassName("add-to-cart");

Array.from(addToCartBtns).forEach(btn => {
  btn.addEventListener("click", e => {
    commodity_id = parseInt(btn.dataset.commodity_id);
    fetch("/add-to-cart/", {
      method: "POST",
      headers: {"Content-Type": "application/json",},
      body: JSON.stringify({commodity_id: commodity_id})  
    })
    .then((response) => response.json())
    .then((data) => {
      if(data["success"]) {
        btn.textContent = "Додано";
        btn.style.cursor = "default";
        btn.style.boxShadow = "none";
      }
    });
  });
});