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
    const gridContainer = document.getElementById('allergenGrid');
    if (!gridContainer) return;

    // Render allergen grid
    renderAllergenGrid();

    // Setup tab switching
    setupTabs();

    // Setup encode functionality
    setupEncode();

    // Setup decode functionality
    setupDecode();
});

// ==========================================
// 4. RENDER FUNCTIONS
// ==========================================

function renderAllergenGrid() {
    const gridContainer = document.getElementById('allergenGrid');
    if (!gridContainer) return;

    ALLERGENS.forEach(allergen => {
        const btn = document.createElement('button');
        btn.className = "allergen-btn p-4 rounded-xl border-2 border-gray-200 bg-white hover:border-blue-300 transition-all text-left";
        btn.dataset.id = allergen.id;
        btn.innerHTML = `
            <span class="text-2xl mb-2 block">${allergen.emoji}</span>
            <span class="text-sm font-medium text-gray-900">${allergen.name}</span>
        `;

        btn.addEventListener('click', () => toggleAllergen(allergen.id, btn));
        gridContainer.appendChild(btn);
    });
}

// ==========================================
// 5. EVENT HANDLERS
// ==========================================

function toggleAllergen(id, btnElement) {
    const index = selectedAllergens.indexOf(id);
    if (index > -1) {
        selectedAllergens.splice(index, 1);
        btnElement.classList.remove('selected');
    } else {
        selectedAllergens.push(id);
        btnElement.classList.add('selected');
    }

    updateButtonStates();
}

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

    if (generateBtn) {
        generateBtn.addEventListener('click', () => {
            const code = encodeAllergens(selectedAllergens);
            const words = code.split('.');

            const codeText = document.getElementById('generatedCodeText');
            codeText.innerHTML = `${words[0]}.<span class="text-blue-600">${words[1]}</span>.${words[2]}`;

            document.getElementById('encodeResult').classList.remove('hidden');
            lucide.createIcons();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            selectedAllergens = [];

            // Reset all allergen buttons
            document.querySelectorAll('.allergen-btn').forEach(btn => {
                btn.classList.remove('selected');
            });

            document.getElementById('encodeResult').classList.add('hidden');
            updateButtonStates();
        });
    }

    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const codeText = document.getElementById('generatedCodeText').innerText;
            navigator.clipboard.writeText(codeText);

            const originalHTML = this.innerHTML;
            this.innerHTML = `<i data-lucide="check" class="mr-2 h-4 w-4"></i> Copied!`;
            lucide.createIcons();

            setTimeout(() => {
                this.innerHTML = originalHTML;
                lucide.createIcons();
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
        const allergenIds = decodeWords(code);

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
    });
}
