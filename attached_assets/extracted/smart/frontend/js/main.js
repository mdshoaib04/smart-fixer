document.addEventListener('DOMContentLoaded', () => {
    const codeEditorElement = document.getElementById('code-editor');

    // Initialize CodeMirror
    const editor = CodeMirror(codeEditorElement, {
        value: "def hello_world():\n    print('Hello, Smart Code Reviewer!')\n\nhello_world()",
        mode: 'python',
        theme: 'dracula',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
    });

    const outputContent = document.getElementById('output-content');

    // Display initial welcome message
    outputContent.textContent = "Welcome to the Smart Code Reviewer! Click a button on the left to get started.";

    const reviewBtn = document.getElementById('review-btn');
    const explainBtn = document.getElementById('explain-btn');
    const compileBtn = document.getElementById('compile-btn');
    const professionSelect = document.getElementById('profession');

    async function analyzeCode(action) {
        const code = editor.getValue();
        const profession = professionSelect.value;
        
        outputContent.textContent = "Analyzing...";

        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, action, profession })
        });

        const result = await response.json();
        if (response.ok) {
            outputContent.textContent = result.response;
        } else {
            console.error("Backend Error:", result.error); // Log error to console
            outputContent.textContent = `Error: ${result.error}`;
        }
    }

    reviewBtn.addEventListener('click', () => analyzeCode('review'));
    explainBtn.addEventListener('click', () => analyzeCode('explain'));
    compileBtn.addEventListener('click', () => analyzeCode('compile'));

    const qnaBtn = document.querySelector('.qna-search button');
    const qnaInput = document.querySelector('.qna-search input');

    async function handleQna() {
        const code = editor.getValue();
        const question = qnaInput.value;

        if (!question) {
            alert("Please enter a question.");
            return;
        }

        outputContent.textContent = "Thinking...";

        const response = await fetch('/qna', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, question })
        });

        const result = await response.json();
        if (response.ok) {
            outputContent.textContent = result.response;
        } else {
            console.error("Backend Error:", result.error); // Log error to console
            outputContent.textContent = `Error: ${result.error}`;
        }
        qnaInput.value = ''; // Clear the input
    }

    qnaBtn.addEventListener('click', handleQna);

    // Dropdown menu toggling
    const mainMenuToggle = document.getElementById('main-menu-toggle');
    const profileToggle = document.getElementById('profile-toggle');

    mainMenuToggle.addEventListener('click', () => {
        mainMenuToggle.parentNode.classList.toggle('active');
    });

    profileToggle.addEventListener('click', () => {
        profileToggle.parentNode.classList.toggle('active');
    });

    window.addEventListener('click', (event) => {
        if (!event.target.matches('.menu-btn') && !event.target.matches('.icon') && !event.target.matches('.icon-btn')) {
            const dropdowns = document.querySelectorAll('.menu-dropdown, .profile-menu');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    const saveSnippetBtn = document.getElementById('save-snippet-btn');
    saveSnippetBtn.addEventListener('click', async () => {
        const code = editor.getValue();
        const title = prompt("Enter a title for your snippet:");
        if (!title) return;

        // Placeholder for language detection
        const language = 'Python'; // This should be dynamically detected

        // For now, we'll assume the last AI output is the review
        const review_output = outputContent.innerText;

        try {
            const response = await fetch('/snippets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    language,
                    code_content: code,
                    review_output: review_output,
                    explain_output: "", // To be implemented
                    compile_output: "" // To be implemented
                })
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
            } else {
                alert(`Error saving snippet: ${result.message}`);
            }
        } catch (error) {
            console.error('Error saving snippet:', error);
            alert('An error occurred while saving the snippet.');
        }
    });
    
    const themeToggleBtn = document.getElementById('theme-toggle');
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        if (document.body.classList.contains('light-mode')) {
            localStorage.setItem('theme', 'light');
            themeToggleBtn.innerText = '☀️';
        } else {
            localStorage.setItem('theme', 'dark');
            themeToggleBtn.innerText = '🌙';
        }
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        themeToggleBtn.innerText = '☀️';
    } else {
        themeToggleBtn.innerText = '🌙';
    }
});