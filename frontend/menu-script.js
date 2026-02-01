// ==========================================
// Menu Scanner - Main Script
// ==========================================

// ==========================================
// 1. MOCK DATA
// ==========================================
const MOCK_MENU_ITEMS = [
    { name: "Caesar Salad", ingredients: ["lettuce", "parmesan", "croutons", "egg"], allergens: ["milk", "eggs", "wheat"] },
    { name: "Grilled Salmon", ingredients: ["salmon", "lemon", "herbs"], allergens: ["fish"] },
    { name: "Pasta Carbonara", ingredients: ["pasta", "bacon", "eggs", "parmesan"], allergens: ["wheat", "eggs", "milk"] },
    { name: "Pad Thai", ingredients: ["rice noodles", "shrimp", "peanuts", "tofu"], allergens: ["shellfish", "peanuts", "soy"] },
    { name: "Vegetable Stir Fry", ingredients: ["mixed vegetables", "sesame oil", "soy sauce"], allergens: ["sesame", "soy"] },
    { name: "Grilled Chicken", ingredients: ["chicken", "herbs", "olive oil"], allergens: [] },
    { name: "Fresh Fruit Bowl", ingredients: ["seasonal fruits"], allergens: [] },
    { name: "Mushroom Risotto", ingredients: ["rice", "mushrooms", "parmesan", "butter"], allergens: ["milk"] },
    { name: "Fish Tacos", ingredients: ["fish", "tortilla", "cabbage", "lime"], allergens: ["fish", "wheat"] },
    { name: "Garden Salad", ingredients: ["mixed greens", "tomatoes", "cucumber", "olive oil"], allergens: [] },
];

const ALLERGEN_LABELS = {
    milk: { name: "Milk", emoji: "🥛" },
    eggs: { name: "Eggs", emoji: "🥚" },
    peanuts: { name: "Peanuts", emoji: "🥜" },
    wheat: { name: "Wheat", emoji: "🌾" },
    soy: { name: "Soy", emoji: "🫘" },
    fish: { name: "Fish", emoji: "🐟" },
    shellfish: { name: "Shellfish", emoji: "🦐" },
    sesame: { name: "Sesame", emoji: "🫘" },
    "tree-nuts": { name: "Tree Nuts", emoji: "🌰" },
    mustard: { name: "Mustard", emoji: "🟡" },
    celery: { name: "Celery", emoji: "🥬" },
};

// State
let userAllergens = [];

// ==========================================
// 2. DOM INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Get DOM elements
    const codeInput = document.getElementById('userCodeInput');
    const analyzeBtn = document.getElementById('analyzeMenuBtn');

    // Only run if we're on the menu page
    if (!codeInput || !analyzeBtn) return;

    // Setup event listeners
    setupInputValidation();
    setupAnalyze();
    setupReset();
});

// ==========================================
// 3. EVENT HANDLERS
// ==========================================

function setupInputValidation() {
    const codeInput = document.getElementById('userCodeInput');
    const analyzeBtn = document.getElementById('analyzeMenuBtn');

    codeInput.addEventListener('input', (e) => {
        analyzeBtn.disabled = e.target.value.trim() === "";
    });
}

function setupAnalyze() {
    const analyzeBtn = document.getElementById('analyzeMenuBtn');
    const codeInput = document.getElementById('userCodeInput');
    const inputView = document.getElementById('inputView');
    const resultsView = document.getElementById('resultsView');

    analyzeBtn.addEventListener('click', () => {
        const code = codeInput.value.toLowerCase();

        // Mock decoding logic
        if (code.includes("ocean")) {
            userAllergens = ["milk", "peanuts", "shellfish"];
        } else if (code.includes("crystal")) {
            userAllergens = ["eggs", "wheat"];
        } else if (code.includes("meadow")) {
            userAllergens = ["fish", "tree-nuts"];
        } else {
            // Default fallback for demo
            userAllergens = ["milk", "eggs"];
        }

        // Switch views
        inputView.classList.add('hidden');
        resultsView.classList.remove('hidden');

        // Render results
        renderActiveAllergens();
        renderMenu();

        // Refresh icons
        if (typeof lucide !== 'undefined') lucide.createIcons();
    });
}

function setupReset() {
    const resetBtn = document.getElementById('resetMenuBtn');
    const codeInput = document.getElementById('userCodeInput');
    const analyzeBtn = document.getElementById('analyzeMenuBtn');
    const inputView = document.getElementById('inputView');
    const resultsView = document.getElementById('resultsView');

    resetBtn.addEventListener('click', () => {
        userAllergens = [];
        codeInput.value = "";
        analyzeBtn.disabled = true;

        // Switch views back
        resultsView.classList.add('hidden');
        inputView.classList.remove('hidden');
    });
}

// ==========================================
// 4. RENDERING FUNCTIONS
// ==========================================

function renderActiveAllergens() {
    const container = document.getElementById('activeAllergensList');
    container.innerHTML = '';

    userAllergens.forEach(id => {
        const data = ALLERGEN_LABELS[id];
        const span = document.createElement('span');
        span.className = "px-3 py-1 rounded-full bg-white border border-blue-200 text-sm font-medium flex items-center gap-1 text-blue-700 shadow-sm";
        span.innerText = `${data ? data.emoji : ''} ${data ? data.name : id}`;
        container.appendChild(span);
    });
}

function renderMenu() {
    const container = document.getElementById('menuListContainer');
    container.innerHTML = '';

    let safeCount = 0;
    let avoidCount = 0;

    MOCK_MENU_ITEMS.forEach(item => {
        // Check safety
        const conflictAllergens = item.allergens.filter(a => userAllergens.includes(a));
        const isSafe = conflictAllergens.length === 0;

        if (isSafe) safeCount++; else avoidCount++;

        // Create card
        const card = document.createElement('div');
        const borderColor = isSafe ? "border-green-200 bg-green-50/50" : "border-red-200 bg-red-50/50";
        const icon = isSafe
            ? `<i data-lucide="check-circle" class="h-5 w-5 text-green-600"></i>`
            : `<i data-lucide="alert-triangle" class="h-5 w-5 text-red-600"></i>`;
        const badgeClass = isSafe ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700";
        const badgeText = isSafe ? "Safe" : "Avoid";

        card.className = `p-6 rounded-xl border-2 transition-all ${borderColor}`;

        // Build ingredients string
        const ingredientsStr = item.ingredients.join(", ");

        // Build conflict tags (only if unsafe)
        let conflictTagsHTML = '';
        if (!isSafe) {
            conflictTagsHTML = `<div class="mt-3 flex flex-wrap gap-2">`;
            conflictAllergens.forEach(a => {
                const label = ALLERGEN_LABELS[a];
                conflictTagsHTML += `
                    <span class="px-2 py-1 rounded-md bg-red-100 text-red-700 text-xs font-bold flex items-center gap-1">
                        ${label ? label.emoji : ''} ${label ? label.name : a}
                    </span>`;
            });
            conflictTagsHTML += `</div>`;
        }

        // Card HTML
        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                        ${icon}
                        <h3 class="font-semibold text-gray-900 text-lg">${item.name}</h3>
                    </div>
                    <p class="text-sm text-gray-600">${ingredientsStr}</p>
                    ${conflictTagsHTML}
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-bold ${badgeClass}">${badgeText}</span>
            </div>
        `;

        container.appendChild(card);
    });

    // Update stats
    document.getElementById('safeCount').innerText = safeCount;
    document.getElementById('avoidCount').innerText = avoidCount;

    // Refresh icons
    if (typeof lucide !== 'undefined') lucide.createIcons();
}
