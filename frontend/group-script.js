// ==========================================
// Group Allergen Code - Main Script
// ==========================================

// ==========================================
// 1. DATA & CONSTANTS
// ==========================================
const WORD_POOL = [
    "ocean", "maple", "thunder", "crystal", "velvet", "ember", "frost", "coral",
    "meadow", "storm", "willow", "sage", "river", "breeze", "dawn", "dusk",
    "summit", "valley", "canyon", "ridge", "harbor", "beacon", "anchor", "compass",
    "cedar", "birch", "oak", "pine", "fern", "moss", "ivy", "bloom",
];

// State
let members = [];

// ==========================================
// 2. DOM INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Get DOM elements
    const inputName = document.getElementById('inputName');
    const inputCode = document.getElementById('inputCode');
    const addMemberBtn = document.getElementById('addMemberBtn');

    // Only run if we're on the group page
    if (!inputName || !inputCode || !addMemberBtn) return;

    // Setup event listeners
    setupInputValidation();
    setupAddMember();
    setupGenerateCode();
    setupCopyButton();
});

// ==========================================
// 3. EVENT HANDLERS
// ==========================================

function setupInputValidation() {
    const inputName = document.getElementById('inputName');
    const inputCode = document.getElementById('inputCode');
    const addMemberBtn = document.getElementById('addMemberBtn');

    const validateInputs = () => {
        const valid = inputName.value.trim() !== "" && inputCode.value.trim() !== "";
        addMemberBtn.disabled = !valid;
    };

    inputName.addEventListener('input', validateInputs);
    inputCode.addEventListener('input', validateInputs);
}

function setupAddMember() {
    const inputName = document.getElementById('inputName');
    const inputCode = document.getElementById('inputCode');
    const addMemberBtn = document.getElementById('addMemberBtn');
    const resultSection = document.getElementById('resultSection');

    addMemberBtn.addEventListener('click', () => {
        const newMember = {
            id: Date.now().toString(),
            name: inputName.value.trim(),
            code: inputCode.value.trim().toLowerCase()
        };

        members.push(newMember);

        // Clear inputs
        inputName.value = "";
        inputCode.value = "";
        addMemberBtn.disabled = true;

        // Reset result (since data changed)
        resultSection.classList.add('hidden');

        renderMembers();
    });
}

function setupGenerateCode() {
    const generateBtn = document.getElementById('generateGroupCodeBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateCombinedCode);
    }
}

function setupCopyButton() {
    const copyBtn = document.getElementById('copyGroupBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const text = document.getElementById('combinedCodeText').innerText;
            navigator.clipboard.writeText(text);

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

// ==========================================
// 4. MEMBER MANAGEMENT
// ==========================================

function removeMember(id) {
    members = members.filter(m => m.id !== id);
    document.getElementById('resultSection').classList.add('hidden');
    renderMembers();
}

function renderMembers() {
    const membersSection = document.getElementById('membersSection');
    const membersList = document.getElementById('membersList');
    const memberCountLabel = document.getElementById('memberCount');
    const emptyState = document.getElementById('emptyState');

    // Toggle sections
    if (members.length > 0) {
        membersSection.classList.remove('hidden');
        emptyState.classList.add('hidden');
    } else {
        membersSection.classList.add('hidden');
        emptyState.classList.remove('hidden');
    }

    // Update count
    memberCountLabel.innerText = members.length;

    // Rebuild list
    membersList.innerHTML = '';

    members.forEach(member => {
        const item = document.createElement('div');
        item.className = "flex items-center justify-between p-4 rounded-xl bg-gray-100";

        item.innerHTML = `
            <div>
                <p class="font-medium text-gray-900">${member.name}</p>
                <p class="text-sm text-gray-500 font-mono">${member.code}</p>
            </div>
            <button class="remove-btn p-2 rounded-lg hover:bg-red-100 text-gray-400 hover:text-red-600 transition-colors" data-id="${member.id}">
                <i data-lucide="x" class="h-5 w-5"></i>
            </button>
        `;

        membersList.appendChild(item);
    });

    // Attach remove event listeners
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            removeMember(id);
        });
    });

    // Refresh icons
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

// ==========================================
// 5. CODE GENERATION
// ==========================================

function generateCombinedCode() {
    if (members.length === 0) return;

    // Hash all codes together
    const allCodes = members.map(m => m.code).sort().join("-");
    let hashNum = 0;

    for (let i = 0; i < allCodes.length; i++) {
        hashNum = ((hashNum << 5) - hashNum) + allCodes.charCodeAt(i);
        hashNum = hashNum & hashNum;
    }
    hashNum = Math.abs(hashNum);

    const word1 = WORD_POOL[hashNum % WORD_POOL.length];
    const word2 = WORD_POOL[(hashNum * 7) % WORD_POOL.length];
    const word3 = WORD_POOL[(hashNum * 13) % WORD_POOL.length];

    // Display result
    const displayHTML = `${word1}.<span class="text-blue-600">${word2}</span>.${word3}`;
    document.getElementById('combinedCodeText').innerHTML = displayHTML;
    document.getElementById('resultSection').classList.remove('hidden');
}
