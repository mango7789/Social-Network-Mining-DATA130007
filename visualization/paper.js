document.addEventListener("DOMContentLoaded", () => {
  const topLeftDiv = document.querySelector(".top-left");
  const distanceDiv = document.querySelector("#distance");
  const degreeDiv = document.querySelector("#degree");
  const nodesDiv = document.querySelector("#nodes");

  ////////////////////////////////////////////////////////////////////////
  //                            Top Left                                //
  ////////////////////////////////////////////////////////////////////////
  if (topLeftDiv) {
    const jsonData = {
      "1": "Community A",
      "2": "Community B",
      "3": "Community A",
      "4": "Community C",
      "5": "Community B"
    };
  
    const edges = [
      { src: 1, dst: 2 },
      { src: 2, dst: 3 },
      { src: 3, dst: 4 },
      { src: 4, dst: 5 },
      { src: 1, dst: 5 }
    ];
  
    const nodes = Object.entries(jsonData).map(([id, community]) => ({
      id: +id,
      community
    }));
  
    const width = 800;
    const height = 600;
  
    const svg = d3.select('.top-left').append('svg')
      .attr('width', width)
      .attr('height', height);
  
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.7)')
      .style('color', 'white')
      .style('padding', '5px')
      .style('border-radius', '4px')
      .style('visibility', 'hidden');
  
    const color = d3.scaleOrdinal(d3.schemeCategory10);
  
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges)
        .id(d => d.src)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Plot links (edges)
    const link = svg.append('g')
      .selectAll('.link')
      .data(edges)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', '#aaa')
      .attr('stroke-width', 1.5);
  
    // Plot nodes
    const node = svg.append('g')
      .selectAll('.node')
      .data(nodes)
      .enter().append('circle')
      .attr('class', 'node')
      .attr('r', 10)
      .attr('fill', d => color(d.community))
      .call(d3.drag()
        .on('start', dragStart)
        .on('drag', dragged)
        .on('end', dragEnd));
  
    // Tooltip on hover
    node.on('mouseover', function (event, d) {
      tooltip.style('visibility', 'visible')
        .html(`<b>Node ID</b>: ${d.id}<br><b>Community</b>: ${d.community}`);
    })
      .on('mousemove', function (event) {
        tooltip.style('top', event.pageY + 10 + 'px')
          .style('left', event.pageX + 10 + 'px');
      })
      .on('mouseout', function () {
        tooltip.style('visibility', 'hidden');
      });
  
    // Update positions based on the simulation
    simulation.on('tick', () => {
      link
        .attr('x1', d => nodes.find(n => n.id === d.src).x)
        .attr('y1', d => nodes.find(n => n.id === d.src).y)
        .attr('x2', d => nodes.find(n => n.id === d.dst).x)
        .attr('y2', d => nodes.find(n => n.id === d.dst).y);
  
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    });
  
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
  }



  ////////////////////////////////////////////////////////////////////////
  //                           Bottom left                              //
  ////////////////////////////////////////////////////////////////////////  
  if (distanceDiv) {
    const toggleContainer = document.createElement("div");
    toggleContainer.style.position = "absolute";
    toggleContainer.style.top = "10px";
    toggleContainer.style.right = "10px";
    toggleContainer.style.backgroundColor = "white";
    toggleContainer.style.padding = "10px";
    toggleContainer.style.boxShadow = "0px 2px 5px rgba(0, 0, 0, 0.2)";
    toggleContainer.style.borderRadius = "5px";

    const label = document.createElement("label");
    label.innerText = "Select Plot: ";
    label.style.marginRight = "10px";

    const select = document.createElement("select");
    select.id = "plot-selector";

    ["Distance", "Diameter", "Average Citations"].forEach((optionText) => {
      const option = document.createElement("option");
      option.value = optionText.toLowerCase().replace(/ /g, "-");
      option.text = optionText;
      select.appendChild(option);
    });

    toggleContainer.appendChild(label);
    toggleContainer.appendChild(select);
    distanceDiv.appendChild(toggleContainer);

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
          .style("font-size", "14px");
      }

      // Scales
      const x = d3.scaleBand().range([0, chartWidth]).padding(0.1);
      const y = d3.scaleLinear().range([chartHeight, 0]);

      x.domain(data.map(d => d.label));
      y.domain([0, d3.max(data, d => d.value)]);

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
        .merge(bars)
        .transition()
        .duration(750)
        .attr("x", d => x(d.label))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", d => chartHeight - y(d.value));

      bars
        .exit()
        .transition()
        .duration(750)
        .attr("y", chartHeight)
        .attr("height", 0)
        .remove();

      // Update X-axis
      svg
        .select(".x-axis")
        .transition()
        .duration(750)
        .call(d3.axisBottom(x));

      // Update Y-axis
      svg
        .select(".y-axis")
        .transition()
        .duration(750)
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

      // Draw the curve line
      g.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 2);

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
        .select(degreeDiv)
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "rgba(0, 0, 0, 0.7)")
        .style("color", "white")
        .style("padding", "5px")
        .style("border-radius", "4px")
        .style("visibility", "hidden");

      // Mouse events for dots
      dots
        .on("mouseover", (event, d) => {
          tooltip
            .style("visibility", "visible")
            .text(`Degree: ${d.degree}, Count: ${d.count}`);
        })
        .on("mousemove", (event) => {
          tooltip
            .style("top", event.pageY + 10 + "px")
            .style("left", event.pageX + 10 + "px");
        })
        .on("mouseout", () => {
          tooltip.style("visibility", "hidden");
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
        .style("font-size", "14px")
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
     * Function to plot a pie chart for the number of nodes in each community
     * @param {Object} jsonData - JSON data in the format {community: number of nodes}
     * @param {string} title - Title for the chart
     */
    function plotPieChart(jsonData, title) {
      const data = Object.entries(jsonData).map(([community, nodes]) => ({
        community: community,
        nodes: +nodes,
      }));

      const width = nodesDiv.clientWidth;
      const height = nodesDiv.clientHeight;
      const radius = Math.min(width, height) / 2;

      // Clear previous content
      d3.select(nodesDiv).selectAll("svg").remove();

      const svg = d3
        .select(nodesDiv)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`); // Center the pie chart

      // Color scale for the pie slices
      const color = d3.scaleOrdinal(d3.schemeCategory10);

      // Create the pie chart
      const pie = d3.pie().value(d => d.nodes);

      const arc = d3.arc().outerRadius(radius - 10).innerRadius(0);

      // Draw the slices (arc paths)
      const slices = svg
        .selectAll(".slice")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "slice");

      slices
        .append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.community));

      // Add a tooltip
      const tooltip = d3
        .select(nodesDiv)
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("background", "rgba(0, 0, 0, 0.7)")
        .style("color", "white")
        .style("padding", "5px")
        .style("border-radius", "4px")
        .style("visibility", "hidden");

      // Tooltip behavior for hover events
      slices
        .on("mouseover", (event, d) => {
          tooltip
            .style("visibility", "visible")
            .html(`<b>Community</b>: ${d.data.community}<br><b>Nodes</b>: ${d.data.nodes}`);
        })
        .on("mousemove", (event) => {
          tooltip
            .style("top", event.pageY + 10 + "px")
            .style("left", event.pageX + 10 + "px");
        })
        .on("mouseout", () => {
          tooltip.style("visibility", "hidden");
        });

      // Title
      svg
        .append("text")
        .attr("x", 0)
        .attr("y", -radius - 20)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .text(title);
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
