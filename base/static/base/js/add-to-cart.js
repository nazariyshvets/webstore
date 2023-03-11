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