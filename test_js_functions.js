// Test script to verify JavaScript functions for language validation
console.log("Testing JavaScript functions for language validation...");

// Check if required functions exist
const requiredFunctions = [
    'validateCodeLanguage',
    'showCodeError',
    'clearCodeError',
    'setupRealTimeValidation'
];

const missingFunctions = [];

requiredFunctions.forEach(func => {
    if (typeof window[func] === 'function') {
        console.log(`✓ ${func} function exists`);
    } else {
        console.log(`✗ ${func} function is missing`);
        missingFunctions.push(func);
    }
});

// Check if required DOM elements exist
const requiredElements = [
    'postCode',
    'postLanguage',
    'codeError'
];

const missingElements = [];

requiredElements.forEach(element => {
    if (document.getElementById(element)) {
        console.log(`✓ ${element} element exists`);
    } else {
        console.log(`✗ ${element} element is missing`);
        missingElements.push(element);
    }
});

// Summary
if (missingFunctions.length === 0 && missingElements.length === 0) {
    console.log("✓ All required functions and elements are present!");
} else {
    console.log("✗ Issues found:");
    if (missingFunctions.length > 0) {
        console.log("  Missing functions:", missingFunctions.join(", "));
    }
    if (missingElements.length > 0) {
        console.log("  Missing elements:", missingElements.join(", "));
    }
}