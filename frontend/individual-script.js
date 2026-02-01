// Initialize Lucide icons
lucide.createIcons();

// API Configuration
const API_BASE_URL = `http://${window.location.hostname}:5000/api`;

// State
let availableAllergens = [];
let selectedAllergens = new Set();
let generatedCode = '';

// DOM Elements - Tabs
const tabEncode = document.getElementById('tabEncode');
const tabDecode = document.getElementById('tabDecode');
const encodeSection = document.getElementById('encodeSection');
const decodeSection = document.getElementById('decodeSection');

// DOM Elements - Encode
const allergenOptions = document.getElementById('allergenOptions');
const allergenCount = document.getElementById('allergenCount');
const selectedTagsContainer = document.getElementById('selectedTagsContainer');
const dropdownBtn = document.getElementById('dropdownBtn');
const dropdownMenu = document.getElementById('dropdownMenu');
const dropdownPlaceholder = document.getElementById('dropdownPlaceholder');
const allergenSearch = document.getElementById('allergenSearch');
const generateBtn = document.getElementById('generateBtn');
const encodeResult = document.getElementById('encodeResult');
const generatedCodeText = document.getElementById('generatedCodeText');
const copyBtn = document.getElementById('copyBtn');
const resetBtn = document.getElementById('resetBtn');

// DOM Elements - Decode
const decodeInput = document.getElementById('decodeInput');
const decodeBtn = document.getElementById('decodeBtn');
const decodeResult = document.getElementById('decodeResult');
const decodedAllergensList = document.getElementById('decodedAllergensList');

// Tab Switching
if (tabEncode && tabDecode && encodeSection && decodeSection) {
    tabEncode.addEventListener('click', () => {
        // Switch to encode tab
        tabEncode.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        tabEncode.classList.remove('text-gray-500');
        tabDecode.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        tabDecode.classList.add('text-gray-500');
        
        encodeSection.classList.remove('hidden');
        decodeSection.classList.add('hidden');
    });
    
    tabDecode.addEventListener('click', () => {
        // Switch to decode tab
        tabDecode.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        tabDecode.classList.remove('text-gray-500');
        tabEncode.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        tabEncode.classList.add('text-gray-500');
        
        decodeSection.classList.remove('hidden');
        encodeSection.classList.add('hidden');
        
        lucide.createIcons(); // Refresh icons
    });
}

// Load available allergens on page load
async function loadAllergens() {
    try {
        console.log('Loading allergens from API...');
        const response = await fetch(`${API_BASE_URL}/allergens`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Allergens loaded:', data);
        
        if (data.allergens && Array.isArray(data.allergens)) {
            availableAllergens = data.allergens;
            renderAllergenOptions();
        } else {
            throw new Error('Invalid allergens data format');
        }
    } catch (error) {
        console.error('Error loading allergens:', error);
        showError('Failed to load allergens. Please refresh the page.');
    }
}

// Render allergen dropdown options
function renderAllergenOptions(searchTerm = '') {
    if (!allergenOptions) {
        console.error('allergenOptions element not found');
        return;
    }
    
    // Filter allergens based on search term
    const filteredAllergens = searchTerm
        ? availableAllergens.filter(allergen => 
            allergen.toLowerCase().includes(searchTerm.toLowerCase())
          )
        : availableAllergens;
    
    if (filteredAllergens.length === 0) {
        allergenOptions.innerHTML = `
            <div class="px-4 py-3 text-center text-sm text-gray-500">
                No allergens found matching "${escapeHtml(searchTerm)}"
            </div>
        `;
        return;
    }
    
    allergenOptions.innerHTML = filteredAllergens.map(allergen => {
        const isSelected = selectedAllergens.has(allergen);
        const safeAllergen = allergen.replace(/'/g, "\\'");
        return `
            <div class="px-2 py-1">
                <label class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <input 
                        type="checkbox" 
                        value="${escapeHtml(allergen)}"
                        ${isSelected ? 'checked' : ''}
                        class="rounded border-gray-300 text-green-600 focus:ring-green-500 allergen-checkbox"
                        data-allergen="${escapeHtml(allergen)}"
                    >
                    <span class="text-sm text-gray-700">${escapeHtml(capitalizeFirst(allergen))}</span>
                </label>
            </div>
        `;
    }).join('');
    
    // Add event listeners to checkboxes
    document.querySelectorAll('.allergen-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const allergen = e.target.dataset.allergen;
            toggleAllergen(allergen);
        });
    });
}

// Toggle allergen selection
function toggleAllergen(allergen) {
    if (selectedAllergens.has(allergen)) {
        selectedAllergens.delete(allergen);
    } else {
        selectedAllergens.add(allergen);
    }
    
    updateSelectedDisplay();
    renderAllergenOptions(); // Re-render to update checkboxes
}

