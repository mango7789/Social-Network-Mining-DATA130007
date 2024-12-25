document.addEventListener("DOMContentLoaded", () => {
  const topLeftDiv = document.querySelector(".top-left");
  const topRightDiv = document.querySelector(".top-right");
  const distanceDiv = document.querySelector("#distance");
  const degreeDiv = document.querySelector("#degree");
  const nodesDiv = document.querySelector("#nodes");

  async function loadData() {
    const communityData = await d3.json("community.json");
    const linkData = await d3.csv("links.csv");
    return { communityData, linkData };
  }

  ////////////////////////////////////////////////////////////////////////
  //                            Top Left                                //
  ////////////////////////////////////////////////////////////////////////
  if (topLeftDiv) {
    // Example CSV Data as an array of objects (mimicking CSV data)
    const nodes = [
      { id: "b84f", community: "Community A", authors: "Author1", year: 2009, venue: "Venue1", out_d: 3, in_d: 5 },
      { id: 2, community: "Community B", authors: "Author2", year: 2010, venue: "Venue2", out_d: 2, in_d: 4 },
      { id: 3, community: "Community A", authors: "Author3", year: 2011, venue: "Venue3", out_d: 1, in_d: 3 },
      { id: 4, community: "Community C", authors: "Author4", year: 2015, venue: "Venue4", out_d: 4, in_d: 2 },
      { id: 5, community: "Community B", authors: "Author5", year: 2015, venue: "Venue5", out_d: 5, in_d: 20 }
    ];

    // Edges (the relationships between nodes)
    const edges = [
      { src: "b84f", dst: 2 },
      { src: "b84f", dst: 3 },
      { src: "b84f", dst: 4 },
      { src: 2, dst: 3 },
      { src: 4, dst: 5 }
    ];

    const titleData = {
      "b84f": "Title A",
      "2": "Title B",
      "3": "Title C",
      "4": "Title D",
      "5": "Title E"
    };

    const width = topLeftDiv.clientWidth;
    const height = topLeftDiv.clientHeight;

    const svg = d3.select('.top-left').append('svg')
      .attr('width', width)
      .attr('height', height);

    // Create a zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 5])  // Limits the zoom scale (from 50% to 500%)
      .on('zoom', (event) => {
        // Apply zoom transformation only to the graph group
        graphGroup.attr('transform', event.transform);
      });

    svg.call(zoom);  // Bind the zoom behavior to the SVG

    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('padding', '5px')
      .style('border-radius', '4px')
      .style('visibility', 'hidden');

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

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges)
        .id(d => d.src)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Add a group for the graph content (nodes and links)
    const graphGroup = svg.append('g');

    // Plot links (edges)
    // graphGroup.selectAll('.link')
    //   .data(edges)
    //   .enter().append('line')
    //   .attr('class', 'link')
    //   .attr('stroke', '#aaa')
    //   .attr('stroke-width', 0.5);

    function logisticGrowth(x, r_max = 30, k = 0.1, x_0 = 20) {
      return r_max / (1 + Math.exp(-k * (x - x_0)));
    }

    // Add legend on the right side (outside the zoomed group)
    const legendWidth = 150;
    const legendMargin = 20;

    const legend = svg.append('g')
      .attr('transform', `translate(${width - legendWidth - legendMargin}, ${legendMargin})`);

    const communities = [...new Set(nodes.map(d => d.community))];

    const legendItems = legend.selectAll('.legend-item')
      .data(communities)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 20})`);

    legendItems.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', d => color(d));

    legendItems.append('text')
      .attr('x', 20)
      .attr('y', 10)
      .text(d => d)
      .style('font-size', '12px')
      .style('alignment-baseline', 'middle');

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

    const yearSlider = document.getElementById('year-slider');
    const yearLabel = document.getElementById('slider-value');

    yearSlider.addEventListener('input', function () {
      const selectedYear = +this.value;
      yearLabel.textContent = selectedYear;


      // Filter nodes and edges based on the selected year
      const filteredNodes = nodes.filter(node => node.year <= selectedYear);
      const filteredEdges = edges.filter(edge =>
        filteredNodes.some(node => node.id === edge.src) && filteredNodes.some(node => node.id === edge.dst)
      );


      // Redraw the graph with filtered data
      graphGroup.selectAll('.node').remove();
      graphGroup.selectAll('.link').remove();
      graphGroup.selectAll('.node-label').remove();

      // Re-plot links and nodes based on filtered data
      plotGraph(filteredNodes, filteredEdges);
    });

    // Function to plot nodes and links based on the filtered data
    function plotGraph(filteredNodes, filteredEdges) {
      // Re-create links (edges)
      graphGroup.selectAll('.link')
        .data(filteredEdges)
        .enter().append('line')
        .attr('class', 'link')
        .attr('stroke', '#aaa')
        .attr('stroke-width', 0.5);

      // Re-create nodes
      const nodeCircles = graphGroup.selectAll('.node')
        .data(filteredNodes)
        .enter().append('circle')
        .attr('class', 'node')
        .attr('r', d => logisticGrowth(d.in_d))
        .attr('fill', d => color(d.community))
        .call(d3.drag()
          .on('start', dragStart)
          .on('drag', dragged)
          .on('end', dragEnd));

      const nodeLabels = graphGroup.selectAll('.node-label')
        .data(filteredNodes)
        .enter().append('text')
        .attr('class', 'node-label')
        .attr('text-anchor', 'middle')
        .attr('dy', 4) // Adjust vertical alignment
        .style('font-size', '10px')
        .style('pointer-events', 'none') // Prevent interference with drag events
        .text(d => d.id);

      // Tooltip on hover
      nodeCircles
        .on('mouseover', function (event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', d => 1.2 * logisticGrowth(d.in_d));

          tooltip.style('visibility', 'visible')
            .html(`
        <b>ID</b>: ${d.id}<br>
        <b>Title</b>: ${titleData[d.id]}<br>
        <b>Authors</b>: ${d.authors}<br>
        <b>Year</b>: ${d.year}<br>
        <b>Venue</b>: ${d.venue}<br>
        <b>Reference(s)</b>: ${d.out_d}<br>
        <b>Citation(s)</b>: ${d.in_d}`
            );
        })
        .on('mousemove', function (event) {
          tooltip.style('top', event.pageY + 10 + 'px')
            .style('left', event.pageX + 10 + 'px');
        })
        .on('mouseout', function () {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', d => logisticGrowth(d.in_d));
          tooltip.style('visibility', 'hidden');
        });

      simulation.nodes(filteredNodes).on('tick', ticked);
      simulation.force('link').links(edges);

      // Restart the simulation to apply new data and layout
      simulation.alpha(1).restart();

      function ticked() {
        graphGroup.selectAll('.link')
          .attr('x1', d => filteredNodes.find(n => n.id === d.src).x)
          .attr('y1', d => filteredNodes.find(n => n.id === d.src).y)
          .attr('x2', d => filteredNodes.find(n => n.id === d.dst).x)
          .attr('y2', d => filteredNodes.find(n => n.id === d.dst).y);

        nodeCircles
          .attr('cx', d => d.x)
          .attr('cy', d => d.y);

        nodeLabels
          .attr('x', d => d.x)
          .attr('y', d => d.y);
      }
    }

    // Initialize with the full data
    yearSlider.value = 2016;
    yearLabel.textContent = '2016';

    plotGraph(nodes, edges);

    // // Reset the simulation when the year is changed
    // // TODO: When need efficiency, uncomment this code to transfer the task of filtering data to backend server
    // fetch(`/getFilteredData?year=${selectedYear}`)
    //   .then(response => response.json())  // Assuming the server returns JSON
    //   .then(data => {
    //     // Filter nodes and edges for the selected year
    //     const filteredNodes = data.nodes.filter(node => node.year <= selectedYear);
    //     const filteredEdges = data.edges.filter(edge =>
    //       filteredNodes.some(node => node.id === edge.src) && filteredNodes.some(node => node.id === edge.dst)
    //     );

    //     // Now update the graph with the filtered data
    //     updateGraph(filteredNodes, filteredEdges);
    //   })
    //   .catch(error => {
    //     console.error('Error fetching data:', error);
    //   });
  }
  ////////////////////////////////////////////////////////////////////////
  //                            Top Right                               //
  ////////////////////////////////////////////////////////////////////////
  if (topRightDiv) {
    function renderPaginatedTable(data, community = "") {
      let currentPage = 1;
      const rowsPerPage = 12; // Number of rows per page
      const maxVisiblePages = 8; // Maximum number of page numbers displayed

      // Filter data based on community
      const filteredData = community
        ? data.filter((item) => item.venue.toLowerCase() === community.toLowerCase())
        : data;

      // Sort data in reverse order of citation
      const sortedData = filteredData.sort((a, b) => b.citation - a.citation);

      // Function to render the table
      function renderTable() {
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const pageData = sortedData.slice(start, end);

        // Clear existing rows
        const tbody = document.querySelector("#data-table tbody");
        tbody.innerHTML = "";

        // Populate rows for the current page
        pageData.forEach((item, index) => {
          setTimeout(() => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${item.id}</td>
              <td>${item.title}</td>
              <td>${item.year}</td>
              <td>${item.venue}</td>
              <td>${item.references}</td>
              <td>${item.citation}</td>
            `;

            // Add fade-in animation
            row.classList.add("fade-in");
            tbody.appendChild(row);
          }, index * 100);
        });

        updatePagination();
      }

      // Function to update pagination controls
      function updatePagination() {
        const totalPages = Math.ceil(sortedData.length / rowsPerPage);
        const paginationContainer = document.getElementById("pagination-controls");
        paginationContainer.innerHTML = "";

        // Add Prev button
        const prevButton = document.createElement("button");
        prevButton.textContent = "Prev";
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener("click", () => {
          currentPage--;
          renderTable();
        });
        paginationContainer.appendChild(prevButton);

        // Calculate page range to display
        const startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        for (let i = startPage; i <= endPage; i++) {
          const button = document.createElement("button");
          button.textContent = i;
          if (i === currentPage) {
            button.className = "active";
          }
          button.addEventListener("click", () => {
            currentPage = i;
            renderTable();
          });
          paginationContainer.appendChild(button);
        }

        // Add Next button
        const nextButton = document.createElement("button");
        nextButton.textContent = "Next";
        nextButton.disabled = currentPage === totalPages;
        nextButton.addEventListener("click", () => {
          currentPage++;
          renderTable();
        });
        paginationContainer.appendChild(nextButton);
      }

      // Initial render
      renderTable();
    }

    const data = [
      { id: "bf66", title: "cc", year: 2015, venue: "Sigmod", references: 5, citation: 126 },
      { id: "bf67", title: "dd", year: 2016, venue: "ICDE", references: 3, citation: 110 },
      { id: "bf68", title: "ee", year: 2017, venue: "VLDB", references: 6, citation: 95 },
      { id: "bf69", title: "ff", year: 2018, venue: "WWW", references: 10, citation: 230 },
      { id: "bf70", title: "gg", year: 2019, venue: "KDD", references: 8, citation: 150 },
      { id: "bf71", title: "hh", year: 2020, venue: "SIGMOD", references: 4, citation: 99 },
      { id: "bf72", title: "ii", year: 2021, venue: "ICML", references: 7, citation: 140 },
      { id: "bf73", title: "jj", year: 2022, venue: "NeurIPS", references: 2, citation: 50 },
      { id: "bf74", title: "kk", year: 2023, venue: "CVPR", references: 9, citation: 175 },
      { id: "bf75", title: "ll", year: 2024, venue: "ICLR", references: 6, citation: 115 },
      { id: "bf76", title: "mm", year: 2024, venue: "ICLR", references: 6, citation: 115 },
      { id: "bf77", title: "nn", year: 2024, venue: "ICLR", references: 6, citation: 115 },
      { id: "bf78", title: "oo", year: 2024, venue: "ICLR", references: 6, citation: 115 },
    ];

    // Test example
    renderPaginatedTable(data, ""); // Show all data
    // renderPaginatedTable(data, "ICLR"); // Show data only for the community "ICLR"
  }
  ////////////////////////////////////////////////////////////////////////
  //                           Bottom left                              //
  ////////////////////////////////////////////////////////////////////////  
  if (distanceDiv) {
    const select = document.createElement("select");
    select.id = "plot-selector";

    ["Distance", "Diameter", "Average Citations"].forEach((optionText) => {
      const option = document.createElement("option");
      option.value = optionText.toLowerCase().replace(/ /g, "-");
      option.text = optionText;
      select.appendChild(option);
    });

    select.style.position = "absolute";
    select.style.top = "10px";
    select.style.right = "10px";

    distanceDiv.style.position = "relative";
    distanceDiv.appendChild(select);

    // Function to plot bar chart
    function plotBarChartFromJson(jsonData, title) {
      const data = Object.entries(jsonData).map(([key, value]) => ({ label: key, value }));

      const width = distanceDiv.clientWidth;
      const height = distanceDiv.clientHeight;

      const margin = { top: 30, right: 20, bottom: 40, left: 40 };
      const chartWidth = width - margin.left - margin.right;
      const chartHeight = height - margin.top - margin.bottom;

      // Select or create SVG container
      let svg = d3.select(distanceDiv).select("svg");
      if (svg.empty()) {
        svg = d3
          .select(distanceDiv)
          .append("svg")
          .attr("width", width)
          .attr("height", height);

        svg.append("g").attr("class", "bars").attr("transform", `translate(${margin.left},${margin.top})`);
        svg.append("g").attr("class", "x-axis").attr("transform", `translate(${margin.left},${margin.top + chartHeight})`);
        svg.append("g").attr("class", "y-axis").attr("transform", `translate(${margin.left},${margin.top})`);
        svg.append("text").attr("class", "title")
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
      const tooltip = d3.select('body')
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background", "white")
        .style("border", "1px solid #ccc")
        .style("border-radius", "4px")
        .style("padding", "5px")
        .style("pointer-events", "none");

      console.log(tooltip);

      // Update bars with smooth transition
      const bars = svg.select(".bars").selectAll(".bar").data(data, d => d.label);

      bars
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.label))
        .attr("y", chartHeight) // Start at the bottom
        .attr("width", x.bandwidth())
        .attr("height", 0) // Start with height 0
        .attr("fill", "steelblue")
        .on("mouseover", function (event, d) {
          d3.select(this).attr("fill", "darkblue"); // Highlight bar
          tooltip
            .style("opacity", 1)
            .html(`X: ${d.label}<br>Y: ${d.value}`)
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mousemove", function (event) {
          tooltip
            .style("left", `${event.pageX + 10}px`)
            .style("top", `${event.pageY - 20}px`);
        })
        .on("mouseout", function () {
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
      svg
        .select(".x-axis")
        .transition()
        .duration(2000)
        .call(d3.axisBottom(x));

      // Update Y-axis
      svg
        .select(".y-axis")
        .transition()
        .duration(2000)
        .call(d3.axisLeft(y));

      // Update Title
      svg
        .select(".title")
        .text(title);
    }

    // Initial plot
    plotBarChartFromJson({ A: 10, B: 15, C: 7 }, "Distance");

    // Event listener for dropdown
    const plotSelector = document.querySelector("#plot-selector");
    if (plotSelector) {
      plotSelector.addEventListener("change", event => {
        const selected = event.target.value;
        const title = plotSelector.options[plotSelector.selectedIndex].text;
        let jsonData;

        if (selected === "distance") {
          jsonData = { A: 10, B: 15, C: 7 };
        } else if (selected === "diameter") {
          jsonData = { D: 20, E: 25, F: 15 };
        } else if (selected === "average-citations") {
          jsonData = { A: 5, B: 8, C: 3 };
        }

        plotBarChartFromJson(jsonData, title);
      });
    }
  }
  ////////////////////////////////////////////////////////////////////////
  //                          Bottom middle                             //
  //////////////////////////////////////////////////////////////////////// 
  if (degreeDiv) {
    /**
     * Function to plot degree distribution with smooth curves
     * @param {Object} jsonData - JSON data in the format {degree: num}
     * @param {string} title - Title for the chart
     */
    function plotDegreeDistribution(jsonData, title) {
      const data = Object.entries(jsonData).map(([degree, count]) => ({
        degree: +degree,
        count: +count,
      }));

      const width = degreeDiv.clientWidth;
      const height = degreeDiv.clientHeight;

      // Clear previous content
      d3.select(degreeDiv).selectAll("svg").remove();

      const svg = d3
        .select(degreeDiv)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      const margin = { top: 30, right: 20, bottom: 40, left: 50 };
      const chartWidth = width - margin.left - margin.right;
      const chartHeight = height - margin.top - margin.bottom;

      const g = svg
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Scales
      const x = d3
        .scaleBand()
        .range([0, chartWidth])
        .padding(0.1)
        .domain(data.map((d) => d.degree));

      const y = d3
        .scaleLinear()
        .range([chartHeight, 0])
        .domain([0, d3.max(data, (d) => d.count)]);

      // Create line path for the curve plot
      const line = d3
        .line()
        .x((d) => x(d.degree) + x.bandwidth() / 2) // Use the center of each band for a smooth curve
        .y((d) => y(d.count))
        .curve(d3.curveCardinal); // Spline curve technique

      // Draw the curve line with animation
      g.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line) // This defines the final path, which will be animated
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", function () {
          return this.getTotalLength();  // Get the length of the path
        })
        .attr("stroke-dashoffset", function () {
          return this.getTotalLength();  // Initially set the offset to the path length (invisible line)
        })
        .transition() // Apply transition to the line drawing
        .duration(2000) // Duration of the animation (2 seconds)
        .attr("stroke-dashoffset", 0); // Set the dashoffset to 0 to reveal the line


      // Draw the dots at each data point
      const dots = g
        .selectAll(".dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("cx", (d) => x(d.degree) + x.bandwidth() / 2) // Center of each band
        .attr("cy", (d) => y(d.count))
        .attr("r", 4) // Size of the dot
        .attr("fill", "red")
        .attr("stroke", "black")
        .attr("stroke-width", 1);

      // Tooltip (hidden by default)
      const tooltip = d3
        .select('body')
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("padding", "5px")
        .style("border-radius", "4px")
        .style("visibility", "hidden");

      // Mouse events for dots with radius increase on hover
      dots
        .on("mouseover", (event, d) => {
          tooltip
            .style("visibility", "visible")
            .text(`Degree: ${d.degree}, Count: ${d.count}`);

          // Increase radius on hover
          d3.select(event.target)
            .transition()
            .attr("r", 4 * 1.5); // Increase radius by 1.1x
        })
        .on("mousemove", (event) => {
          tooltip
            .style("top", event.pageY + 10 + "px")
            .style("left", event.pageX + 10 + "px");
        })
        .on("mouseout", (event) => {
          tooltip.style("visibility", "hidden");

          // Reset radius when mouse leaves
          d3.select(event.target)
            .transition()
            .attr("r", 4); // Reset radius to original size
        });


      // X-axis
      g.append("g")
        .attr("transform", `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x))
        .append("text")
        .attr("y", 35)
        .attr("x", chartWidth / 2)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text("Degree");

      // Y-axis
      g.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -chartHeight / 2)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .text("Count");

      // Title
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", margin.top / 2)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("font-weight", "bold")
        .text(title);
    }

    // Example data
    const globalDegreeData = { 1: 34, 2: 888, 3: 999, 4: 234, 5: 10 };

    // Initial plot
    plotDegreeDistribution(globalDegreeData, "Degree Distribution");
  }
  ////////////////////////////////////////////////////////////////////////
  //                          Bottom right                              //
  //////////////////////////////////////////////////////////////////////// 
  if (nodesDiv) {
    /**
   * Function to plot a donut chart with text labels, percentages, and tooltips
   * @param {Object} jsonData - JSON data in the format {community: number of nodes}
   * @param {string} title - Title for the chart
   */
    function plotPieChart(jsonData, title) {
      const data = Object.entries(jsonData).map(([community, nodes]) => ({
        label: community,
        value: +nodes,
      }));

      const width = nodesDiv.clientWidth;
      const height = nodesDiv.clientHeight;
      const radius = Math.min(width, height) / 2 - 40;

      // Clear previous content
      d3.select(nodesDiv).selectAll("svg").remove();
      d3.select(nodesDiv).selectAll(".chart-title").remove();

      // Add the title to the top center of the div
      d3.select(nodesDiv)
        .append("div")
        .attr("class", "chart-title")
        .style("position", "absolute")
        .style("top", "2px")
        .style("left", "50%")
        .style("transform", "translateX(-50%)")
        .style("text-align", "center")
        .style("font-size", "16px")
        .style("font-weight", "bold")
        .text(title);

      const svg = d3
        .select(nodesDiv)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

      const color = d3.scaleOrdinal(d3.schemeCategory10);

      const pie = d3
        .pie()
        .sort(null)
        .value((d) => d.value);

      const arc = d3
        .arc()
        .outerRadius(radius * 0.8)
        .innerRadius(radius * 0.4);
      const hoverArc = d3
        .arc()
        .outerRadius(radius * 0.85)
        .innerRadius(radius * 0.35);
      const outerArc = d3
        .arc()
        .innerRadius(radius * 0.9)
        .outerRadius(radius * 0.9);

      // Tooltip setup
      const tooltip = d3
        .select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("padding", "5px")
        .style("border-radius", "4px")
        .style("visibility", "hidden");

      // Draw slices with animation
      const slices = svg
        .append("g")
        .attr("class", "slices")
        .selectAll("path.slice")
        .data(pie(data))
        .enter()
        .append("path")
        .attr("class", "slice")
        .style("fill", (d) => color(d.data.label))
        .each(function (d) {
          this._current = { startAngle: 0, endAngle: 0 };
        })
        .on("mouseover", function (event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr("d", hoverArc); // Grow slice on hover

          tooltip
            .style("visibility", "visible")
            .html(`<b>Community:</b> ${d.data.label}<br><b>Nodes:</b> ${d.data.value}`);
        })
        .on("mousemove", function (event) {
          tooltip.style("top", event.pageY + 10 + "px").style("left", event.pageX + 10 + "px");
        })
        .on("mouseout", function () {
          d3.select(this)
            .transition()
            .duration(200)
            .attr("d", arc); // Reset slice size on mouse out

          tooltip.style("visibility", "hidden");
        })
        .transition()
        .duration(2000)
        .attrTween("d", function (d) {
          const interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(1);
          return function (t) {
            return arc(interpolate(t));
          };
        });

      // Add percentages to slices
      svg
        .append("g")
        .attr("class", "percentages")
        .selectAll("text")
        .data(pie(data))
        .enter()
        .append("text")
        .attr("dy", ".35em")
        .text((d) => `${((d.data.value / d3.sum(data, (d) => d.value)) * 100).toFixed(1)}%`)
        .attr("transform", (d) => `translate(${arc.centroid(d)})`)
        .style("text-anchor", "middle")
        .style("font-size", "10px")
        .style("fill", "white")
        .each(function (d) {
          this._current = { startAngle: 0, endAngle: 0 }; // Store the initial state for animation
        })
        .transition()
        .duration(2000)
        .attrTween("transform", function (d) {
          const interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(1);
          return function (t) {
            const d2 = interpolate(t);
            return `translate(${arc.centroid(d2)})`;
          };
        });

      // Add text labels outside with connecting polylines
      const text = svg
        .append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(pie(data))
        .enter()
        .append("text")
        .attr("dy", ".35em")
        .text((d) => d.data.label)
        .attr("transform", (d) => {
          const pos = outerArc.centroid(d);
          pos[0] = radius * 0.95 * (midAngle(d) < Math.PI ? 1 : -1);
          return `translate(${pos})`;
        })
        .style("text-anchor", (d) => (midAngle(d) < Math.PI ? "start" : "end"))
        .style("font-size", "14px");

      svg
        .append("g")
        .attr("class", "lines")
        .selectAll("polyline")
        .data(pie(data))
        .enter()
        .append("polyline")
        .attr("points", (d) => {
          const pos = outerArc.centroid(d);
          pos[0] = radius * 0.95 * (midAngle(d) < Math.PI ? 1 : -1);
          return [arc.centroid(d), outerArc.centroid(d), pos];
        })
        .style("opacity", 0.3)
        .style("stroke", "black")
        .style("stroke-width", "2px")
        .style("fill", "none");

      function midAngle(d) {
        return d.startAngle + (d.endAngle - d.startAngle) / 2;
      }
    }

    // Example data for the number of nodes in each community
    const nodesData = {
      "Community A": 100,
      "Community B": 150,
      "Community C": 80,
      "Community D": 120,
      "Community E": 60,
    };

    // Initial plot
    plotPieChart(nodesData, "Number of Nodes in Each Community");

  }
});
