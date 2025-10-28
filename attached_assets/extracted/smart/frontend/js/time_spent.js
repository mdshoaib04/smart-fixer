document.addEventListener('DOMContentLoaded', async () => {
    const timeSpentDataContainer = document.getElementById('time-spent-data');

    async function fetchTimeSpentData() {
        try {
            const response = await fetch('/api/time_spent');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            displayTimeSpentData(data);
        } catch (error) {
            console.error('Error fetching time spent data:', error);
            timeSpentDataContainer.innerHTML = '<p>Error loading time spent data. Please try again later.</p>';
        }
    }

    function displayTimeSpentData(data) {
        timeSpentDataContainer.innerHTML = ''; // Clear loading message
        if (data.length === 0) {
            timeSpentDataContainer.innerHTML = '<p>No time spent data available yet.</p>';
            return;
        }

        const ul = document.createElement('ul');
        data.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `Feature: ${item.feature}, Duration: ${item.duration_seconds} seconds, Date: ${item.date}`;
            ul.appendChild(li);
        });
        timeSpentDataContainer.appendChild(ul);
    }

    fetchTimeSpentData();
});