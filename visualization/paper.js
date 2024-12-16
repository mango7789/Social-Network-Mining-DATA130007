document.addEventListener("DOMContentLoaded", () => {
  const topLeftDiv = document.querySelector(".top-left");
  if (topLeftDiv) {
    const svg = d3
      .select(topLeftDiv)
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%");

    svg
      .append("circle")
      .attr("cx", "50%")
      .attr("cy", "50%")
      .attr("r", 30)
      .attr("fill", "steelblue");
  }
});
