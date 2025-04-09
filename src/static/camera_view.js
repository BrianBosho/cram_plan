// camera_view.js - Frontend JavaScript for PyCRAM Camera Interface

// Global state
let availableObjects = [];
let imageGallery = [];

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI event listeners
    initUIElements();
    
    // Setup form event listeners
    setupFormListeners();
    
    // Setup slider value displays
    setupSliderValueDisplays();
});

// Initialize UI elements and basic event listeners
function initUIElements() {
    // Simulation Controls
    document.getElementById('btn-initialize-world').addEventListener('click', initializeWorld);
    document.getElementById('btn-create-objects').addEventListener('click', createObjects);
    document.getElementById('btn-add-objects').addEventListener('click', addObjects);
    document.getElementById('btn-run-robot-actions').addEventListener('click', runRobotActions);
    document.getElementById('btn-exit-world').addEventListener('click', exitWorld);
    
    // Camera Controls
    document.getElementById('btn-capture-image').addEventListener('click', captureImage);
    document.getElementById('btn-demo-camera').addEventListener('click', demoCamera);
    document.getElementById('btn-visualize-depth').addEventListener('click', visualizeDepthMap);
    document.getElementById('btn-identify-objects').addEventListener('click', identifyObjects);
    document.getElementById('btn-advanced-demo').addEventListener('click', advancedCameraDemo);
    
    // Show/hide custom object field
    document.getElementById('object-choice').addEventListener('change', function() {
        const customField = document.getElementById('custom-object');
        if (this.value === 'custom') {
            customField.classList.remove('hidden');
        } else {
            customField.classList.add('hidden');
        }
    });
    
    // Show/hide save path field
    document.getElementById('save-image').addEventListener('change', function() {
        const savePathContainer = document.getElementById('save-path-container');
        if (this.checked) {
            savePathContainer.classList.remove('hidden');
        } else {
            savePathContainer.classList.add('hidden');
        }
    });
}

// Setup form submission handlers
function setupFormListeners() {
    // Spawn Object Form
    document.getElementById('spawn-object-form').addEventListener('submit', function(e) {
        e.preventDefault();
        spawnObject();
    });
    
    // Object Visibility Form
    document.getElementById('object-visibility-form').addEventListener('submit', function(e) {
        e.preventDefault();
        checkObjectVisibility();
    });
    
    // Occluding Objects Form
    document.getElementById('occluding-objects-form').addEventListener('submit', function(e) {
        e.preventDefault();
        findOccludingObjects();
    });
    
    // Look At Object Form
    document.getElementById('look-at-object-form').addEventListener('submit', function(e) {
        e.preventDefault();
        lookAtObject();
    });
    
    // Scan Environment Form
    document.getElementById('scan-environment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        scanEnvironment();
    });
    
    // Object Distances Form
    document.getElementById('object-distances-form').addEventListener('submit', function(e) {
        e.preventDefault();
        calculateObjectDistances();
    });
    
    // Visualize 3D Distances button
    document.getElementById('btn-visualize-3d-distances').addEventListener('click', function() {
        visualize3DDistances();
    });
}

// Setup slider value displays
function setupSliderValueDisplays() {
    // Target Distance Slider
    document.getElementById('target-distance').addEventListener('input', function() {
        document.getElementById('target-distance-value').textContent = `${this.value} m`;
    });
    
    // Visibility Threshold Slider
    document.getElementById('visibility-threshold').addEventListener('input', function() {
        document.getElementById('visibility-threshold-value').textContent = this.value;
    });
    
    // Look Distance Slider
    document.getElementById('look-distance').addEventListener('input', function() {
        document.getElementById('look-distance-value').textContent = `${this.value} m`;
    });
    
    // Elevation Angle Slider
    document.getElementById('elevation-angle').addEventListener('input', function() {
        document.getElementById('elevation-angle-value').textContent = `${this.value}°`;
    });
    
    // Azimuth Angle Slider
    document.getElementById('azimuth-angle').addEventListener('input', function() {
        document.getElementById('azimuth-angle-value').textContent = `${this.value}°`;
    });
    
    // Scan Angles Slider
    document.getElementById('scan-angles').addEventListener('input', function() {
        document.getElementById('scan-angles-value').textContent = `${this.value} angles`;
    });
}

