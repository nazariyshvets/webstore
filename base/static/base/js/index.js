/*SET CURRENT VALUES FOR 'SEARCH' FORM WIDGETS*/
const sortOptions = document.getElementById("sort").children;
const commoditiesNumPerPageOptions = document.getElementById("commodities-num-per-page").children;

Array.from(sortOptions).forEach(option => {
  if(option.value == sort)option.selected = "selected";
});

Array.from(commoditiesNumPerPageOptions).forEach(option => {
  if(option.value == commoditiesNumPerPage)option.selected = "selected";
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