// ==========================================
// Individual Allergen Code - Main Script
// ==========================================

// ==========================================
// 1. DATA & CONSTANTS
// ==========================================
const ALLERGENS = [
    { id: "milk", name: "Milk", emoji: "🥛" },
    { id: "eggs", name: "Eggs", emoji: "🥚" },
    { id: "peanuts", name: "Peanuts", emoji: "🥜" },
    { id: "tree-nuts", name: "Tree Nuts", emoji: "🌰" },
    { id: "wheat", name: "Wheat", emoji: "🌾" },
    { id: "soy", name: "Soy", emoji: "🫘" },
    { id: "fish", name: "Fish", emoji: "🐟" },
    { id: "shellfish", name: "Shellfish", emoji: "🦐" },
    { id: "sesame", name: "Sesame", emoji: "🫘" },
    { id: "mustard", name: "Mustard", emoji: "🟡" },
    { id: "celery", name: "Celery", emoji: "🥬" },
    { id: "lupin", name: "Lupin", emoji: "🌸" },
    { id: "molluscs", name: "Molluscs", emoji: "🦪" },
    { id: "sulphites", name: "Sulphites", emoji: "🍷" },
];

const WORD_POOL = [
    "ocean", "maple", "thunder", "crystal", "velvet", "ember", "frost", "coral",
    "meadow", "storm", "willow", "sage", "river", "breeze", "dawn", "dusk",
    "summit", "valley", "canyon", "ridge", "harbor", "beacon", "anchor", "compass",
    "cedar", "birch", "oak", "pine", "fern", "moss", "ivy", "bloom",
];

// State
let selectedAllergens = [];
let isDropdownOpen = false;
let html5QrCode = null;

// ==========================================
// 2. ENCODING/DECODING FUNCTIONS
// ==========================================

function encodeAllergens(selectedIds) {
    if (selectedIds.length === 0) return "";

    const sorted = [...selectedIds].sort();
    const hash = sorted.join("-");
    let hashNum = 0;

    for (let i = 0; i < hash.length; i++) {
        hashNum = ((hashNum << 5) - hashNum) + hash.charCodeAt(i);
        hashNum = hashNum & hashNum;
    }
    hashNum = Math.abs(hashNum);

    const word1 = WORD_POOL[hashNum % WORD_POOL.length];
    const word2 = WORD_POOL[(hashNum * 7) % WORD_POOL.length];
    const word3 = WORD_POOL[(hashNum * 13) % WORD_POOL.length];

    return `${word1}.${word2}.${word3}`;
}

function decodeWords(code) {
    const words = code.toLowerCase().split(".");
    if (words.length !== 3) return null;

    // Mock decoding - in production this would use a proper lookup
    const mockResults = {
        "ocean.maple.thunder": ["milk", "peanuts", "shellfish"],
        "crystal.velvet.ember": ["eggs", "wheat", "soy"],
        "meadow.storm.willow": ["fish", "tree-nuts"],
        "river.breeze.dawn": ["sesame", "mustard"],
    };

    return mockResults[code] || ["milk", "eggs"];
}

// ==========================================
// 3. DOM INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Only run if we're on the individual page
    const dropdownBtn = document.getElementById('dropdownBtn');
    if (!dropdownBtn) return;

    // Render allergen options in dropdown
    renderAllergenOptions();

    // Setup dropdown functionality
    setupDropdown();

    // Setup tab switching
    setupTabs();

    // Setup encode functionality
    setupEncode();

    // Setup decode functionality
    setupDecode();
});

// ==========================================
// 4. DROPDOWN FUNCTIONS
// ==========================================

function renderAllergenOptions() {
    const optionsContainer = document.getElementById('allergenOptions');
    if (!optionsContainer) return;

    ALLERGENS.forEach(allergen => {
        const option = document.createElement('label');
        option.className = "allergen-option flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors";
        option.dataset.id = allergen.id;
        option.dataset.name = allergen.name.toLowerCase();
        option.innerHTML = `
            <input type="checkbox" class="allergen-checkbox w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" data-id="${allergen.id}">
            <span class="text-xl">${allergen.emoji}</span>
            <span class="text-sm font-medium text-gray-900">${allergen.name}</span>
        `;
        optionsContainer.appendChild(option);
    });

    // Add checkbox change listeners
    document.querySelectorAll('.allergen-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const id = e.target.dataset.id;
            if (e.target.checked) {
                if (!selectedAllergens.includes(id)) {
                    selectedAllergens.push(id);
                }
            } else {
                selectedAllergens = selectedAllergens.filter(a => a !== id);
            }
            updateSelectedDisplay();
            updateButtonStates();
        });
    });
}