// Helper Functions
function showLoading() {
    document.getElementById('loading-indicator').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-indicator').classList.add('hidden');
}

// Add a timeout to ensure the loader is hidden after a certain time (failsafe)
function showLoadingWithTimeout(timeoutMs = 10000) {
    showLoading();
    // Set a timeout to automatically hide the loading indicator after a certain period
    setTimeout(() => {
        hideLoading();
    }, timeoutMs);
}

function showStatus(message, isError = false) {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.style.color = isError ? 'red' : 'black';
}

function displayImage(imageData) {
    if (!imageData) return;
    
    const imgElement = document.getElementById('camera-image');
    imgElement.src = `data:image/png;base64,${imageData}`;
    imgElement.classList.remove('hidden');
}

function refreshObjectLists() {
    fetch('/get_available_objects')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                availableObjects = data.objects;
                
                // Update all select elements that contain object options
                const objectSelects = [
                    'visibility-object',
                    'occluded-object',
                    'look-at-object',
                    'source-object'  // Add source-object to the list
                ];
                
                objectSelects.forEach(selectId => {
                    const select = document.getElementById(selectId);
                    
                    // Skip if the element doesn't exist
                    if (!select) return;
                    
                    // Save the currently selected value
                    const currentValue = select.value;
                    
                    // Clear existing options except first placeholder
                    while (select.options.length > 1) {
                        select.remove(1);
                    }
                    
                    // Add new options
                    availableObjects.forEach(objName => {
                        const option = document.createElement('option');
                        option.value = objName;
                        option.textContent = objName;
                        select.appendChild(option);
                    });
                    
                    // Restore the selected value if possible
                    if (currentValue) {
                        select.value = currentValue;
                    }
                });
                
                // Update the destination objects list
                updateDestinationObjectsList();
            }
        })
        .catch(error => {
            console.error('Error fetching available objects:', error);
        });
}

function updateDestinationObjectsList() {
    const container = document.getElementById('destination-objects-list');
    if (!container) return;
    
    // Clear current list
    container.innerHTML = '';
    
    // Add checkbox for each object
    availableObjects.forEach(objName => {
        const div = document.createElement('div');
        div.className = 'form-check';
        
        const input = document.createElement('input');
        input.className = 'form-check-input';
        input.type = 'checkbox';
        input.id = `dest-${objName}`;
        input.value = objName;
        input.checked = true;  // By default, check all objects
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `dest-${objName}`;
        label.textContent = objName;
        
        div.appendChild(input);
        div.appendChild(label);
        container.appendChild(div);
    });
}

// API Request Functions
function makeApiRequest(endpoint, method = 'POST', data = null) {
    showLoadingWithTimeout(30000); // Show loading with a 30-second timeout
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: data ? JSON.stringify(data) : null
    };
    
    if (method === 'GET' || !data) {
        delete options.body;
    }
    
    return fetch(endpoint, options)
        .then(response => response.json())
        .then(data => {
            hideLoading(); // Always hide loading on success
            
            if (data.status === 'error') {
                showStatus(`Error: ${data.message}`, true);
                throw new Error(data.message);
            }
            
            showStatus(data.message || 'Operation completed successfully');
            return data;
        })
        .catch(error => {
            hideLoading(); // Always hide loading on error
            showStatus(`Error: ${error.message}`, true);
            console.error('API request error:', error);
            throw error;
        });
}

// Simulation Control Functions
function initializeWorld() {
    makeApiRequest('/initialize_world')
        .then(() => {
            // After initializing, refresh available objects
            setTimeout(refreshObjectLists, 1000);
        });
}

function createObjects() {
    makeApiRequest('/create_objects')
        .then(() => {
            // After creating objects, refresh available objects
            setTimeout(refreshObjectLists, 1000);
        });
}

function addObjects() {
    makeApiRequest('/add_objects')
        .then(() => {
            // After adding objects, refresh available objects
            setTimeout(refreshObjectLists, 1000);
        });
}

function runRobotActions() {
    makeApiRequest('/run_robot_actions');
}

