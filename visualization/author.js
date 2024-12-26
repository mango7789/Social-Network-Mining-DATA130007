const authors = [
    { id: 1, name: "Alade O. Tokuta", papers: "555036b37cea80f95414a000", num_co_authors: 3, num_papers: 1 },
    { id: 2, name: "Aravind Srinivasan", papers: "555036b37cea80f954149ffe", num_co_authors: 3, num_papers: 1 },
    { id: 3, name: "Christian Wulff-Nilsen", papers: "555036b37cea80f954149ffc", num_co_authors: 0, num_papers: 1 }
];

// Link data (src, dst, w)
const links = [
    { source: 1, target: 2, weight: 1 },
    { source: 1, target: 3, weight: 5 },
];

const community = { 1: "A", 2: "A", 3: "B" };

// Prepare graph data
const width = 600, height = 400;

const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

// Create nodes
const uniqueNodeIds = Array.from(new Set(links.flatMap(link => [link.source, link.target])));
const nodes = uniqueNodeIds.map(id => ({
    id,
    name: authors.find(author => author.id === id)?.name || `Node ${id}`,
    community: community[id] || "Unknown"
}));

// Setup force simulation
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

// Draw links
const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", "#999")
    .attr("stroke-width", d => d.weight || 1);

// Draw nodes
const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 10)
    .attr("fill", d => d.community === "A" ? "blue" : "green")
    .call(drag(simulation));

node.append("title")
    .text(d => d.name);

// Update positions on simulation tick
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

// Click event for nodes
node.on("click", d => {
    const author = authors.find(a => a.id === d.id);
    showDetails(author, d.id);
});

// Show author details
function showDetails(author, nodeId) {
    if (author) {
        d3.select("#info").text(`${author.name} (${author.num_co_authors} co-authors, ${author.num_papers} papers)`);
        d3.select("#papers").selectAll("li")
            .data([author.papers])
            .join("li")
            .text(d => d);
    } else {
        d3.select("#info").text(`Node ${nodeId} (No detailed information available)`);
    }

    const connectedNodes = links
        .filter(link => link.source.id === nodeId || link.target.id === nodeId)
        .map(link => (link.source.id === nodeId ? link.target.id : link.source.id));
    const coAuthorNames = connectedNodes.map(id => authors.find(a => a.id === id)?.name || `Node ${id}`);
    d3.select("#coauthors").selectAll("li")
        .data(coAuthorNames)
        .join("li")
        .text(d => d);
}

// Drag behavior
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