// Update selected allergens display
function updateSelectedDisplay() {
    const count = selectedAllergens.size;
    
    if (allergenCount) {
        allergenCount.textContent = `${count} selected`;
    }
    
    if (count === 0) {
        if (dropdownPlaceholder) {
            dropdownPlaceholder.textContent = 'Click to select allergens...';
            dropdownPlaceholder.classList.add('text-gray-500');
            dropdownPlaceholder.classList.remove('text-gray-900');
        }
        if (selectedTagsContainer) {
            selectedTagsContainer.classList.add('hidden');
        }
        if (generateBtn) {
            generateBtn.disabled = true;
        }
    } else {
        if (dropdownPlaceholder) {
            dropdownPlaceholder.textContent = `${count} allergen${count > 1 ? 's' : ''} selected`;
            dropdownPlaceholder.classList.remove('text-gray-500');
            dropdownPlaceholder.classList.add('text-gray-900');
        }
        
        if (selectedTagsContainer) {
            selectedTagsContainer.classList.remove('hidden');
            selectedTagsContainer.innerHTML = Array.from(selectedAllergens).map(allergen => {
                const safeAllergen = allergen.replace(/'/g, "\\'");
                return `
                    <span class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-green-100 text-green-700 text-xs font-medium">
                        ${escapeHtml(capitalizeFirst(allergen))}
                        <button onclick="window.toggleAllergenFromTag('${safeAllergen}')" class="hover:text-green-900" type="button">
                            <i data-lucide="x" class="h-3 w-3"></i>
                        </button>
                    </span>
                `;
            }).join('');
            lucide.createIcons();
        }
        
        if (generateBtn) {
            generateBtn.disabled = false;
        }
    }
}

// Toggle dropdown menu
if (dropdownBtn && dropdownMenu) {
    dropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle('hidden');
        
        // Focus search input when dropdown opens
        if (!dropdownMenu.classList.contains('hidden') && allergenSearch) {
            setTimeout(() => allergenSearch.focus(), 100);
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (dropdownMenu && !dropdownMenu.contains(e.target) && !dropdownBtn.contains(e.target)) {
            dropdownMenu.classList.add('hidden');
            // Clear search when closing
            if (allergenSearch) {
                allergenSearch.value = '';
                renderAllergenOptions();
            }
        }
    });
}

// Search functionality
if (allergenSearch) {
    allergenSearch.addEventListener('input', (e) => {
        const searchTerm = e.target.value.trim();
        renderAllergenOptions(searchTerm);
    });
    
    // Prevent dropdown from closing when clicking search input
    allergenSearch.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// Generate allergen code
if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
        if (selectedAllergens.size === 0) {
            showError('Please select at least one allergen');
            return;
        }
        
        try {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-5 w-5 animate-spin inline"></i> Generating...';
            lucide.createIcons();
            
            const allergensList = Array.from(selectedAllergens);
            
            console.log('Encoding allergens:', allergensList);
            
            const response = await fetch(`${API_BASE_URL}/encode`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    allergens: allergensList
                })
            });
            
            const data = await response.json();
            console.log('Encode response:', data);
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Failed to generate code');
            }
            
            generatedCode = data.code;
            generatedCodeText.textContent = generatedCode;
            encodeResult.classList.remove('hidden');
            
            // Generate QR code if canvas exists
            const qrCanvas = document.getElementById('qrCodeCanvas');
            if (qrCanvas && typeof QRCode !== 'undefined') {
                QRCode.toCanvas(qrCanvas, generatedCode, { width: 200 }, (error) => {
                    if (error) console.error('QR generation error:', error);
                });
            }
            
            console.log('Generated code:', {
                allergens: allergensList,
                words: data.words,
                code: data.code
            });
            
        } catch (error) {
            console.error('Error generating code:', error);
            showError(error.message || 'Failed to generate code. Please try again.');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Generate Code <i data-lucide="arrow-right" class="ml-2 h-5 w-5 inline"></i>';
            lucide.createIcons();
        }
    });
}

// Copy code to clipboard
if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(generatedCode);
            
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i data-lucide="check" class="mr-2 h-4 w-4 inline"></i> Copied!';
            lucide.createIcons();
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                lucide.createIcons();
            }, 2000);
        } catch (error) {
            console.error('Error copying code:', error);
            showError('Failed to copy code. Please copy manually.');
        }
    });
}

// Reset form
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        selectedAllergens.clear();
        generatedCode = '';
        
        updateSelectedDisplay();
        renderAllergenOptions();
        
        if (encodeResult) {
            encodeResult.classList.add('hidden');
        }
    });
}

// Decode button and input
if (decodeInput && decodeBtn) {
    decodeInput.addEventListener('input', () => {
        decodeBtn.disabled = decodeInput.value.trim() === '';
    });
    
    decodeBtn.addEventListener('click', async () => {
        const code = decodeInput.value.trim();
        
        if (!code) {
            showError('Please enter a code to decode');
            return;
        }
        
        try {
            decodeBtn.disabled = true;
            decodeBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-5 w-5 animate-spin inline"></i> Decoding...';
            lucide.createIcons();
            
            console.log('Decoding code:', code);
            
            const response = await fetch(`${API_BASE_URL}/decode`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code
                })
            });
            
            const data = await response.json();
            console.log('Decode response:', data);
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Failed to decode code');
            }
            
            // Display decoded allergens
            decodedAllergensList.innerHTML = data.allergens.map(allergen => `
                <span class="inline-flex items-center px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm font-medium">
                    ${escapeHtml(capitalizeFirst(allergen))}
                </span>
            `).join('');
            
            decodeResult.classList.remove('hidden');
            
            console.log('Decoded code:', {
                code: code,
                words: data.words,
                allergens: data.allergens
            });
            
        } catch (error) {
            console.error('Error decoding code:', error);
            showError(error.message || 'Failed to decode code. Please check the code and try again.');
            if (decodeResult) {
                decodeResult.classList.add('hidden');
            }
        } finally {
            decodeBtn.disabled = false;
            decodeBtn.innerHTML = '<i data-lucide="search" class="mr-2 h-5 w-5 inline"></i> Decode';
            lucide.createIcons();
        }
    });
}

// Utility functions
function showError(message) {
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
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Make functions globally available for onclick handlers
window.toggleAllergen = toggleAllergen;
window.toggleAllergenFromTag = toggleAllergen;

// Initialize on page load
window.addEventListener('load', () => {
    console.log('Page loaded, initializing...');
    loadAllergens();
});
