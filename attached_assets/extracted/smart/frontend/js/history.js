document.addEventListener('DOMContentLoaded', () => {
    const snippetsContainer = document.getElementById('snippets-container');

    async function fetchSnippets() {
        try {
            const response = await fetch('/snippets');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const snippets = await response.json();
            displaySnippets(snippets);
        } catch (error) {
            console.error('Error fetching snippets:', error);
            snippetsContainer.innerHTML = '<p>Error loading snippets. Please try again later.</p>';
        }
    }

    async function displaySnippets(snippets) {
        snippetsContainer.innerHTML = '';
        if (snippets.length === 0) {
            snippetsContainer.innerHTML = '<p>No snippets saved yet. Start coding!</p>';
            return;
        }

        for (const snippet of snippets) {
            const snippetCard = document.createElement('div');
            snippetCard.classList.add('snippet-card');
            snippetCard.innerHTML = `
                <h3>${snippet.title}</h3>
                <p>Language: ${snippet.language}</p>
                <p>Created: ${new Date(snippet.created_at).toLocaleDateString()}</p>
                <button class="view-history-btn" data-snippet-id="${snippet.id}">View History</button>
            `;
            snippetsContainer.appendChild(snippetCard);
        }

        snippetsContainer.querySelectorAll('.view-history-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                const snippetId = e.target.dataset.snippetId;
                try {
                    const response = await fetch(`/snippets/${snippetId}/versions`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const versions = await response.json();
                    console.log(`Versions for snippet ID ${snippetId}:`, versions);
                    alert(`Check console for versions of snippet ID: ${snippetId}`);
                    // Here you would typically open a modal or navigate to a detailed view
                } catch (error) {
                    console.error(`Error fetching versions for snippet ${snippetId}:`, error);
                    alert('Error loading snippet versions.');
                }
            });
        });
    }

    fetchSnippets();
});