document.addEventListener("DOMContentLoaded", () => {
    const topLeftDiv = document.querySelector(".top-left")
    ////////////////////////////////////////////////////////////////////////
    //                            Top Left                                //
    ////////////////////////////////////////////////////////////////////////
    if (topLeftDiv) {
        const nodes = [
            { id: 1, name: "Alade O. Tokuta", co_authors: [4, 16, 17], papers: ["555036b37cea80f95414a000"] },
            { id: 2, name: "Aravind Srinivasan", co_authors: [7, 10, 15], papers: ["555036b37cea80f954149ffe"] },
            { id: 3, name: "Christian Wulff-Nilsen", co_authors: [], papers: ["555036b37cea80f954149ffc"] },
            { id: 4, name: "Donghyun Kim", co_authors: [1, 16, 17], papers: ["555036b37cea80f95414a000"] },
            { id: 5, name: "Howard W. Beck", co_authors: [9, 12], papers: ["5736965d6e3b12023e56a854"] },
            { id: 6, name: "Julián Mestre", co_authors: [], papers: ["555036b37cea80f954149ffd"] },
            { id: 7, name: "Madhav V. Marathe", co_authors: [2, 10, 15], papers: ["555036b37cea80f954149ffe"] },
            { id: 8, name: "Maxime Crochemore", co_authors: [13], papers: ["555036b37cea80f954149fff"] },
            { id: 9, name: "Shamkant B. Navathe", co_authors: [5, 12], papers: ["5736965d6e3b12023e56a854"] },
            { id: 10, name: "Srinivasan Parthasarathy", co_authors: [2, 7, 15], papers: ["555036b37cea80f954149ffe"] },
            { id: 11, name: "Subrata Ghosh", co_authors: [14], papers: ["5736965d6e3b12023e56a853"] },
            { id: 12, name: "Tarek M. Anwar", co_authors: [5, 9], papers: ["5736965d6e3b12023e56a854"] },
            { id: 13, name: "Thierry Lecroq", co_authors: [8], papers: ["555036b37cea80f954149fff"] },
            { id: 14, name: "Timos K. Sellis", co_authors: [11], papers: ["5736965d6e3b12023e56a853"] },
            { id: 15, name: "V. S. Anil Kumar", co_authors: [2, 7, 10], papers: ["555036b37cea80f954149ffe"] },
            { id: 16, name: "Wei Wang", co_authors: [1, 4, 17], papers: ["555036b37cea80f95414a000"] },
            { id: 17, name: "Weili Wu", co_authors: [1, 4, 16], papers: ["555036b37cea80f95414a000"] }
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

        // Function to plot nodes and links based on the filtered data
        function plotGraph(filteredNodes, filteredEdges) {
            // Re-create links (edges)
            graphGroup.selectAll('.link')
                .data(filteredEdges)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke', '#aaa')
                .attr('stroke-width', d => d.weight);

            // Re-create nodes
            const nodeCircles = graphGroup.selectAll('.node')
                .data(filteredNodes)
                .enter().append('circle')
                .attr('class', 'node')
                .attr('r', d => logisticGrowth(d.co_authors.length))
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
                        .attr('r', d => 1.2 * logisticGrowth(d.co_authors.length));

                    tooltip.style('visibility', 'visible')
                        .html(`
                        <b>ID</b>: ${d.id}<br>
                    `);
                })
                .on('mousemove', function (event) {
                    tooltip.style('top', event.pageY + 10 + 'px')
                        .style('left', event.pageX + 10 + 'px');
                })
                .on('mouseout', function () {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('r', d => logisticGrowth(d.co_authors.length));
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

        plotGraph(nodes, edges);
    }
    ////////////////////////////////////////////////////////////////////////
    //                            Top Right                               //
    ////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////
    //                           Bottom Left                              //
    ////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////
    //                           Bottom Right                             //
    ////////////////////////////////////////////////////////////////////////
});
