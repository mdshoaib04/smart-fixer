// Frontend JavaScript for Smart Code Reviewer

document.addEventListener('DOMContentLoaded', () => {
    console.log('script.js loaded and DOMContentLoaded event fired.');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const showSignupLink = document.getElementById('show-signup');
    const showLoginLink = document.getElementById('show-login');

    showSignupLink.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Showing signup form');
        loginForm.classList.remove('active');
        signupForm.classList.add('active');
        console.log('loginForm active after click:', loginForm.classList.contains('active'));
        console.log('signupForm active after click:', signupForm.classList.contains('active'));
    });

    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Showing login form');
        signupForm.classList.remove('active');
        loginForm.classList.add('active');
        console.log('loginForm active after click:', loginForm.classList.contains('active'));
        console.log('signupForm active after click:', signupForm.classList.contains('active'));
    });

    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const targetId = toggle.dataset.target;
            const passwordInput = document.getElementById(targetId);
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggle.textContent = '🙈'; // Eye-slash icon
            } else {
                passwordInput.type = 'password';
                toggle.textContent = '👁️'; // Eye icon
            }
        });
    });

    // Handle Login
    loginForm.querySelector('button[type="submit"]').addEventListener('click', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message);
                window.location.href = '/main'; // Redirect to main page on successful login
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during login.');
        }
    });

    // Handle Signup
    signupForm.querySelector('button[type="submit"]').addEventListener('click', async (e) => {
        e.preventDefault();
        const username = document.getElementById('signup-username').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-confirm-password').value;

        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message);
                signupForm.classList.remove('active');
                loginForm.classList.add('active');
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during signup.');
        }
    });

    // Handle Google Signup
    document.querySelector('.google-signup').addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/login/google';
    });

    // Handle GitHub Signup
    document.querySelector('.github-signup').addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/login/github';
    });
});