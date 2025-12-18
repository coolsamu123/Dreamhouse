/**
 * Dreamhouse - Frontend Application
 * Real estate listing viewer for Brussels apartments
 */

// State
let allListings = [];
let filteredListings = [];
let map = null;
let markers = [];
let statusData = null;

// DOM Elements
const listingsContainer = document.getElementById('listings-container');
const loadingEl = document.getElementById('loading');
const noResultsEl = document.getElementById('no-results');
const lastUpdatedEl = document.getElementById('last-updated');
const listingCountEl = document.getElementById('listing-count');
const mapContainer = document.getElementById('map-container');

// Filters
const filterCommune = document.getElementById('filter-commune');
const filterPrice = document.getElementById('filter-price');
const filterBedrooms = document.getElementById('filter-bedrooms');
const filterSurface = document.getElementById('filter-surface');

// Theme toggle
function initTheme() {
    const isDark = localStorage.getItem('theme') === 'dark' ||
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);

    if (isDark) {
        document.documentElement.classList.add('dark');
    }
}

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
}

// Format price
function formatPrice(price) {
    if (!price) return 'Prix non disponible';
    const num = typeof price === 'string' ? parseFloat(price.replace(/[^\d]/g, '')) : price;
    return new Intl.NumberFormat('fr-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
        .format(num);
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-BE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

// Check if listing is new (within last 24 hours)
function isNew(listing) {
    if (listing.is_new) return true;
    if (!listing.first_seen) return false;
    const firstSeen = new Date(listing.first_seen);
    const now = new Date();
    const diffHours = (now - firstSeen) / (1000 * 60 * 60);
    return diffHours < 24;
}

// Create listing card HTML
function createListingCard(listing) {
    const isNewListing = isNew(listing);
    const imageUrl = listing.images && listing.images.length > 0 ? listing.images[0] : null;

    return `
        <article class="listing-card" data-id="${listing.id}">
            <div class="listing-image-container">
                ${isNewListing ? '<span class="badge-new">NEW</span>' : ''}
                ${imageUrl
            ? `<img src="${imageUrl}" alt="${listing.title || 'Appartement'}" class="listing-image" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'placeholder-image\\'>🏠</div>'">`
            : '<div class="placeholder-image">🏠</div>'
        }
            </div>
            <div class="p-4">
                <div class="flex justify-between items-start mb-2">
                    <h2 class="listing-price">${formatPrice(listing.price)}</h2>
                    <span class="source-badge">${listing.source || 'Unknown'}</span>
                </div>

                <h3 class="font-semibold text-gray-800 dark:text-white mb-1 truncate">
                    ${listing.title || 'Appartement à louer'}
                </h3>

                <p class="listing-address mb-3">
                    📍 ${listing.address || listing.commune || 'Bruxelles'}
                </p>

                <div class="listing-details mb-4">
                    ${listing.bedrooms ? `<span class="listing-detail">🛏️ ${listing.bedrooms} ch.</span>` : ''}
                    ${listing.surface ? `<span class="listing-detail">📐 ${listing.surface} m²</span>` : ''}
                    <span class="listing-detail">📍 ${listing.commune || 'Bruxelles'}</span>
                </div>

                <div class="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400 mb-3">
                    <span>Vu le ${formatDate(listing.first_seen)}</span>
                </div>

                <a href="${listing.source_url}" target="_blank" rel="noopener noreferrer" class="btn-view">
                    Voir l'annonce →
                </a>
            </div>
        </article>
    `;
}

// Apply filters
function applyFilters() {
    const commune = filterCommune.value.toLowerCase();
    const priceRange = filterPrice.value;
    const bedrooms = filterBedrooms.value;
    const surfaceRange = filterSurface.value;

    filteredListings = allListings.filter(listing => {
        // Commune filter
        if (commune && !listing.commune?.toLowerCase().includes(commune)) {
            return false;
        }

        // Price filter
        if (priceRange) {
            const [min, max] = priceRange.split('-').map(Number);
            const price = typeof listing.price === 'string'
                ? parseFloat(listing.price.replace(/[^\d]/g, ''))
                : listing.price;
            if (!price || price < min || price > max) {
                return false;
            }
        }

        // Bedrooms filter
        if (bedrooms) {
            const bedroomCount = parseInt(listing.bedrooms);
            if (bedrooms === '3') {
                if (!bedroomCount || bedroomCount < 3) return false;
            } else {
                if (bedroomCount !== parseInt(bedrooms)) return false;
            }
        }

        // Surface filter
        if (surfaceRange) {
            const [min, max] = surfaceRange.split('-').map(Number);
            const surface = typeof listing.surface === 'string'
                ? parseFloat(listing.surface.replace(/[^\d]/g, ''))
                : listing.surface;
            if (!surface || surface < min || surface > max) {
                return false;
            }
        }

        return true;
    });

    renderListings();
    updateMap();
}

// Reset filters
function resetFilters() {
    filterCommune.value = '';
    filterPrice.value = '';
    filterBedrooms.value = '';
    filterSurface.value = '';
    applyFilters();
}

// Render listings
function renderListings() {
    loadingEl.classList.add('hidden');

    if (filteredListings.length === 0) {
        listingsContainer.innerHTML = '';
        noResultsEl.classList.remove('hidden');
        return;
    }

    noResultsEl.classList.add('hidden');

    // Sort by first_seen (newest first)
    const sorted = [...filteredListings].sort((a, b) => {
        const dateA = new Date(a.first_seen || 0);
        const dateB = new Date(b.first_seen || 0);
        return dateB - dateA;
    });

    listingsContainer.innerHTML = sorted.map(createListingCard).join('');
    listingCountEl.textContent = `${filteredListings.length} annonce${filteredListings.length > 1 ? 's' : ''}`;
}

// Initialize map
function initMap() {
    if (map) return;

    // Center on Brussels
    map = L.map('map').setView([50.8476, 4.3572], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}

// Update map markers
function updateMap() {
    if (!map) return;

    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Brussels commune coordinates (approximate)
    const communeCoords = {
        'saint-gilles': [50.8279, 4.3468],
        'forest': [50.8103, 4.3199],
        'ixelles': [50.8253, 4.3749],
    };

    filteredListings.forEach(listing => {
        const commune = listing.commune?.toLowerCase() || '';
        let coords = null;

        for (const [key, value] of Object.entries(communeCoords)) {
            if (commune.includes(key)) {
                // Add some random offset for visual separation
                coords = [
                    value[0] + (Math.random() - 0.5) * 0.01,
                    value[1] + (Math.random() - 0.5) * 0.01
                ];
                break;
            }
        }

        if (coords) {
            const marker = L.marker(coords)
                .addTo(map)
                .bindPopup(`
                    <div class="p-2">
                        <strong>${formatPrice(listing.price)}</strong><br>
                        ${listing.title || 'Appartement'}<br>
                        <a href="${listing.source_url}" target="_blank" class="text-blue-500">Voir →</a>
                    </div>
                `);
            markers.push(marker);
        }
    });
}

// Toggle views
function showListView() {
    mapContainer.classList.add('hidden');
    listingsContainer.classList.remove('hidden');
    document.getElementById('view-list').classList.add('active');
    document.getElementById('view-map').classList.remove('active');
}

function showMapView() {
    listingsContainer.classList.add('hidden');
    mapContainer.classList.remove('hidden');
    document.getElementById('view-map').classList.add('active');
    document.getElementById('view-list').classList.remove('active');

    initMap();
    setTimeout(() => map.invalidateSize(), 100);
    updateMap();
}

// Load listings data
async function loadListings() {
    try {
        const response = await fetch('listings.json');
        if (!response.ok) throw new Error('Failed to load listings');

        const data = await response.json();

        allListings = data.listings || [];
        filteredListings = allListings;
        statusData = data; // Store for status modal

        // Update UI
        if (data.last_updated) {
            lastUpdatedEl.textContent = `Mis à jour: ${formatDate(data.last_updated)}`;
        }

        renderListings();
        checkApiStatus(); // Update header status indicator

    } catch (error) {
        console.error('Error loading listings:', error);
        loadingEl.innerHTML = `
            <p class="text-red-500">Erreur de chargement des annonces</p>
            <p class="text-sm text-gray-500 mt-2">${error.message}</p>
            <button onclick="location.reload()" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">
                Réessayer
            </button>
        `;
    }
}

// Status Modal
function openStatusModal() {
    const modal = document.getElementById('status-modal');
    modal.classList.remove('hidden');
    updateStatusModal();
}

function closeStatusModal() {
    const modal = document.getElementById('status-modal');
    modal.classList.add('hidden');
}

function updateStatusModal() {
    // Update stats
    document.getElementById('stat-listings').textContent = allListings.length || '-';

    // Count new listings (last 24h)
    const newCount = allListings.filter(l => isNew(l)).length;
    document.getElementById('stat-new').textContent = newCount || '0';

    // Last update time
    if (statusData?.last_updated) {
        const date = new Date(statusData.last_updated);
        const hours = Math.floor((Date.now() - date) / (1000 * 60 * 60));
        document.getElementById('stat-updated').textContent = hours < 1 ? '<1h' : `${hours}h`;
    }

    // Check API status based on data
    checkApiStatus();
}

function checkApiStatus() {
    const apiIndicator = document.getElementById('api-indicator');
    const apiText = document.getElementById('api-text');
    const statusIndicator = document.getElementById('status-indicator');

    // Determine status based on listings data
    if (allListings.length > 0) {
        // Check if data is fresh (updated in last 4 hours)
        const lastUpdate = new Date(statusData?.last_updated || 0);
        const hoursSince = (Date.now() - lastUpdate) / (1000 * 60 * 60);

        if (hoursSince < 4) {
            apiIndicator.className = 'w-3 h-3 rounded-full bg-green-500';
            statusIndicator.className = 'w-2 h-2 rounded-full bg-green-500';
            apiText.textContent = `✓ Actif - ${allListings.length} annonces récupérées`;
        } else if (hoursSince < 24) {
            apiIndicator.className = 'w-3 h-3 rounded-full bg-yellow-500';
            statusIndicator.className = 'w-2 h-2 rounded-full bg-yellow-500';
            apiText.textContent = `⚠ Dernière MAJ il y a ${Math.floor(hoursSince)}h`;
        } else {
            apiIndicator.className = 'w-3 h-3 rounded-full bg-red-500';
            statusIndicator.className = 'w-2 h-2 rounded-full bg-red-500';
            apiText.textContent = `✗ Pas de MAJ depuis ${Math.floor(hoursSince)}h`;
        }
    } else {
        apiIndicator.className = 'w-3 h-3 rounded-full bg-yellow-500';
        statusIndicator.className = 'w-2 h-2 rounded-full bg-yellow-500';
        apiText.textContent = '⚠ Aucune donnée - lancez le scraping';
    }
}

async function testApiConnection() {
    const apiIndicator = document.getElementById('api-indicator');
    const apiText = document.getElementById('api-text');
    const btn = document.getElementById('btn-test-api');

    btn.disabled = true;
    btn.textContent = '⏳ Test...';
    apiIndicator.className = 'w-3 h-3 rounded-full bg-yellow-500 animate-pulse';
    apiText.textContent = 'Test de connexion en cours...';

    // Simulate API check by reloading data
    try {
        const response = await fetch('listings.json?t=' + Date.now());
        if (response.ok) {
            const data = await response.json();
            if (data.listings && data.listings.length > 0) {
                apiIndicator.className = 'w-3 h-3 rounded-full bg-green-500';
                apiText.textContent = `✓ Données OK - ${data.listings.length} annonces`;
            } else {
                apiIndicator.className = 'w-3 h-3 rounded-full bg-yellow-500';
                apiText.textContent = '⚠ JSON OK mais pas d\'annonces';
            }
        } else {
            throw new Error('HTTP ' + response.status);
        }
    } catch (error) {
        apiIndicator.className = 'w-3 h-3 rounded-full bg-red-500';
        apiText.textContent = '✗ Erreur: ' + error.message;
    }

    btn.disabled = false;
    btn.textContent = '🔄 Test API';
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadListings();

    // Theme toggles
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
    document.getElementById('theme-toggle-desktop')?.addEventListener('click', toggleTheme);

    // Filters
    filterCommune.addEventListener('change', applyFilters);
    filterPrice.addEventListener('change', applyFilters);
    filterBedrooms.addEventListener('change', applyFilters);
    filterSurface.addEventListener('change', applyFilters);

    // Reset buttons
    document.getElementById('btn-reset-filters')?.addEventListener('click', resetFilters);
    document.getElementById('btn-reset-filters-2')?.addEventListener('click', resetFilters);

    // View toggles
    document.getElementById('view-list')?.addEventListener('click', showListView);
    document.getElementById('view-map')?.addEventListener('click', showMapView);

    // Status modal
    document.getElementById('btn-status')?.addEventListener('click', openStatusModal);
    document.getElementById('close-modal')?.addEventListener('click', closeStatusModal);
    document.getElementById('btn-test-api')?.addEventListener('click', testApiConnection);

    // Close modal on backdrop click
    document.getElementById('status-modal')?.addEventListener('click', (e) => {
        if (e.target.id === 'status-modal') closeStatusModal();
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeStatusModal();
    });
});
