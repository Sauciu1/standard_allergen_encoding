// ==========================================
// Group Allergen Code - Main Script
// ==========================================

// Initialize Lucide icons
lucide.createIcons();

// ==========================================
// 1. DATA & CONSTANTS
// ==========================================
const WORD_POOL = [
    "ocean", "maple", "thunder", "crystal", "velvet", "ember", "frost", "coral",
    "meadow", "storm", "willow", "sage", "river", "breeze", "dawn", "dusk",
    "summit", "valley", "canyon", "ridge", "harbor", "beacon", "anchor", "compass",
    "cedar", "birch", "oak", "pine", "fern", "moss", "ivy", "bloom",
];

// API Configuration
const API_BASE_URL = `http://${window.location.hostname}:5000/api`;

// State
let members = [];

// DOM Elements
const inputName = document.getElementById('inputName');
const inputCode = document.getElementById('inputCode');
const addMemberBtn = document.getElementById('addMemberBtn');
const generateBtn = document.getElementById('generateGroupCodeBtn');
const copyBtn = document.getElementById('copyGroupBtn');
const membersSection = document.getElementById('membersSection');
const membersList = document.getElementById('membersList');
const memberCountLabel = document.getElementById('memberCount');
const emptyState = document.getElementById('emptyState');
const resultSection = document.getElementById('resultSection');
const combinedCodeText = document.getElementById('combinedCodeText');

// ==========================================
// 2. DOM INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Only run if we're on the group page
    if (!inputName || !inputCode || !addMemberBtn) return;

    // Setup event listeners
    // Input validation
    const validateInputs = () => {
        const valid = inputName.value.trim() !== "" && inputCode.value.trim() !== "";
        addMemberBtn.disabled = !valid;
    };

    inputName.addEventListener('input', validateInputs);
    inputCode.addEventListener('input', validateInputs);

    // Add member
    addMemberBtn.addEventListener('click', async () => {
        const name = inputName.value.trim();
        const code = inputCode.value.trim();
        
        await addMember(name, code);
    });

    // Generate combined code
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            await generateCombinedCode();
        });
    }

    // Copy button
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const text = combinedCodeText.textContent;
            navigator.clipboard.writeText(text);

            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i data-lucide="check" class="mr-2 h-4 w-4"></i> Copied!';
            lucide.createIcons();

            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                lucide.createIcons();
            }, 2000);
        });
    }
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

    addMemberBtn.addEventListener('click', async () => {
        const name = inputName.value.trim();
        const code = inputCode.value.trim();
        
        await addMember(name, code);
    });
}

function setupGenerateCode() {
    const generateBtn = document.getElementById('generateGroupCodeBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            await generateCombinedCode();
        });
    }
}

function setupCopyButton() {
    const copyBtn = document.getElementById('copyGroupBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const text = combinedCodeText.textContent;
            navigator.clipboard.writeText(text);

            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i data-lucide="check" class="mr-2 h-4 w-4"></i> Copied!';
            lucide.createIcons();

            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                lucide.createIcons();
            }, 2000);
        });
    }
}

// ==========================================
// 4. MEMBER MANAGEMENT
// ==========================================

async function addMember(name, code) {
    try {
        // Show loading
        if (addMemberBtn) {
            addMemberBtn.disabled = true;
            addMemberBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 animate-spin inline"></i> Validating...';
            lucide.createIcons();
        }
        
        console.log('Validating code:', code);
        
        // Validate code by trying to decode it
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
        console.log('Validation response:', data);
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Invalid allergen code. Please check and try again.');
        }
        
        // Code is valid, add member
        const newMember = {
            id: Date.now().toString(),
            name: name,
            code: code,
            allergens: data.allergens // Store decoded allergens
        };

        members.push(newMember);

        // Clear inputs
        if (inputName) inputName.value = "";
        if (inputCode) inputCode.value = "";

        // Reset result (since data changed)
        if (resultSection) resultSection.classList.add('hidden');

        renderMembers();
        
        showSuccess(`${name} added successfully!`);
        
    } catch (error) {
        console.error('Error adding member:', error);
        showError(error.message || 'Failed to add member. Please check the allergen code.');
    } finally {
        if (addMemberBtn) {
            addMemberBtn.disabled = false;
            addMemberBtn.innerHTML = '<i data-lucide="plus" class="mr-2 h-4 w-4"></i> Add Member';
            lucide.createIcons();
        }
    }
}

function removeMember(id) {
    members = members.filter(m => m.id !== id);
    if (resultSection) resultSection.classList.add('hidden');
    renderMembers();
}

function renderMembers() {
    // Toggle sections
    if (members.length > 0) {
        if (membersSection) membersSection.classList.remove('hidden');
        if (emptyState) emptyState.classList.add('hidden');
    } else {
        if (membersSection) membersSection.classList.add('hidden');
        if (emptyState) emptyState.classList.remove('hidden');
    }

    // Update count
    if (memberCountLabel) memberCountLabel.textContent = members.length;

    // Rebuild list
    if (membersList) {
        membersList.innerHTML = '';

        members.forEach(member => {
            const item = document.createElement('div');
            item.className = "flex items-center justify-between p-4 rounded-xl bg-gray-50 border border-gray-200";

            const allergensList = member.allergens.map(a => capitalizeFirst(a)).join(', ');
            
            item.innerHTML = `
                <div class="flex-1">
                    <p class="font-medium text-gray-900 mb-1">${escapeHtml(member.name)}</p>
                    <p class="text-xs text-gray-500 font-mono mb-1">${escapeHtml(member.code)}</p>
                    <p class="text-xs text-gray-600">Allergens: ${escapeHtml(allergensList)}</p>
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
    }

    lucide.createIcons();
}

// ==========================================
// 5. CODE GENERATION
// ==========================================

async function generateCombinedCode() {
    if (members.length === 0) {
        showError('Please add at least one member');
        return;
    }

    try {
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-5 w-5 animate-spin inline"></i> Combining...';
            lucide.createIcons();
        }
        
        const codes = members.map(m => m.code);
        
        console.log('Combining codes:', codes);
        
        const response = await fetch(`${API_BASE_URL}/combine-codes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                codes: codes
            })
        });
        
        const data = await response.json();
        console.log('Combine response:', data);
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to combine codes');
        }
        
        // Display result
        if (combinedCodeText) combinedCodeText.textContent = data.combined_code;
        if (resultSection) resultSection.classList.remove('hidden');
        
        // Log combined allergens for debugging
        console.log('Combined allergens:', data.combined_allergens);
        
        showSuccess('Combined code generated successfully!');
        
    } catch (error) {
        console.error('Error generating combined code:', error);
        showError(error.message || 'Failed to generate combined code. Please try again.');
    } finally {
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Generate Combined Code <i data-lucide="arrow-right" class="ml-2 h-5 w-5 inline"></i>';
            lucide.createIcons();
        }
    }
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

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 z-50 p-4 rounded-lg bg-green-50 border border-green-200 shadow-lg max-w-md';
    successDiv.innerHTML = `
        <div class="flex items-center gap-3">
            <i data-lucide="check-circle" class="h-5 w-5 text-green-600 flex-shrink-0"></i>
            <p class="text-sm text-green-700">${escapeHtml(message)}</p>
        </div>
    `;
    
    document.body.appendChild(successDiv);
    lucide.createIcons();
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
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
