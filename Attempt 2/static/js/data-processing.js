// data-processing.js
// Example using D3.js for loading data and Plotly for creating a chart

document.addEventListener('DOMContentLoaded', function() {
    // Load and process the CSV data
    d3.csv("./static/data/train.csv").then(function(data) {
        console.log("Data loaded successfully:", data);
        // Example processing: Count the number of customers by gender
        const genderCounts = d3.rollup(data, v => v.length, d => d.Gender);
        console.log("Gender counts:", genderCounts);

        // Convert the Map to a format suitable for Plotly
        const genderData = Array.from(genderCounts, ([key, value]) => ({gender: key, count: value}));
        
        // Plotly chart for Gender Analysis
        const plotData = [{
            type: 'bar',
            x: genderData.map(d => d.gender),
            y: genderData.map(d => d.count),
            marker: {
                color: 'blue'
            }
        }];

        const layout = {
            title: 'Gender Distribution',
            xaxis: {
                title: 'Gender'
            },
            yaxis: {
                title: 'Count'
            }
        };

        Plotly.newPlot('gender-chart', plotData, layout);
    }).catch(function(error) {
        console.error("Error loading the CSV data:", error);
    });
});