function setupDropdown() {
    const dropdownBtn = document.getElementById('dropdownBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const dropdownArrow = document.getElementById('dropdownArrow');
    const searchInput = document.getElementById('allergenSearch');

    // Toggle dropdown on button click
    dropdownBtn.addEventListener('click', () => {
        isDropdownOpen = !isDropdownOpen;
        dropdownMenu.classList.toggle('hidden', !isDropdownOpen);
        dropdownArrow.classList.toggle('rotate-180', isDropdownOpen);

        if (isDropdownOpen && searchInput) {
            searchInput.focus();
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('allergenDropdown');
        if (!dropdown.contains(e.target) && isDropdownOpen) {
            isDropdownOpen = false;
            dropdownMenu.classList.add('hidden');
            dropdownArrow.classList.remove('rotate-180');
        }
    });

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            document.querySelectorAll('.allergen-option').forEach(option => {
                const name = option.dataset.name;
                if (name.includes(searchTerm)) {
                    option.classList.remove('hidden');
                } else {
                    option.classList.add('hidden');
                }
            });
        });
    }
}

function updateSelectedDisplay() {
    const tagsContainer = document.getElementById('selectedTagsContainer');
    const placeholder = document.getElementById('dropdownPlaceholder');
    const countDisplay = document.getElementById('allergenCount');

    // Update count
    const count = selectedAllergens.length;
    countDisplay.textContent = `${count} selected`;

    // Update count badge color
    if (count > 0) {
        countDisplay.classList.remove('bg-blue-100', 'text-blue-700');
        countDisplay.classList.add('bg-blue-600', 'text-white');
    } else {
        countDisplay.classList.remove('bg-blue-600', 'text-white');
        countDisplay.classList.add('bg-blue-100', 'text-blue-700');
    }

    // Update placeholder
    if (count > 0) {
        placeholder.textContent = `${count} allergen${count > 1 ? 's' : ''} selected`;
        placeholder.classList.remove('text-gray-500');
        placeholder.classList.add('text-gray-900');
    } else {
        placeholder.textContent = 'Click to select allergens...';
        placeholder.classList.remove('text-gray-900');
        placeholder.classList.add('text-gray-500');
    }

    // Update tags display
    tagsContainer.innerHTML = '';
    if (count > 0) {
        tagsContainer.classList.remove('hidden');
        tagsContainer.classList.add('flex');

        selectedAllergens.forEach(id => {
            const allergen = ALLERGENS.find(a => a.id === id);
            if (allergen) {
                const tag = document.createElement('span');
                tag.className = "inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium";
                tag.innerHTML = `
                    <span>${allergen.emoji}</span>
                    <span>${allergen.name}</span>
                    <button type="button" class="remove-tag ml-1 hover:text-blue-900" data-id="${id}">
                        <i data-lucide="x" class="h-3 w-3"></i>
                    </button>
                `;
                tagsContainer.appendChild(tag);
            }
        });

        // Add remove tag listeners
        document.querySelectorAll('.remove-tag').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                selectedAllergens = selectedAllergens.filter(a => a !== id);

                // Uncheck the checkbox
                const checkbox = document.querySelector(`.allergen-checkbox[data-id="${id}"]`);
                if (checkbox) checkbox.checked = false;

                updateSelectedDisplay();
                updateButtonStates();
            });
        });

        // Refresh icons for the X buttons
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } else {
        tagsContainer.classList.add('hidden');
        tagsContainer.classList.remove('flex');
    }
}

// ==========================================
// 5. QR CODE GENERATION
// ==========================================

function generateQRCode(code) {
    const canvas = document.getElementById('qrCodeCanvas');
    if (!canvas) return;

    // Check if QRCode library is loaded
    if (typeof QRCode !== 'undefined') {
        QRCode.toCanvas(canvas, code, {
            width: 180,
            margin: 2,
            color: {
                dark: '#1f2937',  // gray-800
                light: '#ffffff'
            }
        }, function(error) {
            if (error) console.error('QR Code generation error:', error);
        });
    } else {
        console.warn('QRCode library not loaded');
    }
}

// ==========================================
// 6. EVENT HANDLERS
// ==========================================

