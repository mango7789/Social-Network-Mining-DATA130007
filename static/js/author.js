document.addEventListener("DOMContentLoaded", () => {
  const topLeftDiv = document.querySelector(".top-left");
  const topRightDiv = document.querySelector(".top-right");
  const bottomLeftDiv = document.getElementById("citation-plot");
  const bottomRightDiv = document.getElementById("coauthors-rank");
  ////////////////////////////////////////////////////////////////////////
  //                            Top Left                                //
  ////////////////////////////////////////////////////////////////////////
  if (topLeftDiv) {
    const nodes = [
      {
        id: 1,
        name: "Alade O. Tokuta",
        co_authors: [4, 16, 17],
        papers: ["555036b37cea80f95414a000"],
        community: 1,
      },
      {
        id: 2,
        name: "Aravind Srinivasan",
        co_authors: [7, 10, 15],
        papers: ["555036b37cea80f954149ffe"],
        community: 2,
      },
      {
        id: 3,
        name: "Christian Wulff-Nilsen",
        co_authors: [],
        papers: ["555036b37cea80f954149ffc"],
        community: 3,
      },
      {
        id: 4,
        name: "Donghyun Kim",
        co_authors: [1, 16, 17],
        papers: ["555036b37cea80f95414a000"],
        community: 1,
      },
      {
        id: 5,
        name: "Howard W. Beck",
        co_authors: [9, 12],
        papers: ["5736965d6e3b12023e56a854"],
        community: 4,
      },
      {
        id: 6,
        name: "Julián Mestre",
        co_authors: [],
        papers: ["555036b37cea80f954149ffd"],
        community: 3,
      },
      {
        id: 7,
        name: "Madhav V. Marathe",
        co_authors: [2, 10, 15],
        papers: ["555036b37cea80f954149ffe"],
        community: 2,
      },
      {
        id: 8,
        name: "Maxime Crochemore",
        co_authors: [13],
        papers: ["555036b37cea80f954149fff"],
        community: 5,
      },
      {
        id: 9,
        name: "Shamkant B. Navathe",
        co_authors: [5, 12],
        papers: ["5736965d6e3b12023e56a854"],
        community: 4,
      },
      {
        id: 10,
        name: "Srinivasan Parthasarathy",
        co_authors: [2, 7, 15],
        papers: ["555036b37cea80f954149ffe"],
        community: 2,
      },
      {
        id: 11,
        name: "Subrata Ghosh",
        co_authors: [14],
        papers: ["5736965d6e3b12023e56a853"],
        community: 6,
      },
      {
        id: 12,
        name: "Tarek M. Anwar",
        co_authors: [5, 9],
        papers: ["5736965d6e3b12023e56a854"],
        community: 4,
      },
      {
        id: 13,
        name: "Thierry Lecroq",
        co_authors: [8],
        papers: ["555036b37cea80f954149fff"],
        community: 5,
      },
      {
        id: 14,
        name: "Timos K. Sellis",
        co_authors: [11],
        papers: ["5736965d6e3b12023e56a853"],
        community: 6,
      },
      {
        id: 15,
        name: "V. S. Anil Kumar",
        co_authors: [2, 7, 10],
        papers: ["555036b37cea80f954149ffe"],
        community: 2,
      },
      {
        id: 16,
        name: "Wei Wang",
        co_authors: [1, 4, 17],
        papers: ["555036b37cea80f95414a000"],
        community: 1,
      },
      {
        id: 17,
        name: "Weili Wu",
        co_authors: [1, 4, 16],
        papers: ["555036b37cea80f95414a000"],
        community: 1,
      },
    ];

    const edges = [
      { src: 7, dst: 15, weight: 1 },
      { src: 10, dst: 15, weight: 1 },
      { src: 2, dst: 15, weight: 1 },
      { src: 7, dst: 10, weight: 1 },
      { src: 2, dst: 7, weight: 1 },
      { src: 2, dst: 10, weight: 1 },
      { src: 8, dst: 13, weight: 2 },
      { src: 4, dst: 16, weight: 5 },
      { src: 4, dst: 17, weight: 1 },
      { src: 1, dst: 4, weight: 1 },
      { src: 16, dst: 17, weight: 1 },
      { src: 1, dst: 16, weight: 1 },
      { src: 1, dst: 17, weight: 1 },
      { src: 11, dst: 14, weight: 1 },
      { src: 5, dst: 12, weight: 1 },
      { src: 5, dst: 9, weight: 1 },
      { src: 9, dst: 12, weight: 1 },
    ];

    const width = topLeftDiv.clientWidth;
    const height = topLeftDiv.clientHeight;

    const svg = d3
      .select(".top-left")
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    // Create a zoom behavior
    const zoom = d3.zoom().scaleExtent([0.5, 5]).on("zoom", event => {
      graphGroup.attr("transform", event.transform);
    });

    svg.call(zoom); // Bind the zoom behavior to the SVG

    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "tooltip")
      .style("position", "absolute")
      .style("padding", "5px")
      .style("border-radius", "4px")
      .style("visibility", "hidden");

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create a mapping from community to a unique position
    const communityCenters = {};
    nodes.forEach(node => {
      if (!communityCenters[node.community]) {
        communityCenters[node.community] = { x: 0, y: 0, count: 0 };
      }
      communityCenters[node.community].x += Math.random() * width;
      communityCenters[node.community].y += Math.random() * height;
      communityCenters[node.community].count += 1;
    });

    // Average the center positions for each community
    for (const community in communityCenters) {
      communityCenters[community].x /= communityCenters[community].count;
      communityCenters[community].y /= communityCenters[community].count;
    }

    const simulation = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(edges).id(d => d.src).distance(100))
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Add a group for the graph content (nodes and links)
    const graphGroup = svg.append("g");

    function logisticGrowth(x, r_max = 30, k = 0.1, x_0 = 20) {
      return r_max / (1 + Math.exp(-k * (x - x_0)));
    }

    // Add legend on the right side (outside the zoomed group)
    const legendWidth = 150;
    const legendMargin = 20;

    const legend = svg
      .append("g")
      .attr(
        "transform",
        `translate(${width - legendWidth - legendMargin}, ${legendMargin})`
      );

    const communities = [...new Set(nodes.map(d => d.community))];

    const legendItems = legend
      .selectAll(".legend-item")
      .data(communities)
      .enter()
      .append("g")
      .attr("class", "legend-item")
      .attr("transform", (d, i) => `translate(0, ${i * 20})`);

    legendItems
      .append("rect")
      .attr("width", 15)
      .attr("height", 15)
      .attr("fill", d => color(d));

    legendItems
      .append("text")
      .attr("x", 20)
      .attr("y", 10)
      .text(d => d)
      .style("font-size", "12px")
      .style("alignment-baseline", "middle");

    // Functions for dragging
    function dragStart(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnd(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Function to plot nodes and links based on the filtered data
    function plotGraph(filteredNodes, filteredEdges) {
      // Re-create links (edges)
      graphGroup
        .selectAll(".link")
        .data(filteredEdges)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke", "#aaa")
        .attr("stroke-width", d => d.weight);

      // Re-create nodes
      const nodeCircles = graphGroup
        .selectAll(".node")
        .data(filteredNodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", d => logisticGrowth(d.co_authors.length))
        .attr("fill", d => color(d.community))
        .call(
          d3
            .drag()
            .on("start", dragStart)
            .on("drag", dragged)
            .on("end", dragEnd)
        );

      const nodeLabels = graphGroup
        .selectAll(".node-label")
        .data(filteredNodes)
        .enter()
        .append("text")
        .attr("class", "node-label")
        .attr("text-anchor", "middle")
        .attr("dy", 4) // Adjust vertical alignment
        .style("font-size", "10px")
        .style("pointer-events", "none") // Prevent interference with drag events
        .text(d => d.id);

      // Tooltip on hover
      nodeCircles
        .on("mouseover", function(event, d) {
          d3
            .select(this)
            .transition()
            .duration(200)
            .attr("r", d => 1.2 * logisticGrowth(d.co_authors.length));

          tooltip.style("visibility", "visible").html(`
                        <b>ID</b>: ${d.id}<br>
                    `);
        })
        .on("mousemove", function(event) {
          tooltip
            .style("top", event.pageY + 10 + "px")
            .style("left", event.pageX + 10 + "px");
        })
        .on("mouseout", function() {
          d3
            .select(this)
            .transition()
            .duration(200)
            .attr("r", d => logisticGrowth(d.co_authors.length));
          tooltip.style("visibility", "hidden");
        });

      simulation.nodes(filteredNodes).on("tick", ticked);
      simulation.force("link").links(edges);

      // Restart the simulation to apply new data and layout
      simulation.alpha(1).restart();

      function ticked() {
        graphGroup
          .selectAll(".link")
          .attr("x1", d => filteredNodes.find(n => n.id === d.src).x)
          .attr("y1", d => filteredNodes.find(n => n.id === d.src).y)
          .attr("x2", d => filteredNodes.find(n => n.id === d.dst).x)
          .attr("y2", d => filteredNodes.find(n => n.id === d.dst).y);

        nodeCircles.attr("cx", d => d.x).attr("cy", d => d.y);

        nodeLabels.attr("x", d => d.x).attr("y", d => d.y);
      }
    }

    plotGraph(nodes, edges);
  }
  ////////////////////////////////////////////////////////////////////////
  //                            Top Right                               //
  ////////////////////////////////////////////////////////////////////////
  if (topRightDiv) {
  }
  ////////////////////////////////////////////////////////////////////////
  //                           Bottom Left                              //
  ////////////////////////////////////////////////////////////////////////
  if (bottomLeftDiv) {
    function plotBarChartFromJson(jsonData, title) {
      const data = jsonData.map(d => ({
        label: d.year,
        value: d.count,
      }));
      console.log(data);
      const width = bottomLeftDiv.clientWidth;
      const height = bottomLeftDiv.clientHeight;

      const margin = { top: 30, right: 20, bottom: 40, left: 40 };
      const chartWidth = width - margin.left - margin.right;
      const chartHeight = height - margin.top - margin.bottom;

      // Select or create SVG container (ensure only one svg exists)
      let svg = d3.select(bottomLeftDiv).select("svg");
      if (svg.empty()) {
        svg = d3
          .select(bottomLeftDiv)
          .append("svg")
          .attr("width", width)
          .attr("height", height);

        svg
          .append("g")
          .attr("class", "bars")
          .attr("transform", `translate(${margin.left},${margin.top})`);
        svg
          .append("g")
          .attr("class", "x-axis")
          .attr(
            "transform",
            `translate(${margin.left},${margin.top + chartHeight})`
          );
        svg
          .append("g")
          .attr("class", "y-axis")
          .attr("transform", `translate(${margin.left},${margin.top})`);
        svg
          .append("text")
          .attr("class", "title")
          .attr("x", width / 2)
          .attr("y", margin.top / 2)
          .attr("text-anchor", "middle")
          .style("font-size", "16px")
          .style("font-weight", "bold");
      }

      // Scales
      const x = d3.scaleBand().range([0, chartWidth]).padding(0.1);
      const y = d3.scaleLinear().range([chartHeight, 0]);

      x.domain(data.map(d => d.label));
      y.domain([0, d3.max(data, d => d.value)]);

      // Tooltip setup
      const tooltip = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("border", "1px solid #ccc")
        .style("border-radius", "4px")
        .style("padding", "5px")
        .style("pointer-events", "none");

      // Update bars with smooth transition
      const bars = svg
        .select(".bars")
        .selectAll(".bar")
        .data(data, d => d.label);

      bars
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => {
          x(d.label);
        })
        .attr("y", chartHeight) // Start at the bottom
        .attr("width", x.bandwidth())
        .attr("height", 0) // Start with height 0
        .attr("fill", "steelblue")
        .on("mouseover", function(event, d) {
          d3.select(this).attr("fill", "darkblue"); // Highlight bar
          tooltip
            .style("opacity", 1)
            .html(`Year: ${d.label}<br>Citations: ${d.value}`)
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mousemove", function(event) {
          tooltip
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mouseout", function() {
          d3.select(this).attr("fill", "steelblue"); // Reset bar color
          tooltip.style("opacity", 0);
        })
        .merge(bars)
        .transition()
        .duration(2000)
        .attr("x", d => x(d.label))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", d => chartHeight - y(d.value));

      bars
        .exit()
        .transition()
        .duration(2000)
        .attr("y", chartHeight)
        .attr("height", 0)
        .remove();

      // Update X-axis
      svg.select(".x-axis").transition().duration(2000).call(d3.axisBottom(x));

      // Update Y-axis
      svg.select(".y-axis").transition().duration(2000).call(d3.axisLeft(y));

      // Update Title
      svg.select(".title").text(title);
    }

    const data = {
      id: 1,
      name: "Author Name",
      citations: { 2018: 5, 2019: 15, 2020: 10, 2021: 25, 2022: 20 },
    };

    // Format data for D3
    const formattedData = Object.entries(
      data.citations
    ).map(([year, count]) => ({
      year: +year,
      count: count,
    }));

    // Use formatted data to plot
    plotBarChartFromJson(formattedData, "Citations per Year");
  }
  ////////////////////////////////////////////////////////////////////////
  //                           Bottom Right                             //
  ////////////////////////////////////////////////////////////////////////
  if (bottomRightDiv) {
    function plotRankChartVertical(data, title) {
      // Format data into an array of objects
      const formattedData = Object.entries(data)
        .map(([id, count]) => ({
          id,
          count,
        }))
        .sort((a, b) => b.count - a.count); // Sort descending by count

      const width = bottomRightDiv.clientWidth;
      const height = bottomRightDiv.clientHeight;

      const margin = { top: 30, right: 40, bottom: 20, left: 120 };
      const chartWidth = width - margin.left - margin.right;
      const chartHeight = height - margin.top - margin.bottom;

      // Select or create SVG container
      let svg = d3.select(bottomRightDiv).select("svg");
      if (svg.empty()) {
        svg = d3
          .select(bottomRightDiv)
          .append("svg")
          .attr("width", width)
          .attr("height", height);

        svg
          .append("g")
          .attr("class", "bars")
          .attr("transform", `translate(${margin.left},${margin.top})`);
        svg
          .append("g")
          .attr("class", "x-axis")
          .attr(
            "transform",
            `translate(${margin.left},${margin.top + chartHeight})`
          );
        svg
          .append("g")
          .attr("class", "y-axis")
          .attr("transform", `translate(${margin.left},${margin.top})`);
        svg
          .append("text")
          .attr("class", "title")
          .attr("x", width / 2)
          .attr("y", margin.top / 2)
          .attr("text-anchor", "middle")
          .style("font-size", "16px")
          .style("font-weight", "bold");
      }

      // Scales
      const y = d3
        .scaleBand()
        .domain(formattedData.map(d => d.id)) // Use ids as labels
        .range([0, chartHeight])
        .padding(0.1);

      const x = d3
        .scaleLinear()
        .domain([0, d3.max(formattedData, d => d.count)]) // Use max count as the upper bound
        .range([0, chartWidth]);

      // Tooltip setup
      const tooltip = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("border", "1px solid #ccc")
        .style("border-radius", "4px")
        .style("padding", "5px")
        .style("pointer-events", "none");

      // Update bars
      const bars = svg
        .select(".bars")
        .selectAll(".bar")
        .data(formattedData, d => d.id);

      bars
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", 0) // Start at the leftmost point
        .attr("y", d => y(d.id))
        .attr("width", 0) // Start with width 0
        .attr("height", y.bandwidth())
        .attr("fill", "steelblue")
        .on("mouseover", function(event, d) {
          d3.select(this).attr("fill", "darkblue"); // Highlight bar
          tooltip
            .style("opacity", 1)
            .html(`ID: ${d.id}<br>Co-author Times: ${d.count}`)
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mousemove", function(event) {
          tooltip
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mouseout", function() {
          d3.select(this).attr("fill", "steelblue"); // Reset bar color
          tooltip.style("opacity", 0);
        })
        .merge(bars)
        .transition()
        .duration(2000)
        .attr("x", 0)
        .attr("y", d => y(d.id))
        .attr("width", d => x(d.count))
        .attr("height", y.bandwidth());

      bars.exit().transition().duration(2000).attr("width", 0).remove();

      // Update X-axis
      svg
        .select(".x-axis")
        .transition()
        .duration(2000)
        .call(d3.axisBottom(x).ticks(5));

      // Update Y-axis
      svg.select(".y-axis").transition().duration(2000).call(d3.axisLeft(y));

      // Update Title
      svg.select(".title").text(title);
    }

    // Example data: { id: co-author times }
    const rankData = {
      A: 15,
      B: 20,
      C: 5,
      D: 25,
      E: 10,
    };

    // Plot the vertical rank chart
    plotRankChartVertical(rankData, "Co-author Frequency by ID");
  }
});
