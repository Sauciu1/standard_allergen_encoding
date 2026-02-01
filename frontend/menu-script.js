// ==========================================
// Menu Scanner - Main Script
// ==========================================

// Initialize Lucide icons
lucide.createIcons();

// API Configuration - use current host to work with both localhost and 127.0.0.1
const API_BASE_URL = `http://${window.location.hostname}:5000/api`;

// DOM Elements
const inputView = document.getElementById('inputView');
const resultsView = document.getElementById('resultsView');
const userCodeInput = document.getElementById('userCodeInput');
const analyzeMenuBtn = document.getElementById('analyzeMenuBtn');
const resetMenuBtn = document.getElementById('resetMenuBtn');
const menuListContainer = document.getElementById('menuListContainer');
const activeAllergensList = document.getElementById('activeAllergensList');
const safeCountEl = document.getElementById('safeCount');
const avoidCountEl = document.getElementById('avoidCount');

// State
let currentResults = null;
let userAllergenPhrases = [];
let decodedAllergens = [];

// Enable/disable analyze button based on input
if (userCodeInput && analyzeMenuBtn) {
    userCodeInput.addEventListener('input', () => {
        const hasInput = userCodeInput.value.trim().length > 0;
        analyzeMenuBtn.disabled = !hasInput;
    });

    // Analyze menu button click
    analyzeMenuBtn.addEventListener('click', async () => {
        const userCode = userCodeInput.value.trim();
        
        if (!userCode) {
            showError('Please enter your allergen code');
            return;
        }
        
        // Parse allergen code (split by dots or spaces)
        const allergenPhrases = userCode.split(/[.\s,]+/).filter(word => word.length > 0);
        
        if (allergenPhrases.length === 0) {
            showError('Invalid allergen code format');
            return;
        }
        
        await analyzeMenu(allergenPhrases);
    });
}

// Reset button click
if (resetMenuBtn) {
    resetMenuBtn.addEventListener('click', () => {
        inputView.classList.remove('hidden');
        resultsView.classList.add('hidden');
        userCodeInput.value = '';
        analyzeMenuBtn.disabled = true;
        currentResults = null;
        userAllergenPhrases = [];
        decodedAllergens = [];  // Reset decoded allergens
    });
}

// Analyze menu function
async function analyzeMenu(allergenPhrases) {
    try {
        // Show loading state
        analyzeMenuBtn.disabled = true;
        analyzeMenuBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-5 w-5 animate-spin"></i> Analyzing...';
        lucide.createIcons();
        
        console.log('Sending request to API with phrases:', allergenPhrases);
        
        // Call API
        const response = await fetch(`${API_BASE_URL}/analyze-menu`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                allergen_phrases: allergenPhrases
            })
        });
        
        console.log('Response status:', response.status);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            throw new Error('Server returned non-JSON response. Make sure Flask API is running: flask --app flaskr run --debug');
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to analyze menu');
        }
        
        // Store results
        currentResults = data.results;
        userAllergenPhrases = data.user_allergen_phrases;
        decodedAllergens = data.user_allergens || [];  // Store decoded allergens
        
        // Display results
        displayResults(data);
        
        // Switch views
        inputView.classList.add('hidden');
        resultsView.classList.remove('hidden');
        
    } catch (error) {
        console.error('Error analyzing menu:', error);
        showError(error.message || 'Failed to analyze menu. Please check console for details.');
    } finally {
        // Reset button state
        analyzeMenuBtn.disabled = false;
        analyzeMenuBtn.innerHTML = '<i data-lucide="search" class="mr-2 h-5 w-5"></i> Analyze Menu';
        lucide.createIcons();
    }
}

// Display results function
function displayResults(data) {
    // Update stats
    safeCountEl.textContent = data.stats.safe;
    avoidCountEl.textContent = data.stats.avoid;
    
    // Display decoded allergens (not the encoded phrases)
    const allergensToDisplay = data.user_allergens && data.user_allergens.length > 0 
        ? data.user_allergens 
        : data.user_allergen_phrases;
    
    activeAllergensList.innerHTML = allergensToDisplay.map(allergen => `
        <span class="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
            ${escapeHtml(capitalizeFirst(allergen))}
        </span>
    `).join('');
    
    // Display menu items
    menuListContainer.innerHTML = data.results.map(item => {
        const isSafe = item.allowed;
        const bgColor = isSafe ? 'bg-green-50' : 'bg-red-50';
        const borderColor = isSafe ? 'border-green-200' : 'border-red-200';
        const iconColor = isSafe ? 'text-green-600' : 'text-red-600';
        const icon = isSafe ? 'check-circle' : 'alert-triangle';
        const statusText = isSafe ? 'SAFE' : 'AVOID';
        const statusColor = isSafe ? 'text-green-700' : 'text-red-700';
        
        return `
            <div class="p-4 rounded-xl border ${borderColor} ${bgColor}">
                <div class="flex items-start gap-4">
                    <i data-lucide="${icon}" class="h-6 w-6 ${iconColor} flex-shrink-0 mt-0.5"></i>
                    <div class="flex-1">
                        <div class="flex items-start justify-between gap-4 mb-2">
                            <h3 class="font-semibold text-gray-900">${escapeHtml(item.meal)}</h3>
                            <span class="px-2 py-1 rounded text-xs font-bold ${statusColor} whitespace-nowrap">
                                ${statusText}
                            </span>
                        </div>
                        <p class="text-sm text-gray-600 mb-2">${escapeHtml(item.reason)}</p>
                        ${item.item_allergens && item.item_allergens.length > 0 ? `
                            <div class="flex flex-wrap gap-1 mt-2">
                                <span class="text-xs text-gray-500">Contains:</span>
                                ${item.item_allergens.map(allergen => {
                                    const isMatched = item.matched_allergens && item.matched_allergens.includes(allergen);
                                    const allergenBg = isMatched ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600';
                                    return `<span class="px-2 py-0.5 rounded text-xs ${allergenBg}">${escapeHtml(allergen)}</span>`;
                                }).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Reinitialize Lucide icons
    lucide.createIcons();
}

// Helper function to capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Show error message
function showError(message) {
    // Create a temporary error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg bg-red-50 border border-red-200 shadow-lg max-w-md';
    errorDiv.innerHTML = `
        <div class="flex items-center gap-3">
            <i data-lucide="alert-circle" class="h-5 w-5 text-red-600 flex-shrink-0"></i>
            <p class="text-sm text-red-700">${escapeHtml(message)}</p>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    lucide.createIcons();
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check API health on page load
async function checkAPIHealth() {
    try {
        const response = await fetch(`http://${window.location.hostname}:5000/health`);
        if (!response.ok) {
            throw new Error('API not responding');
        }
        console.log('✅ API connection successful');
    } catch (error) {
        console.error('❌ API connection failed:', error);
        showError('Cannot connect to server. Please start the Flask API: flask --app flaskr run --debug');
    }
}

// Check API health when page loads
window.addEventListener('load', () => {
    checkAPIHealth();
});
