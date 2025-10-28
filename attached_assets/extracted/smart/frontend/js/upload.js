document.addEventListener('DOMContentLoaded', () => {
    const uploadCard = document.getElementById('upload-card');
    const writeCard = document.getElementById('write-card');
    const fileInput = document.getElementById('file-input');

    // Trigger file input when upload card is clicked
    uploadCard.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            // Handle the file upload logic here
            console.log('File selected:', file.name);
            // For now, we'll just redirect to the main page
            window.location.href = '/main';
        }
    });

    // Redirect to main page when write card is clicked
    writeCard.addEventListener('click', () => {
        window.location.href = '/main';
    });
});