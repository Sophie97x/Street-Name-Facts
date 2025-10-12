// Global variables
let map;
let currentStreetInfo = null;
let streetMarkers = [];

// DOM elements
const locationSearchInput = document.getElementById("locationSearch");
const streetNameSearchInput = document.getElementById("streetNameSearch");
const searchLocationBtn = document.getElementById("searchLocationBtn");
const searchStreetBtn = document.getElementById("searchStreetBtn");
const streetInfo = document.getElementById("streetInfo");
const streetTitle = document.getElementById("streetTitle");
const streetSummary = document.getElementById("streetSummary");
const streetOrigin = document.getElementById("streetOrigin");
const moreInfoBtn = document.getElementById("moreInfoBtn");
const streetDetails = document.getElementById("streetDetails");
const streetFacts = document.getElementById("streetFacts");
const searchResults = document.getElementById("searchResults");
const resultsList = document.getElementById("resultsList");
const factText = document.getElementById("factText");
const newFactBtn = document.getElementById("newFactBtn");
const locateBtn = document.getElementById("locateBtn");
const fullscreenBtn = document.getElementById("fullscreenBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const helpBtn = document.getElementById("helpBtn");
const instructionsModal = document.getElementById("instructionsModal");

// Initialize the application
document.addEventListener("DOMContentLoaded", function() {
    console.log('DOM loaded, initializing application...');
    
    // Show loading initially
    showLoading(true);
    
    // Initialize components
    setupEventListeners();
    loadRandomFact();
    
    // Wait for Leaflet to be fully loaded before initializing map
    if (typeof L !== 'undefined') {
        console.log('Leaflet already loaded, initializing map immediately...');
        initializeMap();
    } else {
        console.log('Waiting for Leaflet to load...');
        // Check every 100ms for Leaflet to load
        const checkLeaflet = setInterval(() => {
            if (typeof L !== 'undefined') {
                console.log('Leaflet loaded, initializing map...');
                clearInterval(checkLeaflet);
                initializeMap();
            }
        }, 100);
        
        // Timeout after 5 seconds
        setTimeout(() => {
            if (typeof L === 'undefined') {
                clearInterval(checkLeaflet);
                console.error('Leaflet failed to load within 5 seconds');
                showMapError('Map library failed to load. Please refresh the page.');
            }
        }, 5000);
    }
    
    // Show instructions on first visit (but not immediately to avoid blocking map)
    if (!localStorage.getItem('hasVisited')) {
        setTimeout(() => {
            if (instructionsModal && typeof L !== 'undefined') {
                instructionsModal.style.display = "block";
                localStorage.setItem('hasVisited', 'true');
            }
        }, 3000);
    }
});

// Initialize Leaflet map
function initializeMap() {
    try {
        console.log('Initializing map...');
        
        // Check if Leaflet is loaded
        if (typeof L === 'undefined') {
            console.error('Leaflet library not loaded!');
            showMapError('Map library failed to load. Please check your internet connection.');
            return;
        }
        
        // Check if map container exists
        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.error('Map container not found!');
            showMapError('Map container element not found in HTML.');
            return;
        }
        
        console.log('Map container found, checking dimensions...');
        console.log('Initial container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
        
        // If container has zero height, wait a bit for CSS to apply
        if (mapContainer.offsetHeight === 0) {
            console.log('Container height is 0, waiting for layout...');
            setTimeout(() => {
                console.log('Retry - container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
                createMapInstance();
            }, 100);
        } else {
            createMapInstance();
        }
        
        function createMapInstance() {
            console.log('Creating map instance...');
            // Create map with London as default (like our test)
            map = L.map('map').setView([51.505, -0.09], 10);
            
            console.log('Map object created, adding tiles...');
            
            // Add OpenStreetMap tiles (same as working test)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(map);
            
            console.log('Tiles added, setting up events...');
            
            // Add a test marker to verify map is working
            L.marker([51.5, -0.09]).addTo(map)
                .bindPopup('Welcome to Street Names Explorer!<br>Search for a location to begin.')
                .openPopup();
            
            // Add click event to map
            map.on('click', onMapClick);
            
            // Add zoom event
            map.on('zoomend', onMapZoom);
            
            console.log('✅ Map initialized successfully!');
            
            // Hide loading overlay after map loads
            setTimeout(() => {
                showLoading(false);
            }, 500);
        }
        
    } catch (error) {
        console.error('❌ Error initializing map:', error);
        showMapError('Failed to initialize map: ' + error.message);
    }
}

// Show map error
function showMapError(message) {
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f8f9fa; color: #666; flex-direction: column; text-align: center; padding: 20px;">
                <div style="font-size: 48px; margin-bottom: 20px;">🗺️</div>
                <h3 style="margin: 0 0 10px 0; color: #333;">Map Loading Error</h3>
                <p style="margin: 0 0 20px 0; max-width: 400px;">${message}</p>
                <button onclick="location.reload()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;">Reload Page</button>
            </div>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Check if all required elements exist
    const elements = {
        searchLocationBtn, searchStreetBtn, moreInfoBtn, newFactBtn,
        locateBtn, fullscreenBtn, helpBtn, locationSearchInput, streetNameSearchInput
    };
    
    for (const [name, element] of Object.entries(elements)) {
        if (!element) {
            console.warn(`Element ${name} not found`);
        }
    }
    
    if (searchLocationBtn) searchLocationBtn.addEventListener('click', searchLocation);
    if (searchStreetBtn) searchStreetBtn.addEventListener('click', searchStreetNames);
    if (moreInfoBtn) moreInfoBtn.addEventListener('click', toggleMoreInfo);
    if (newFactBtn) newFactBtn.addEventListener('click', loadRandomFact);
    if (locateBtn) locateBtn.addEventListener('click', locateUser);
    if (fullscreenBtn) fullscreenBtn.addEventListener('click', toggleFullscreen);
    if (helpBtn) helpBtn.addEventListener('click', showInstructions);
    
    // Enter key support
    if (locationSearchInput) {
        locationSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchLocation();
        });
    }
    
    if (streetNameSearchInput) {
        streetNameSearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchStreetNames();
        });
    }
    
    // Modal close
    const closeBtn = document.querySelector('.close');
    if (closeBtn) closeBtn.addEventListener('click', hideInstructions);
    
    window.addEventListener('click', (e) => {
        if (e.target === instructionsModal) {
            hideInstructions();
        }
    });
    
    console.log('Event listeners set up successfully');
}

