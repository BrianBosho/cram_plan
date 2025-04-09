// Function to fetch available objects and populate dropdown
function populateObjectDropdowns() {
    fetch('/get_objects')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const objects = data.objects;
                const sourceDropdown = document.getElementById('source-object');
                const destContainer = document.getElementById('destination-objects-list');
                
                // Clear existing options (except the default)
                while (sourceDropdown.options.length > 1) {
                    sourceDropdown.remove(1);
                }
                
                // Clear destination list
                destContainer.innerHTML = '';
                
                // Add objects to source dropdown and destination list
                objects.forEach(obj => {
                    // Add to source dropdown
                    const option = document.createElement('option');
                    option.value = obj.name;
                    option.textContent = obj.name;
                    sourceDropdown.appendChild(option);
                    
                    // Add to destination list as checkbox
                    const checkDiv = document.createElement('div');
                    checkDiv.className = 'form-check';
                    checkDiv.innerHTML = `
                        <input class="form-check-input dest-object-check" type="checkbox" 
                               value="${obj.name}" id="dest-${obj.name}">
                        <label class="form-check-label" for="dest-${obj.name}">
                            ${obj.name}
                        </label>
                    `;
                    destContainer.appendChild(checkDiv);
                });
            }
        })
        .catch(error => console.error('Error fetching objects:', error));
}

// Toggle destination objects list based on "Use all objects" checkbox
document.getElementById('use-all-objects')?.addEventListener('change', function() {
    const destList = document.getElementById('destination-objects-list');
    if (this.checked) {
        destList.classList.add('hidden');
    } else {
        destList.classList.remove('hidden');
    }
});

// Handle object distances form submission
document.getElementById('object-distances-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    showLoader();
    
    const sourceObject = document.getElementById('source-object').value;
    const useAllObjects = document.getElementById('use-all-objects').checked;
    const topN = document.getElementById('top-n').value;
    
    let destinationObjects = [];
    if (!useAllObjects) {
        const checkedBoxes = document.querySelectorAll('.dest-object-check:checked');
        destinationObjects = Array.from(checkedBoxes).map(cb => cb.value);
    }
    
    fetch('/calculate_object_distances', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            source_object: sourceObject,
            destination_objects: destinationObjects,
            top_n: parseInt(topN),
            use_all_objects: useAllObjects
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.status === 'success') {
            // Display distances in results area
            displayObjectDistances(data.distances);
        } else {
            showAlert('error', 'Failed to calculate distances: ' + data.message);
        }
    })
    .catch(error => {
        hideLoader();
        showAlert('error', 'Error calculating distances: ' + error);
    });
});

// Visualize 3D distances button
document.getElementById('btn-visualize-3d-distances')?.addEventListener('click', function() {
    showLoader();
    fetch('/visualize_3d_distances')
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (data.status === 'success') {
                displayImage(data.image_url, 'Distance Visualization');
            } else {
                showAlert('error', 'Failed to visualize distances: ' + data.message);
            }
        })
        .catch(error => {
            hideLoader();
            showAlert('error', 'Error visualizing distances: ' + error);
        });
});

// Display object distances in a nicely formatted table
function displayObjectDistances(distances) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';
    
    const table = document.createElement('table');
    table.className = 'table table-striped table-hover';
    
    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr>
            <th>Object 1</th>
            <th>Object 2</th>
            <th>Distance (m)</th>
        </tr>
    `;
    
    const tbody = document.createElement('tbody');
    
    distances.forEach(dist => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${dist.object1}</td>
            <td>${dist.object2}</td>
            <td>${dist.distance.toFixed(3)}</td>
        `;
        tbody.appendChild(row);
    });
    
    table.appendChild(thead);
    table.appendChild(tbody);
    resultsContainer.appendChild(table);
    
    // Show the results area
    document.getElementById('results-area').classList.remove('hidden');
}

// Update the top-n value display
document.getElementById('top-n')?.addEventListener('input', function() {
    document.getElementById('top-n-value').textContent = this.value + ' results';
});

// Call this function when the page loads to populate object dropdowns
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Populate object dropdowns (for distance calculation)
    populateObjectDropdowns();
    
    // Set up tab event listeners to refresh object lists when switching tabs
    const distancesTab = document.querySelector('[data-bs-target="#distances-functions"]');
    if (distancesTab) {
        distancesTab.addEventListener('shown.bs.tab', populateObjectDropdowns);
    }
}); 