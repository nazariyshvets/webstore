window.addEventListener("load", () => {
  const commoditiesContainer = document.querySelector(".cart--commodities");
  const buyBtn = document.querySelector(".cart--buy");

  commoditiesContainer?.addEventListener(
    "click",
    handleCommoditiesContainerClick
  );
  buyBtn?.addEventListener("click", handleBuyBtnClick);

  updateTotalPriceDisplay();
});

function handleCommoditiesContainerClick(event) {
  const target = event.target;

  if (target.matches(".cart--decrease")) {
    handleDecreaseBtnClick(target);
  } else if (target.matches(".cart--increase")) {
    handleIncreaseBtnClick(target);
  }
}

function handleDecreaseBtnClick(target) {
  const commodity = target.closest(".cart--commodity");
  const quantity = parseInt(commodity.dataset.quantity);

  if (quantity > 1) {
    commodity.dataset.quantity = quantity - 1;
    updateQuantityDisplay(commodity);
    updateTotalPriceDisplay();
  }
}

function handleIncreaseBtnClick(target) {
  const commodity = target.closest(".cart--commodity");
  const quantity = parseInt(commodity.dataset.quantity);

  commodity.dataset.quantity = quantity + 1;
  updateQuantityDisplay(commodity);
  updateTotalPriceDisplay();
}

function updateQuantityDisplay(commodity) {
  commodity.querySelector(".cart--quantity-display").textContent =
    commodity.dataset.quantity;
}

function updateTotalPriceDisplay() {
  document.querySelector(".cart--buy--price").textContent =
    formatNumberWithSpaces(calculateTotalPrice().replace(".", ","));
}

function calculateTotalPrice() {
  const commodities = document.querySelectorAll(".cart--commodity");
  return [...commodities]
    .reduce((sum, commodity) => {
      return (
        sum +
        parseFloat(commodity.dataset.price.replace(",", ".")) *
          parseInt(commodity.dataset.quantity)
      );
    }, 0)
    .toFixed(2);
}

function formatNumberWithSpaces(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function handleBuyBtnClick(event) {
  const buyBtn = event.currentTarget;

  if (buyBtn.disabled) return;
  buyBtn.disabled = true;

  const commodities = document.querySelectorAll(".cart--commodity");
  const data = [...commodities].map((commodity) => ({
    commodity_id: parseInt(commodity.dataset.id),
    quantity: parseInt(commodity.dataset.quantity),
  }));

  fetch("/cart/buy/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .catch((error) => {
      console.error("Error:", error);
    })
    .finally(() => window.location.reload());
}