function exitWorld() {
    makeApiRequest('/exit_world');
}

// Camera Functions
function captureImage() {
    const targetDistance = document.getElementById('target-distance').value;
    const saveImage = document.getElementById('save-image').checked;
    const savePath = saveImage ? document.getElementById('save-path').value : null;
    
    // Show an initial message
    if (saveImage && savePath) {
        showStatus(`Capturing and saving image to ${savePath}...`);
    } else {
        showStatus('Capturing camera image...');
    }
    
    const data = {
        display: false,
        target_distance: parseFloat(targetDistance),
        save_path: savePath
    };
    
    makeApiRequest('/capture_camera_image', 'POST', data)
        .then(response => {
            // Display the image
            if (response.image) {
                displayImage(response.image.data);
            }
            
            // Show file path if saved successfully
            if (response.saved_to) {
                const saveInfoEl = document.createElement('div');
                saveInfoEl.className = 'alert alert-success mt-2';
                saveInfoEl.innerHTML = `<i class="fas fa-check-circle"></i> Saved to: ${response.saved_to}`;
                
                // Add below the image
                const imageContainer = document.querySelector('.image-container');
                
                // Remove any existing alert
                const existingAlert = imageContainer.querySelector('.alert');
                if (existingAlert) {
                    existingAlert.remove();
                }
                
                imageContainer.appendChild(saveInfoEl);
                
                // Auto-hide after 10 seconds
                setTimeout(() => {
                    saveInfoEl.remove();
                }, 10000);
            }
        });
}

function demoCamera() {
    makeApiRequest('/demo_camera')
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

function visualizeDepthMap() {
    const colormap = 'plasma'; // Default colormap
    
    makeApiRequest(`/visualize_depth_map?colormap=${colormap}`)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

function identifyObjects() {
    makeApiRequest('/identify_objects')
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
            refreshObjectLists(); // Refresh object lists
        });
}

function advancedCameraDemo() {
    makeApiRequest('/advanced_camera_demo')
        .then(response => {
            if (response.images && response.images.length > 0) {
                // Display the first image in the main viewer
                displayImage(response.images[0].data);
                
                // Create a gallery for all images
                createImageGallery(response.images);
            }
        });
}

function spawnObject() {
    const objectChoice = document.getElementById('object-choice').value;
    const finalObjectChoice = objectChoice === 'custom' 
        ? document.getElementById('custom-object').value
        : objectChoice;
    
    const coordX = parseFloat(document.getElementById('coord-x').value);
    const coordY = parseFloat(document.getElementById('coord-y').value);
    const coordZ = parseFloat(document.getElementById('coord-z').value);
    
    const color = document.getElementById('color').value;
    const objectName = document.getElementById('object-name').value.trim();
    
    const data = {
        object_choice: finalObjectChoice,
        coordinates: [coordX, coordY, coordZ],
        color: color || null,
        name: objectName || null
    };
    
    makeApiRequest('/spawn_object', 'POST', data)
        .then((response) => {
            // Display a more informative message about the spawned object
            if (response.name) {
                showStatus(`Object created: ${response.name} at coordinates [${coordX}, ${coordY}, ${coordZ}]`);
            }
            
            // After spawning an object, refresh object lists
            setTimeout(refreshObjectLists, 1000);
        });
}

