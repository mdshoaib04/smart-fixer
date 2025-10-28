// Time Tracker JavaScript - Complete Implementation

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const themeToggle = document.querySelector('.theme-toggle');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        themeToggle.innerHTML = '🌞';
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        themeToggle.innerHTML = '🌙';
    }
}

// Initialize the time tracker
document.addEventListener('DOMContentLoaded', function() {
    // Update statistics
    updateStatistics();
    
    // Generate heatmap
    generateHeatmap();
    
    // Set up event listeners for settings
    setupSettingsListeners();
    
    // Add event listener for dropdown toggle
    setupDropdownToggle();
});

function updateStatistics() {
    // Simulate data fetching - in a real app, this would come from an API
    const todayHrs = Math.floor(Math.random() * 24);
    const weekHrs = Math.floor(Math.random() * 100);
    const monthHrs = Math.floor(Math.random() * 1000);
    
    document.getElementById('today-hrs').textContent = todayHrs;
    document.getElementById('week-hrs').textContent = weekHrs;
    document.getElementById('month-hrs').textContent = monthHrs;
    
    // Update activity section
    const totalHours = todayHrs + weekHrs + monthHrs;
    const currentYear = new Date().getFullYear();
    document.getElementById('total-time-spent').textContent = `${totalHours} hrs spent in ${currentYear}`;
}

function generateHeatmap() {
    const grid = document.querySelector('.heatmap-grid');
    const months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];
    const weekdays = ['Mon', 'Wed', 'Fri'];
    
    // Generate cells for each day
    for (let i = 0; i < 12; i++) { // 12 months
        for (let j = 0; j < 3; j++) { // 3 weekdays
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            
            // Simulate random hours for demonstration
            const hours = Math.floor(Math.random() * 8);
            cell.dataset.hours = hours;
            
            // Apply color based on hours
            if (hours === 0) {
                cell.classList.add('zero');
            } else if (hours <= 2) {
                cell.classList.add('light');
            } else if (hours <= 4) {
                cell.classList.add('medium');
            } else if (hours <= 6) {
                cell.classList.add('dark');
            } else {
                cell.classList.add('darkest');
            }
            
            // Add hover tooltip
            cell.title = `Hours: ${hours}`;
            
            grid.appendChild(cell);
        }
    }
    
    // Update longest and current streaks
    updateStreaks();
}

function updateStreaks() {
    // Simulate streak calculation
    const longestStreak = Math.floor(Math.random() * 30);
    const currentStreak = Math.floor(Math.random() * 7);
    
    document.getElementById('longest-streak').textContent = `${longestStreak} days`;
    document.getElementById('current-streak').textContent = `${currentStreak} days`;
}

