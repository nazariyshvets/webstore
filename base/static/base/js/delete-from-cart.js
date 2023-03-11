const deleteFromCartBtns = document.getElementsByClassName("delete-from-cart");

Array.from(deleteFromCartBtns).forEach(btn => {
  btn.addEventListener("click", e => {
    commodity_id = parseInt(btn.dataset.commodity_id);
    fetch("/delete-from-cart/", {
      method: "POST",
      headers: {"Content-Type": "application/json",},
      body: JSON.stringify({commodity_id: commodity_id})  
    })
    .then((response) => response.json())
    .then((data) => {
      if(data["success"]) {
        btn.parentNode.parentNode.removeChild(btn.parentNode);

        if(document.getElementById("commodities").children.length == 0) {
          document.getElementById("buy").remove();
          document.getElementById("empty-cart-img").style.display = "inline-block";
          document.getElementById("empty-cart").style.display = "block";
        }
      }
    });
  });
});

if(document.getElementById("commodities").children.length == 0) {
  document.getElementById("empty-cart-img").style.display = "inline-block";
  document.getElementById("empty-cart").style.display = "block";
}