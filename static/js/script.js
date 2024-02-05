const baseURL = 'http://localhost:9090'

const defaultFilterParams = {
    geographies: ["Germany","Spain","France"],
    genders: ["Male","Female"],
    churns: [1,0]
};
 
$(document).ready(function() {
    $('#geographyDropdown').select2();
    $('#genderDropdown').select2();
    $('#churnDropdown').select2();
});

document.addEventListener('DOMContentLoaded', function() {
    fetchFilterOptions(); // New function to load dropdown options
    loadData(); // Load data on page load with default parameters
});

function fetchFilterOptions() {
    document.getElementById('filter-spinner').style.display = 'inherit';

    fetch('/api/filter_options')
    .then(response => response.json())
    .then(data => {
        document.getElementById('filter-spinner').style.display = 'none';
        document.getElementById('filter-form').style.display = 'inherit';

        populateDropdown('geographyDropdown', data.Country);
        populateDropdown('genderDropdown', data.Gender);
        populateDropdown('churnDropdown', data.Churn);
    })
    .catch(error => {
        document.getElementById('filter-spinner').style.display = 'none';
        console.error('Error fetching filter options:', error)
    });
}

function populateDropdown(dropdownId, options) {
    const dropdown = document.getElementById(dropdownId);
    dropdown.innerHTML = ''; // Clear existing options
    options.forEach(option => {
        const optElement = document.createElement('option');
        optElement.value = option;
        optElement.textContent = option;
        if (dropdownId == 'geographyDropdown' && defaultFilterParams.geographies.includes(option) ) {
            optElement.selected = true;
        }
        
        if (dropdownId == 'genderDropdown' && defaultFilterParams.genders.includes(option) ) {
            optElement.selected = true;
        }
        if (dropdownId == 'churnDropdown' && defaultFilterParams.churns.includes(option) ) {
            optElement.selected = true;
        }
        dropdown.appendChild(optElement);
    });
}

function loadData(params = defaultFilterParams) {

    updateAllVisualBoxes('none');
    updateSpinnerOfAllVisualBoxes('inherit');
    
    const {genders, geographies, churns} = params;

    const geographiesCommaDelimited = geographies.join(',');
    const gendersCommaDelimited = genders.join(',');
    const churnsCommaDelimited = churns.join(',');

    let queryAPI = `/api/filter_data/${encodeURIComponent(gendersCommaDelimited)}/${encodeURIComponent(geographiesCommaDelimited)}/${encodeURIComponent(churnsCommaDelimited)}`;
    let queryURL = baseURL + queryAPI;

    fetch(queryURL, {
        method: 'GET', // Adjust as needed
        // Add parameters to the request if necessary
    })
    .then(response => response.json())
    .then(data => {
        updateSpinnerOfAllVisualBoxes('none');
        updateAllVisualBoxes('inherit');
        renderCharts(data);
    })
    .catch(error => {
        updateSpinnerOfAllVisualBoxes('none');
        updateAllVisualBoxes('none');
        console.error('Error fetching data:', error)
    });
}

function updateAllVisualBoxes(displayValue) {
    var elems = document.querySelectorAll('.visual-box');
    elems.forEach(function (el) {
        el.style.display = displayValue;
    });
}

function updateSpinnerOfAllVisualBoxes(displayValue) {
    document.getElementById('pie-chart-spinner').style.display = displayValue;
    document.getElementById('bar-chart-spinner').style.display =  displayValue;
    document.getElementById('map-spinner').style.display =  displayValue;
    document.getElementById('box-plot-spinner').style.display =  displayValue;
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
}

function updateData() {
    const geographyDropdownValue = getSelectedOptions('geographyDropdown');
    const genderDropdownValue = getSelectedOptions('genderDropdown');
    const churnDropdownValue = getSelectedOptions('churnDropdown');
    loadData({ geographies: geographyDropdownValue, genders: genderDropdownValue , churns: churnDropdownValue });
}

function getSelectedOptions(dropdownId) {
    const selectElement = document.getElementById(dropdownId);
    const selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value);
    console.log("Selected values:", selectedValues); // Logs an array of selected option values
    // To get the text of selected options
    const selectedTexts = Array.from(selectElement.selectedOptions).map(option => option.text);
    console.log("Selected texts:", selectedTexts); // Logs an array of the text of selected options
    return selectedValues; // Or return selectedTexts if you need the texts
}