function setupSettingsListeners() {
    // Toggle friend comparison
    document.getElementById('compare-friend').addEventListener('change', function() {
        const compareFriend = document.getElementById('compare-friend').checked;
        const heatmapContainer = document.querySelector('.heatmap-container');
        
        if (compareFriend) {
            // Add second graph here
            const secondGraph = document.createElement('div');
            secondGraph.className = 'heatmap-container second-graph';
            secondGraph.innerHTML = `
                <div class="month-labels">
                    <span>Oct</span><span>Nov</span><span>Dec</span><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span><span>Aug</span><span>Sep</span>
                </div>
                <div class="weekday-labels">
                    <span>Mon</span><span>Wed</span><span>Fri</span>
                </div>
                <div class="heatmap-grid">
                    <!-- Second graph cells -->
                </div>
            `;
            heatmapContainer.appendChild(secondGraph);
            
            // Generate cells for second graph
            const secondGrid = secondGraph.querySelector('.heatmap-grid');
            for (let i = 0; i < 12; i++) { // 12 months
                for (let j = 0; j < 3; j++) { // 3 weekdays
                    const cell = document.createElement('div');
                    cell.className = 'heatmap-cell';
                    
                    // Simulate random hours for demonstration
                    const hours = Math.floor(Math.random() * 8);
                    cell.dataset.hours = hours;
                    
                    // Apply color based on hours
                    if (hours === 0) {
                        cell.classList.add('zero');
                    } else if (hours <= 2) {
                        cell.classList.add('light');
                    } else if (hours <= 4) {
                        cell.classList.add('medium');
                    } else if (hours <= 6) {
                        cell.classList.add('dark');
                    } else {
                        cell.classList.add('darkest');
                    }
                    
                    // Add hover tooltip
                    cell.title = `Hours: ${hours}`;
                    
                    secondGrid.appendChild(cell);
                }
            }
        } else {
            const secondGraph = document.querySelector('.second-graph');
            if (secondGraph) {
                secondGraph.remove();
            }
        }
    });
    
    // Toggle weekly average
    document.getElementById('show-weekly-average').addEventListener('change', function() {
        const showAverage = document.getElementById('show-weekly-average').checked;
        const avgLabel = document.createElement('div');
        avgLabel.className = 'weekly-average-label';
        avgLabel.textContent = 'Average Time per Week: 29 hrs';
        
        if (showAverage) {
            const heatmapGrid = document.querySelector('.heatmap-grid');
            heatmapGrid.parentNode.insertBefore(avgLabel, heatmapGrid.nextSibling);
        } else {
            const avgLabelElement = document.querySelector('.weekly-average-label');
            if (avgLabelElement) {
                avgLabelElement.remove();
            }
        }
    });
    
    // Toggle longest streak
    document.getElementById('show-longest-streak').addEventListener('change', function() {
        const showStreak = document.getElementById('show-longest-streak').checked;
        const cells = document.querySelectorAll('.heatmap-cell');
        
        if (showStreak) {
            // Find longest streak of consecutive non-zero days
            let maxStreak = 0;
            let currentStreak = 0;
            let maxStart = 0;
            let maxEnd = 0;
            
            cells.forEach((cell, index) => {
                const hours = parseInt(cell.dataset.hours);
                if (hours > 0) {
                    currentStreak++;
                    if (currentStreak > maxStreak) {
                        maxStreak = currentStreak;
                        maxStart = index - currentStreak + 1;
                        maxEnd = index;
                    }
                } else {
                    currentStreak = 0;
                }
            });
            
            // Highlight the longest streak
            for (let i = maxStart; i <= maxEnd; i++) {
                cells[i].classList.add('longest-streak');
            }
        } else {
            // Remove highlights
            cells.forEach(cell => {
                cell.classList.remove('longest-streak');
            });
        }
    });
    
    // Toggle active days
    document.getElementById('highlight-active-days').addEventListener('change', function() {
        const highlightActive = document.getElementById('highlight-active-days').checked;
        const cells = document.querySelectorAll('.heatmap-cell');
        
        if (highlightActive) {
            // Find top 10% of days by hours
            const hoursArray = Array.from(cells).map(cell => parseInt(cell.dataset.hours));
            hoursArray.sort((a, b) => b - a);
            const threshold = hoursArray[Math.floor(hoursArray.length * 0.1)];
            
            cells.forEach(cell => {
                const hours = parseInt(cell.dataset.hours);
                if (hours >= threshold && hours > 0) {
                    cell.classList.add('active-day');
                }
            });
        } else {
            // Remove highlights
            cells.forEach(cell => {
                cell.classList.remove('active-day');
            });
        }
    });
    
    // Toggle monthly stats
    document.getElementById('show-monthly-stats').addEventListener('change', function() {
        const showStats = document.getElementById('show-monthly-stats').checked;
        const activitySection = document.querySelector('.activity-info');
        
        if (showStats) {
            const summaryCard = document.createElement('div');
            summaryCard.className = 'monthly-summary-card';
            summaryCard.innerHTML = `
                <div class="summary-item">
                    <span>📅 Month:</span>
                    <span>October</span>
                </div>
                <div class="summary-item">
                    <span>🟩 Total Time:</span>
                    <span>123 hrs</span>
                </div>
                <div class="summary-item">
                    <span>🔥 Current Streak:</span>
                    <span>6 days</span>
                </div>
                <div class="summary-item">
                    <span>📈 Avg per Week:</span>
                    <span>29 hrs</span>
                </div>
            `;
            activitySection.appendChild(summaryCard);
        } else {
            const summaryCard = document.querySelector('.monthly-summary-card');
            if (summaryCard) {
                summaryCard.remove();
            }
        }
    });
}

function setupDropdownToggle() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownContent = document.querySelector('.dropdown-content');
    
    dropdownToggle.addEventListener('click', function() {
        dropdownContent.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    window.addEventListener('click', function(event) {
        if (!event.target.matches('.dropdown-toggle') && !event.target.closest('.dropdown-content')) {
            dropdownContent.classList.remove('show');
        }
    });
}