function updateButtonStates() {
    const generateBtn = document.getElementById('generateBtn');
    const resetBtn = document.getElementById('resetBtn');
    const encodeResult = document.getElementById('encodeResult');

    if (selectedAllergens.length > 0) {
        generateBtn.disabled = false;
        resetBtn.classList.remove('hidden');
    } else {
        generateBtn.disabled = true;
        resetBtn.classList.add('hidden');
        encodeResult.classList.add('hidden');
    }
}

function setupTabs() {
    const tabEncode = document.getElementById('tabEncode');
    const tabDecode = document.getElementById('tabDecode');
    const sectionEncode = document.getElementById('encodeSection');
    const sectionDecode = document.getElementById('decodeSection');

    if (!tabEncode || !tabDecode) return;

    tabEncode.addEventListener('click', () => {
        tabEncode.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        tabEncode.classList.remove('text-gray-500');
        tabDecode.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        tabDecode.classList.add('text-gray-500');

        sectionEncode.classList.remove('hidden');
        sectionDecode.classList.add('hidden');
    });

    tabDecode.addEventListener('click', () => {
        tabDecode.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        tabDecode.classList.remove('text-gray-500');
        tabEncode.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        tabEncode.classList.add('text-gray-500');

        sectionDecode.classList.remove('hidden');
        sectionEncode.classList.add('hidden');
    });
}

function setupEncode() {
    const generateBtn = document.getElementById('generateBtn');
    const resetBtn = document.getElementById('resetBtn');
    const copyBtn = document.getElementById('copyBtn');
    const downloadQrBtn = document.getElementById('downloadQrBtn');

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const code = encodeAllergens(selectedAllergens);
            const words = code.split('.');

            const codeText = document.getElementById('generatedCodeText');
            codeText.innerHTML = `${words[0]}.<span class="text-blue-600">${words[1]}</span>.${words[2]}`;

            // Generate QR Code
            generateQRCode(code);

            document.getElementById('encodeResult').classList.remove('hidden');
            if (typeof lucide !== 'undefined') lucide.createIcons();
        });
    }

    // Download QR Code
    if (downloadQrBtn) {
        downloadQrBtn.addEventListener('click', () => {
            const canvas = document.getElementById('qrCodeCanvas');
            const link = document.createElement('a');
            link.download = 'allergen-code-qr.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            selectedAllergens = [];

            // Uncheck all checkboxes
            document.querySelectorAll('.allergen-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });

            // Clear search
            const searchInput = document.getElementById('allergenSearch');
            if (searchInput) searchInput.value = '';

            // Show all options
            document.querySelectorAll('.allergen-option').forEach(option => {
                option.classList.remove('hidden');
            });

            document.getElementById('encodeResult').classList.add('hidden');
            updateSelectedDisplay();
            updateButtonStates();
        });
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const codeText = document.getElementById('generatedCodeText').innerText;
            navigator.clipboard.writeText(codeText);

            const originalHTML = this.innerHTML;
            this.innerHTML = `<i data-lucide="check" class="mr-2 h-4 w-4"></i> Copied!`;
            if (typeof lucide !== 'undefined') lucide.createIcons();

            setTimeout(() => {
                this.innerHTML = originalHTML;
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }, 2000);
        });
    }
}

function setupDecode() {
    const decodeInput = document.getElementById('decodeInput');
    const decodeBtn = document.getElementById('decodeBtn');
    const decodeResult = document.getElementById('decodeResult');

    if (!decodeInput || !decodeBtn) return;

    decodeInput.addEventListener('input', (e) => {
        decodeBtn.disabled = e.target.value.trim() === "";
    });

    decodeBtn.addEventListener('click', () => {
        const code = decodeInput.value.trim().toLowerCase();
        processDecodedCode(code);
    });

    // Setup decode tabs
    setupDecodeTabs();

    // Setup QR Scanner
    setupQrScanner();
}

function processDecodedCode(code) {
    const allergenIds = decodeWords(code);
    const decodeResult = document.getElementById('decodeResult');

    if (allergenIds) {
        const listContainer = document.getElementById('decodedAllergensList');
        listContainer.innerHTML = '';

        allergenIds.forEach(id => {
            const allergen = ALLERGENS.find(a => a.id === id);
            if (allergen) {
                const span = document.createElement('span');
                span.className = "px-4 py-2 rounded-full bg-blue-50 border border-blue-200 text-sm font-medium text-blue-700 flex items-center gap-2";
                span.innerHTML = `<span>${allergen.emoji}</span> ${allergen.name}`;
                listContainer.appendChild(span);
            }
        });

        decodeResult.classList.remove('hidden');
    }
}

