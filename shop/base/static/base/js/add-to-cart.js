const commoditiesContainer = document.querySelector("#commodities");

//event listener for "add to cart" buttons
commoditiesContainer.addEventListener("click", (e) => {
  const target = e.target;

  if (target.matches(".add-to-cart")) {
    const commodity_id = parseInt(target.dataset.commodity_id);

    fetch("/add-to-cart/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commodity_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          target.textContent = "Додано";
          target.style.cursor = "default";
          target.style.boxShadow = "none";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Виникла помилка під час додавання товару в кошик");
      });
  }
});