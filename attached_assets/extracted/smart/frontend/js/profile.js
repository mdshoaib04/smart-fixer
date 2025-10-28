document.addEventListener('DOMContentLoaded', () => {
    const profileName = document.getElementById('profile-name');
    const profileEmail = document.getElementById('profile-email');
    const profileBio = document.getElementById('profile-bio');
    const profilePostsCount = document.getElementById('profile-posts-count');
    const profileFriendsCount = document.getElementById('profile-friends-count');

    // Function to fetch user profile data from backend
    async function fetchUserProfile() {
        const userId = 1; // Placeholder for actual logged-in user ID
        try {
            const response = await fetch(`/api/user/${userId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const userData = await response.json();
            profileName.innerText = userData.name;
            profileEmail.innerText = userData.email;
            profileBio.innerText = userData.bio;
            profilePostsCount.innerText = userData.posts_count;
            profileFriendsCount.innerText = userData.friends_count;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            profileName.innerText = 'Error loading profile';
            profileEmail.innerText = '';
            profileBio.innerText = '';
            profilePostsCount.innerText = 'N/A';
            profileFriendsCount.innerText = 'N/A';
        }
    }

    fetchUserProfile();

    // Event listeners for profile sections
    document.getElementById('view-posts-btn').addEventListener('click', () => {
        window.open('/posts', '_blank');
    });

    document.getElementById('view-friends-btn').addEventListener('click', () => {
        window.open('/chat', '_blank'); // Assuming chat page will show friends
    });

    document.getElementById('view-notifications-btn').addEventListener('click', () => {
        window.open('/notifications', '_blank');
    });

    document.getElementById('view-time-spent-btn').addEventListener('click', () => {
        window.open('/time_spent', '_blank');
    });
});