// The title text
const titleText =
  "Social Network Node Analysis and Community Mining on the dblpv9 Dataset";
const titleElement = document.getElementById("title");
const words = titleText.split(" ");

// Loop through each word and assign it to the h1 element with animation delay
words.forEach((word, index) => {
  const span = document.createElement("span");
  span.classList.add("word");
  span.textContent = word;

  // Dynamically set the animation delay using a CSS variable
  span.style.setProperty("--delay", `${0.2 + index * 0.2}s`);

  titleElement.appendChild(span);
});

// D3.js script for interactive background
const canvas = document.getElementById("background-canvas");
const context = canvas.getContext("2d");
let width = (canvas.width = window.innerWidth);
let height = (canvas.height = window.innerHeight);

const nodes = d3.range(50).map(() => ({
  x: Math.random() * width,
  y: Math.random() * height,
  vx: (Math.random() - 0.5) * 2,
  vy: (Math.random() - 0.5) * 2,
}));

function resizeCanvas() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
}

function drawLinks() {
  context.clearRect(0, 0, width, height);

  nodes.forEach((node) => {
    node.x += node.vx;
    node.y += node.vy;

    if (node.x < 0 || node.x > width) node.vx *= -1;
    if (node.y < 0 || node.y > height) node.vy *= -1;
  });

  context.beginPath();
  nodes.forEach((node, i) => {
    for (let j = i + 1; j < nodes.length; j++) {
      const other = nodes[j];
      const dx = node.x - other.x;
      const dy = node.y - other.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 100) {
        context.moveTo(node.x, node.y);
        context.lineTo(other.x, other.y);
      }
    }
  });
  context.strokeStyle =
    getComputedStyle(document.documentElement).getPropertyValue(
      "--link-color"
    ) || "rgba(236, 240, 241, 0.2)";
  context.stroke();

  context.fillStyle =
    getComputedStyle(document.documentElement).getPropertyValue(
      "--node-color"
    ) || "#1abc9c";
  nodes.forEach((node) => {
    context.beginPath();
    context.arc(node.x, node.y, 3, 0, 2 * Math.PI);
    context.fill();
  });

  requestAnimationFrame(drawLinks);
}

// Resize canvas on window resize
window.addEventListener("resize", () => {
  resizeCanvas();
});

resizeCanvas();
drawLinks();