// Search for location
async function searchLocation() {
    const query = locationSearchInput.value.trim();
    if (!query) {
        showNotification("Please enter a location to search", "warning");
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/search-location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (data.success && data.location) {
            // Center map on location
            map.setView([data.location.latitude, data.location.longitude], 15);
            
            // Add marker
            const marker = L.marker([data.location.latitude, data.location.longitude])
                .addTo(map)
                .bindPopup(`<strong>${data.location.name}</strong>`)
                .openPopup();
            
            streetMarkers.push(marker);
            
            // Load nearby streets
            loadNearbyStreets(data.location.latitude, data.location.longitude);
            
            showNotification("Location found! Click on streets to learn about their names.", "success");
        } else {
            showNotification("Location not found. Try a different search term.", "error");
        }
    } catch (error) {
        console.error('Location search error:', error);
        showNotification("Error searching for location", "error");
    } finally {
        showLoading(false);
    }
}

// Search for street names
async function searchStreetNames() {
    const query = streetNameSearchInput.value.trim();
    if (!query) {
        showNotification("Please enter a street name to search", "warning");
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`/api/search-streets?q=${encodeURIComponent(query)}&limit=10`);
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            displaySearchResults(data.results);
            showNotification(`Found ${data.results.length} street name(s)`, "success");
        } else {
            searchResults.classList.add('hidden');
            showNotification("No streets found with that name", "info");
        }
    } catch (error) {
        console.error('Street search error:', error);
        showNotification("Error searching for street names", "error");
    } finally {
        showLoading(false);
    }
}

