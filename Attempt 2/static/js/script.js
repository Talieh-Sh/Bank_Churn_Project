const baseURL = 'http://localhost:9090/'

document.addEventListener('DOMContentLoaded', function() {
    fetchFilterOptions(); // New function to load dropdown options
    loadData(); // Load data on page load with default parameters
});

function fetchFilterOptions() {
    fetch('/api/filter_options')
    .then(response => response.json())
    .then(data => {
        populateDropdown('dropdown1', data.Country);
        populateDropdown('dropdown2', data.Gender);
    })
    .catch(error => console.error('Error fetching filter options:', error));
}

function populateDropdown(dropdownId, options) {
    const dropdown = document.getElementById(dropdownId);
    dropdown.innerHTML = ''; // Clear existing options
    options.forEach(option => {
        const optElement = document.createElement('option');
        optElement.value = option;
        optElement.textContent = option;
        dropdown.appendChild(optElement);
    });
}

function loadData(params = {}) {

    
    let gender = "M";
    let country = "1";
    let churn = "0";

    let queryAPI = `/api/filter_data/${gender}/${country}/${churn}`;
    let queryURL = baseURL + queryAPI;

    fetch(queryURL, {
        method: 'GET', // Adjust as needed
        // Add parameters to the request if necessary
    })
    .then(response => response.json())
    .then(data => {
        renderCharts(data);
    })
    .catch(error => console.error('Error fetching data:', error));
}

function renderCharts(response) {
    console.log("Data loaded successfully:", response);
    // Render charts based on the fetched data
    // Example: new Chart(document.getElementById('pie-chart').getContext('2d'), {...});
    renderPieChart(response.data);

}
function renderPieChart(data) {
   
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
    Plotly.newPlot('gender-chart2', plotData, layout);
    Plotly.newPlot('gender-chart3', plotData, layout);
}

function updateData() {
    const dropdown1Value = document.getElementById('dropdown1').value;
    const dropdown2Value = document.getElementById('dropdown2').value;
    loadData({ country: dropdown1Value, gender: dropdown2Value });
}
