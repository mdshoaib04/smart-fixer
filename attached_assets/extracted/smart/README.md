# Smart Code Reviewer

This is a web-based application that uses AI to review, explain, and compile code. It features a modern, responsive UI with a variety of features to enhance the coding and learning experience.

## Features

- **AI-Powered Code Analysis:** Get instant feedback on your code's quality, efficiency, and correctness.
- **Code Explanation:** Understand complex code snippets with AI-generated explanations.
- **Multi-Language Support:** Works with a wide range of programming languages.
- **User Authentication:** Secure login and signup with Google and GitHub.
- **Interactive Editor:** A VS Code-style editor with syntax highlighting and shortcuts.
- **And much more...**

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/smart-code-reviewer.git
   cd smart-code-reviewer
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1.  **Create a `.env` file and set your Gemini API Key:**
    Create a file named `.env` in the root directory of the project (`c:\Users\Admin\Desktop\smart`) with the following content:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```
    Replace `YOUR_GEMINI_API_KEY` with your actual API key obtained from Google AI Studio.

2.  **Start the backend server:**
    ```bash
    python backend/app.py
    ```

3.  **Open your browser and navigate to:**
    ```
    http://127.0.0.1:5000
    ```

## Project Structure

-   `backend/`: Contains the Python Flask application and API endpoints.
-   `frontend/`: Contains the HTML, CSS, and JavaScript for the user interface.
-   `requirements.txt`: Lists the Python dependencies for the project.
-   `README.md`: This file.