// Display search results
function displaySearchResults(results) {
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="result-name">${result.name}</div>
            <div class="result-summary">${result.summary}</div>
        `;
        li.addEventListener('click', () => {
            getStreetInfo(result.name);
            streetNameSearchInput.value = result.name;
        });
        resultsList.appendChild(li);
    });
    
    searchResults.classList.remove('hidden');
}

// Get detailed street information
async function getStreetInfo(streetName, city = '', country = '') {
    showLoading(true);
    
    try {
        const response = await fetch('/api/street-info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                street_name: streetName,
                city: city,
                country: country
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.street_info) {
            displayStreetInfo(data.street_info);
            showNotification("Street information loaded!", "success");
        } else {
            showNotification("No information found for this street", "info");
        }
    } catch (error) {
        console.error('Street info error:', error);
        showNotification("Error loading street information", "error");
    } finally {
        showLoading(false);
    }
}

// Display street information
function displayStreetInfo(info) {
    currentStreetInfo = info;
    
    streetTitle.textContent = info.search_term || "Street Information";
    streetSummary.textContent = info.summary;
    streetOrigin.textContent = info.origin;
    
    // Display facts
    if (info.facts && info.facts.length > 0) {
        streetFacts.innerHTML = '';
        info.facts.forEach(fact => {
            const factDiv = document.createElement('div');
            factDiv.className = 'fact-item';
            factDiv.innerHTML = `
                <div class="fact-year">${fact.year}</div>
                <div class="fact-text">${fact.fact}</div>
            `;
            streetFacts.appendChild(factDiv);
        });
        moreInfoBtn.style.display = 'block';
    } else {
        moreInfoBtn.style.display = 'none';
    }
    
    streetInfo.classList.remove('hidden');
    streetDetails.classList.add('hidden');
    moreInfoBtn.innerHTML = 'More Details <i class="fas fa-chevron-down"></i>';
    
    // Hide search results
    searchResults.classList.add('hidden');
}

// Toggle more information
function toggleMoreInfo() {
    if (streetDetails.classList.contains('hidden')) {
        streetDetails.classList.remove('hidden');
        moreInfoBtn.innerHTML = 'Less Details <i class="fas fa-chevron-up"></i>';
    } else {
        streetDetails.classList.add('hidden');
        moreInfoBtn.innerHTML = 'More Details <i class="fas fa-chevron-down"></i>';
    }
}

// Load nearby streets
async function loadNearbyStreets(lat, lon) {
    try {
        const response = await fetch('/api/nearby-streets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                latitude: lat,
                longitude: lon,
                radius: 1000
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.streets) {
            displayNearbyStreets(data.streets);
        }
    } catch (error) {
        console.error('Error loading nearby streets:', error);
    }
}

// Display nearby streets on map
function displayNearbyStreets(streets) {
    // Clear existing street markers
    streetMarkers.forEach(marker => {
        if (marker.options.isStreet) {
            map.removeLayer(marker);
        }
    });
    
    streets.forEach(street => {
        if (street.coordinates && street.coordinates.length > 0) {
            // Create polyline for street
            const polyline = L.polyline(street.coordinates, {
                color: '#667eea',
                weight: 3,
                opacity: 0.7
            }).addTo(map);
            
            // Add click event to polyline
            polyline.on('click', () => {
                showStreetPopup(street, polyline);
            });
            
            polyline.options.isStreet = true;
            streetMarkers.push(polyline);
        }
    });
}

// Show street popup
function showStreetPopup(street, polyline) {
    const popupContent = `
        <div class="street-popup">
            <h4>${street.name}</h4>
            <p><strong>Type:</strong> ${street.type}</p>
            <button onclick="getStreetInfo('${street.name}')">Learn More</button>
        </div>
    `;
    
    // Get center of polyline for popup
    const bounds = polyline.getBounds();
    const center = bounds.getCenter();
    
    L.popup()
        .setLatLng(center)
        .setContent(popupContent)
        .openOn(map);
}

// Map click handler
function onMapClick(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    
    // Load nearby streets when clicking on map
    loadNearbyStreets(lat, lon);
}

// Map zoom handler
function onMapZoom() {
    const zoom = map.getZoom();
    
    // Adjust street line weight based on zoom level
    streetMarkers.forEach(marker => {
        if (marker.options && marker.options.isStreet && marker.setStyle) {
            const weight = Math.max(1, Math.min(5, zoom - 10));
            marker.setStyle({ weight: weight });
        }
    });
}

// Load random street fact
async function loadRandomFact() {
    const facts = [
        "Broadway in New York City was originally a Native American trail called the Wickquasgeck Trail.",
        "Wall Street got its name from a wooden wall built by Dutch colonists in 1653 to defend New Amsterdam.",
        "Main Street is the most common street name in the United States, found in thousands of cities.",
        "Lombard Street in San Francisco is known as the 'most crooked street in the world' with eight hairpin turns.",
        "Fleet Street in London was historically the center of the British press and newspaper industry.",
        "The Champs-Élysées in Paris was originally fields until 1667 when it was transformed into a tree-lined avenue.",
        "Route 66, known as the 'Mother Road,' connected Chicago to Los Angeles and became an icon of American culture.",
        "Abbey Road in London became famous worldwide after The Beatles recorded their album there in 1969."
    ];
    
    const randomFact = facts[Math.floor(Math.random() * facts.length)];
    factText.textContent = randomFact;
}

// Locate user
function locateUser() {
    if (!navigator.geolocation) {
        showNotification("Geolocation is not supported by this browser", "error");
        return;
    }
    
    showLoading(true);
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            map.setView([lat, lon], 15);
            
            const marker = L.marker([lat, lon])
                .addTo(map)
                .bindPopup("Your location")
                .openPopup();
            
            streetMarkers.push(marker);
            loadNearbyStreets(lat, lon);
            
            showNotification("Location found!", "success");
            showLoading(false);
        },
        (error) => {
            showNotification("Unable to get your location: " + error.message, "error");
            showLoading(false);
        }
    );
}

// Toggle fullscreen
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
        fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
    } else {
        document.exitFullscreen();
        fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
    }
}

// Show/hide instructions
function showInstructions() {
    instructionsModal.style.display = "block";
}

function hideInstructions() {
    instructionsModal.style.display = "none";
}

// Show/hide loading overlay
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

// Show notifications
function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    Object.assign(notification.style, {
        position: "fixed",
        top: "20px",
        right: "20px",
        padding: "12px 20px",
        borderRadius: "8px",
        color: "white",
        fontWeight: "500",
        zIndex: "4000",
        maxWidth: "300px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
    });
    
    const colors = {
        success: "#28a745",
        error: "#dc3545",
        warning: "#ffc107",
        info: "#17a2b8"
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 4000);
}