function setupDecodeTabs() {
    const manualInputTab = document.getElementById('manualInputTab');
    const scanQrTab = document.getElementById('scanQrTab');
    const manualInputSection = document.getElementById('manualInputSection');
    const scanQrSection = document.getElementById('scanQrSection');

    if (!manualInputTab || !scanQrTab) return;

    manualInputTab.addEventListener('click', () => {
        // Update tab styles
        manualInputTab.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        manualInputTab.classList.remove('text-gray-500');
        scanQrTab.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        scanQrTab.classList.add('text-gray-500');

        // Show/hide sections
        manualInputSection.classList.remove('hidden');
        scanQrSection.classList.add('hidden');

        // Stop scanner if running
        stopQrScanner();
    });

    scanQrTab.addEventListener('click', () => {
        // Update tab styles
        scanQrTab.classList.add('bg-white', 'shadow-sm', 'text-gray-900');
        scanQrTab.classList.remove('text-gray-500');
        manualInputTab.classList.remove('bg-white', 'shadow-sm', 'text-gray-900');
        manualInputTab.classList.add('text-gray-500');

        // Show/hide sections
        scanQrSection.classList.remove('hidden');
        manualInputSection.classList.add('hidden');

        // Refresh icons
        if (typeof lucide !== 'undefined') lucide.createIcons();
    });
}

function setupQrScanner() {
    const startScanBtn = document.getElementById('startScanBtn');
    const stopScanBtn = document.getElementById('stopScanBtn');

    if (!startScanBtn) return;

    startScanBtn.addEventListener('click', startQrScanner);

    if (stopScanBtn) {
        stopScanBtn.addEventListener('click', stopQrScanner);
    }
}

function startQrScanner() {
    const qrReader = document.getElementById('qrReader');
    const qrScannerContainer = document.getElementById('qrScannerContainer');
    const startScanContainer = document.getElementById('startScanContainer');
    const scannedCodeDisplay = document.getElementById('scannedCodeDisplay');

    if (!qrReader) return;

    // Show scanner, hide start button
    qrScannerContainer.classList.remove('hidden');
    startScanContainer.classList.add('hidden');
    scannedCodeDisplay.classList.add('hidden');

    // Initialize scanner
    html5QrCode = new Html5Qrcode("qrReader");

    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
    };

    html5QrCode.start(
        { facingMode: "environment" },
        config,
        (decodedText) => {
            // QR Code detected
            onQrCodeScanned(decodedText);
        },
        (errorMessage) => {
            // Scan error - ignore, keep scanning
        }
    ).catch((err) => {
        console.error("Unable to start QR scanner:", err);
        alert("Unable to access camera. Please ensure you have granted camera permissions.");
        stopQrScanner();
    });
}

function stopQrScanner() {
    const qrScannerContainer = document.getElementById('qrScannerContainer');
    const startScanContainer = document.getElementById('startScanContainer');

    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            html5QrCode.clear();
            html5QrCode = null;
        }).catch((err) => {
            console.error("Error stopping scanner:", err);
        });
    }

    // Show start button, hide scanner
    if (qrScannerContainer) qrScannerContainer.classList.add('hidden');
    if (startScanContainer) startScanContainer.classList.remove('hidden');
}

function onQrCodeScanned(code) {
    const scannedCodeDisplay = document.getElementById('scannedCodeDisplay');
    const scannedCodeText = document.getElementById('scannedCodeText');
    const decodeInput = document.getElementById('decodeInput');

    // Show the scanned code
    if (scannedCodeDisplay && scannedCodeText) {
        scannedCodeText.textContent = code;
        scannedCodeDisplay.classList.remove('hidden');
    }

    // Also fill the manual input field
    if (decodeInput) {
        decodeInput.value = code;
        const decodeBtn = document.getElementById('decodeBtn');
        if (decodeBtn) decodeBtn.disabled = false;
    }

    // Stop the scanner
    stopQrScanner();

    // Auto-decode after a short delay
    setTimeout(() => {
        processDecodedCode(code.toLowerCase());
    }, 500);

    // Refresh icons
    if (typeof lucide !== 'undefined') lucide.createIcons();
}
