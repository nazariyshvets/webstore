window.addEventListener("load", () => {
  const commoditiesContainer = document.querySelector(".commodities");

  commoditiesContainer?.addEventListener(
    "click",
    handleCommoditiesContainerClick
  );
});

function handleCommoditiesContainerClick(event) {
  const target = event.target;

  if (target.matches(".commodity-card--add-to-cart")) {
    addToCart(target);
  }
}

function addToCart(targetBtn) {
  const commodityCard = targetBtn.closest(".commodity-card");

  if (commodityCard.dataset.addedToCart === "true") {
    return;
  }
  commodityCard.dataset.addedToCart = "true";

  const commodityId = parseInt(commodityCard.dataset.id);

  fetch("/add-to-cart/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ commodity_id: commodityId }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        targetBtn.textContent = "Додано";
        targetBtn.style.cursor = "default";
        targetBtn.style.boxShadow = "none";
      }
    })
    .catch((error) => {
      commodityCard.dataset.addedToCart = "false";
      console.error("Error:", error);
      alert("Виникла помилка під час додавання товару в кошик");
    });
}
