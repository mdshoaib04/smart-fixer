document.addEventListener('DOMContentLoaded', () => {
    const sourceLanguage = document.getElementById('source-language');
    const targetLanguage = document.getElementById('target-language');
    const sourceCode = document.getElementById('source-code');
    const targetCode = document.getElementById('target-code');
    const translateBtn = document.getElementById('translate-btn');

    const languages = [
        "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "PHP", "Swift", "Ruby", "Go", 
        "Kotlin", "Rust", "Scala", "Perl", "Dart", "Haskell", "MATLAB", "R", "SQL", "Shell", "Objective-C"
    ];

    // Populate language dropdowns
    languages.forEach(lang => {
        const option1 = new Option(lang, lang);
        const option2 = new Option(lang, lang);
        sourceLanguage.add(option1);
        targetLanguage.add(option2);
    });

    // Handle translation
    translateBtn.addEventListener('click', async () => {
        const sourceLang = sourceLanguage.value;
        const targetLang = targetLanguage.value;
        const code = sourceCode.value;

        if (!code) {
            alert("Please enter some code to translate.");
            return;
        }

        targetCode.value = "Translating...";

        const response = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, sourceLang, targetLang })
        });

        const result = await response.json();
        if (response.ok) {
            targetCode.value = result.translated_code;
        } else {
            targetCode.value = `Error: ${result.error}`;
        }
    });
});