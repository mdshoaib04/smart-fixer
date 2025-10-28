document.addEventListener('DOMContentLoaded', () => {
    const languageSelect = document.getElementById('language-select');
    const searchTermInput = document.getElementById('search-term');
    const searchBtn = document.getElementById('search-btn');
    const addEntryBtn = document.getElementById('add-entry-btn');
    const dictionaryList = document.getElementById('dictionary-list');
    const entryModal = document.getElementById('entry-modal');
    const closeModalBtn = entryModal.querySelector('.close-button');
    const modalTitle = document.getElementById('modal-title');
    const entryIdInput = document.getElementById('entry-id');
    const modalLanguageSelect = document.getElementById('modal-language');
    const modalTermInput = document.getElementById('modal-term');
    const modalDefinitionTextarea = document.getElementById('modal-definition');
    const saveEntryBtn = document.getElementById('save-entry-btn');

    let currentEntries = [];

    // Function to fetch and display dictionary entries
    async function fetchAndDisplayEntries() {
        const selectedLanguage = languageSelect.value;
        try {
            const response = await fetch(`/api/dictionary/${selectedLanguage}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            currentEntries = await response.json();
            renderDictionaryEntries(currentEntries);
        } catch (error) {
            console.error('Error fetching dictionary entries:', error);
            dictionaryList.innerHTML = `<p>Error loading dictionary entries: ${error.message}</p>`;
        }
    }

    // Function to render dictionary entries
    function renderDictionaryEntries(entries) {
        dictionaryList.innerHTML = '';
        if (entries.length === 0) {
            dictionaryList.innerHTML = '<p>No entries found for this language.</p>';
            return;
        }
        entries.forEach(entry => {
            const entryDiv = document.createElement('div');
            entryDiv.classList.add('dictionary-entry');
            entryDiv.innerHTML = `
                <h3>${entry.term}</h3>
                <p>${entry.definition}</p>
                <div class="entry-actions">
                    <button class="edit-entry-btn" data-id="${entry.id}">Edit</button>
                    <button class="delete-entry-btn" data-id="${entry.id}">Delete</button>
                </div>
            `;
            dictionaryList.appendChild(entryDiv);
        });

        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-entry-btn').forEach(button => {
            button.addEventListener('click', (e) => openEditModal(e.target.dataset.id));
        });
        document.querySelectorAll('.delete-entry-btn').forEach(button => {
            button.addEventListener('click', (e) => deleteEntry(e.target.dataset.id));
        });
    }

    // Open Add Entry Modal
    addEntryBtn.addEventListener('click', () => {
        modalTitle.textContent = 'Add Dictionary Entry';
        entryIdInput.value = '';
        modalLanguageSelect.value = languageSelect.value; // Pre-select current language
        modalTermInput.value = '';
        modalDefinitionTextarea.value = '';
        entryModal.style.display = 'block';
    });

    // Open Edit Entry Modal
    function openEditModal(id) {
        const entry = currentEntries.find(e => e.id == id);
        if (entry) {
            modalTitle.textContent = 'Edit Dictionary Entry';
            entryIdInput.value = entry.id;
            modalLanguageSelect.value = entry.language;
            modalTermInput.value = entry.term;
            modalDefinitionTextarea.value = entry.definition;
            entryModal.style.display = 'block';
        }
    }

    // Close Modal
    closeModalBtn.addEventListener('click', () => {
        entryModal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === entryModal) {
            entryModal.style.display = 'none';
        }
    });

    // Save Entry (Add or Update)
    saveEntryBtn.addEventListener('click', async () => {
        const id = entryIdInput.value;
        const language = modalLanguageSelect.value;
        const term = modalTermInput.value;
        const definition = modalDefinitionTextarea.value;

        if (!term || !definition) {
            alert('Term and Definition cannot be empty.');
            return;
        }

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/dictionary/${id}` : '/api/dictionary';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language, term, definition })
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                entryModal.style.display = 'none';
                fetchAndDisplayEntries(); // Refresh list
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error saving entry:', error);
            alert('An error occurred while saving the entry.');
        }
    });

    // Delete Entry
    async function deleteEntry(id) {
        if (!confirm('Are you sure you want to delete this entry?')) {
            return;
        }
        try {
            const response = await fetch(`/api/dictionary/${id}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchAndDisplayEntries(); // Refresh list
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error deleting entry:', error);
            alert('An error occurred while deleting the entry.');
        }
    }

    // Event listeners for language select and search
    languageSelect.addEventListener('change', fetchAndDisplayEntries);
    searchBtn.addEventListener('click', () => {
        const searchTerm = searchTermInput.value.toLowerCase();
        const filteredEntries = currentEntries.filter(entry =>
            entry.term.toLowerCase().includes(searchTerm) ||
            entry.definition.toLowerCase().includes(searchTerm)
        );
        renderDictionaryEntries(filteredEntries);
    });

    // Initial load
    fetchAndDisplayEntries();
});