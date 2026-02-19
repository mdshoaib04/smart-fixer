/**
 * Activity Tracker for SmartFixer
 * Tracks user activity and sends heartbeat to server every minute.
 */

class ActivityTracker {
    constructor() {
        this.isActive = true;
        this.lastActivityTime = Date.now();
        this.checkInterval = 1000;
        this.heartbeatInterval = 60000;
        this.idleThreshold = 120000;
        this.accumulatedTime = 0;

        this.init();
    }

    init() {
        const activities = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart'];
        activities.forEach(event => {
            document.addEventListener(event, () => this.resetIdleTimer(), true);
        });

        setInterval(() => this.track(), this.checkInterval);
        setInterval(() => this.sendHeartbeat(), this.heartbeatInterval);

        console.log('Activity Tracker started');
    }

    resetIdleTimer() {
        this.isActive = true;
        this.lastActivityTime = Date.now();
    }

    track() {
        const now = Date.now();
        if (now - this.lastActivityTime > this.idleThreshold) {
            this.isActive = false;
        }

        if (this.isActive) {
            this.accumulatedTime += this.checkInterval;
        }
    }

    async sendHeartbeat() {
        if (this.accumulatedTime > 0) {
            const timeToSend = Math.floor(this.accumulatedTime / 1000); // seconds
            this.accumulatedTime = 0;

            try {
                // Check if we are on profile page where time_tracking.js handles this
                if (window.location.pathname.includes('/profile')) {
                    // Let time_tracking.js handle it to avoid double counting if possible
                    // But for safety, we can send it as 'seconds'
                }

                await fetch('/api/track-time', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ seconds: timeToSend }) // Changed from duration to seconds
                });
            } catch (error) {
                console.error('Failed to track time', error);
            }
        }
    }

    startSessionTimer() {
        const SESSION_KEY = 'smartfixer_session_start';
        let startTime = sessionStorage.getItem(SESSION_KEY);

        if (!startTime) {
            startTime = Date.now();
            sessionStorage.setItem(SESSION_KEY, startTime);
        }

        setInterval(() => {
            const now = Date.now();
            const diff = now - parseInt(startTime);
            const totalSeconds = Math.floor(diff / 1000);

            // STRICT hh:mm:ss format
            const h = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
            const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
            const s = String(totalSeconds % 60).padStart(2, '0');
            const timeString = `${h}:${m}:${s}`;

            const timerEl = document.getElementById('session-timer-display');
            if (timerEl) {
                // Only update if it's not the profile page OR if we want unified format
                timerEl.textContent = timeString;
            }
        }, 1000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.activityTracker = new ActivityTracker();
    if (window.activityTracker) {
        window.activityTracker.startSessionTimer();
    }
});
