const commoditiesContainer = document.querySelector("#commodities");

//event listener for "delete from cart" buttons
commoditiesContainer.addEventListener("click", (e) => {
  const target = e.target;

  if (target.matches(".delete-from-cart")) {
    const commodity_id = parseInt(target.dataset.commodity_id);

    fetch("/delete-from-cart/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commodity_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const commodity = target.closest(".commodity");
          commoditiesContainer.removeChild(commodity);

          if(commoditiesContainer.children.length == 0) {
            document.querySelector("#buy").remove();
            createEmptyCartWidgets();
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Виникла помилка під час видалення товару з кошика");
      });
  }
});

if(commoditiesContainer.children.length == 0) {
  createEmptyCartWidgets();
}

function createEmptyCartWidgets() {
  const emptyCartImg = `
    <img
      id="empty-cart-img"
      src="/static/base/images/empty_cart.png"
      alt="empty cart"
      draggable="false"
    />
  `;
  const emptyCartText = `
    <h2 id="empty-cart-text">Кошик порожній</h2>
  `;
  document.querySelector("#empty-cart").innerHTML = emptyCartImg + emptyCartText;
}