function checkObjectVisibility() {
    const objectName = document.getElementById('visibility-object').value;
    const threshold = parseFloat(document.getElementById('visibility-threshold').value);
    
    if (!objectName) {
        showStatus('Please select an object', true);
        return;
    }
    
    const data = {
        object_name: objectName,
        threshold: threshold
    };
    
    makeApiRequest('/check_object_visibility', 'POST', data)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

function findOccludingObjects() {
    const objectName = document.getElementById('occluded-object').value;
    
    if (!objectName) {
        showStatus('Please select an object', true);
        return;
    }
    
    makeApiRequest(`/find_occluding_objects?object_name=${objectName}`)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

function lookAtObject() {
    const objectName = document.getElementById('look-at-object').value;
    
    if (!objectName) {
        showStatus('Please select an object', true);
        return;
    }
    
    const distance = parseFloat(document.getElementById('look-distance').value);
    const elevationAngle = parseFloat(document.getElementById('elevation-angle').value);
    const azimuthAngle = parseFloat(document.getElementById('azimuth-angle').value);
    
    const data = {
        object_name: objectName,
        distance: distance,
        elevation_angle: elevationAngle,
        azimuth_angle: azimuthAngle
    };
    
    makeApiRequest('/look_at_object', 'POST', data)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

function scanEnvironment() {
    const angles = parseInt(document.getElementById('scan-angles').value);
    
    const data = {
        angles: angles
    };
    
    makeApiRequest('/scan_environment', 'POST', data)
        .then(response => {
            if (response.images && response.images.length > 0) {
                // Display the first image in the main viewer
                displayImage(response.images[0].data);
                
                // Create a gallery for all scan images
                createImageGallery(response.images);
            }
        });
}

// Image Gallery Functions
function createImageGallery(images) {
    // Create gallery container if it doesn't exist
    let galleryContainer = document.querySelector('.image-gallery');
    if (!galleryContainer) {
        galleryContainer = document.createElement('div');
        galleryContainer.className = 'image-gallery';
        document.querySelector('.image-container').appendChild(galleryContainer);
    } else {
        // Clear existing images
        galleryContainer.innerHTML = '';
    }
    
    // Add each image to the gallery
    images.forEach((imageData, index) => {
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${imageData.data}`;
        img.className = 'gallery-image';
        img.alt = `Image ${index + 1}`;
        img.addEventListener('click', () => {
            // Display clicked image in the main viewer
            displayImage(imageData.data);
        });
        galleryContainer.appendChild(img);
    });
}

function calculateObjectDistances() {
    // Get source object (optional)
    const sourceObject = document.getElementById('source-object').value;
    
    // Get destination objects (if not using all)
    const useAllObjects = document.getElementById('use-all-objects').checked;
    let destinationObjects = [];
    
    if (!useAllObjects) {
        // Get checked destination objects
        const checkboxes = document.querySelectorAll('#destination-objects-list input[type="checkbox"]:checked');
        destinationObjects = Array.from(checkboxes).map(cb => cb.value);
    }
    
    // Get top N value
    const topN = parseInt(document.getElementById('top-n').value);
    
    const data = {
        source_object: sourceObject || null,
        destination_objects: destinationObjects.length > 0 ? destinationObjects : null,
        exclude_types: ["floor", "wall", "kitchen", "ground"],
        top_n: topN
    };
    
    showStatus('Calculating object distances...');
    
    makeApiRequest('/object_distances', 'POST', data)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
            
            // Display formatted distances in the status
            if (response.distances && response.distances.length > 0) {
                let distanceMessage = `Found ${response.distances.length} distance measurements:\n`;
                
                response.distances.forEach((item, index) => {
                    distanceMessage += `${index + 1}. ${item.object1} to ${item.object2}: ${item.distance.toFixed(3)} m\n`;
                });
                
                showStatus(distanceMessage);
            }
        });
}

// Add this function for 3D distance visualization
function visualize3DDistances() {
    const sourceObject = document.getElementById('source-object').value;
    const maxObjects = parseInt(document.getElementById('top-n').value);
    
    const data = {
        source_object: sourceObject || null,
        max_objects: maxObjects
    };
    
    showStatus('Generating 3D distance visualization...');
    
    makeApiRequest('/visualize_3d_distances', 'POST', data)
        .then(response => {
            if (response.image) {
                displayImage(response.image.data);
            }
        });
}

// Update toggle for "use all objects" checkbox
document.addEventListener('DOMContentLoaded', function() {
    // Other initialization code...
    
    // Add event listener for the "use all objects" checkbox
    const useAllObjectsCheckbox = document.getElementById('use-all-objects');
    if (useAllObjectsCheckbox) {
        useAllObjectsCheckbox.addEventListener('change', function() {
            const destList = document.getElementById('destination-objects-list');
            if (this.checked) {
                destList.classList.add('hidden');
            } else {
                destList.classList.remove('hidden');
                // Make sure the list is populated
                updateDestinationObjectsList();
            }
        });
    }
}); 