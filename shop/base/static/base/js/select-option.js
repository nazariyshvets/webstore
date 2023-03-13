const sortOptions = document.getElementById("sort").children;
const commoditiesNumPerPageOptions = document.getElementById("commodities-num-per-page").children;

Array.from(sortOptions).forEach(option => {
  if(option.value == sort)option.selected = "selected";
});

Array.from(commoditiesNumPerPageOptions).forEach(option => {
  if(option.value == commoditiesNumPerPage)option.selected = "selected";
});

console.log(manufacturers);