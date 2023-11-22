window.addEventListener("load", () => {
  const commoditiesContainer = document.querySelector(".cart--commodities");
  const form = document.querySelector(".cart--form");

  commoditiesContainer?.addEventListener(
    "click",
    handleCommoditiesContainerClick
  );
  form?.addEventListener("submit", handleFormSubmit);

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
  const quantityDisplay = commodity.querySelector(".cart--quantity-display");

  if (quantityDisplay) {
    quantityDisplay.textContent = commodity.dataset.quantity;
  }
}

function updateTotalPriceDisplay() {
  const totalPriceDisplay = document.querySelector(".cart--buy--price");

  if (totalPriceDisplay) {
    totalPriceDisplay.textContent = formatNumberWithSpaces(
      calculateTotalPrice().replace(".", ",")
    );
  }
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

function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;

  if (isFormBeingSubmitted(form)) {
    return;
  }
  setFormIsBeingSubmitted(form);

  const commodities = document.querySelectorAll(".cart--commodity");
  const ids = [];
  const quantities = [];

  [...commodities].forEach((commodity) => {
    ids.push(parseInt(commodity.dataset.id));
    quantities.push(parseInt(commodity.dataset.quantity));
  });

  form.elements["ids"].value = ids.join(",");
  form.elements["quantities"].value = quantities.join(",");

  form.submit();
}
