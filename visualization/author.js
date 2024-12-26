// Authors and links data
const authors = [
    { id: 1, name: "Alade O. Tokuta", papers: ["555036b37cea80f95414a000"] },
    { id: 2, name: "Aravind Srinivasan", papers: ["555036b37cea80f954149ffe"] },
    { id: 3, name: "Christian Wulff-Nilsen", papers: ["555036b37cea80f954149ffc"] }
];

const links = [
    { source: 7, target: 15, weight: 1 },
    { source: 10, target: 15, weight: 1 },
    { source: 2, target: 15, weight: 1 },
    { source: 7, target: 10, weight: 1 },
    { source: 2, target: 7, weight: 1 }
];

const width = 600, height = 400;

// Graph
const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

const nodes = Array.from(new Set(links.flatMap(l => [l.source, l.target]))).map(id => ({ id }));

const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(80))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#aaa");

const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 10)
    .attr("fill", "skyblue")
    .call(drag(simulation))
    .on("click", showDetails);

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
});

function showDetails(event, d) {
    const author = authors.find(a => a.id === d.id);
    const paperList = d3.select("#papers").selectAll("li")
        .data(author ? author.papers : ["No papers found"])
        .join("li")
        .text(p => p);
}

// Dragging functionality
function drag(simulation) {
    return d3.drag()
        .on("start", d => {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        })
        .on("drag", d => {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        })
        .on("end", d => {
            if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        });
}
