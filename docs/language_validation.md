# Real-time Language Validation Feature

## Overview
This feature provides real-time validation of code language when creating posts. When a user selects a language from the dropdown and writes code, the system automatically checks if the code matches the selected language and displays an error message if it doesn't.

## Implementation Details

### Frontend (posts.html)
1. Added an error message div below the code textarea
2. Implemented JavaScript functions for real-time validation:
   - `validateCodeLanguage()` - Calls the API to detect the language of the code
   - `showCodeError()` - Displays error messages
   - `clearCodeError()` - Clears error messages
   - `setupRealTimeValidation()` - Sets up event listeners for real-time validation
3. Added event listeners for:
   - Input events on the code textarea (with debouncing)
   - Change events on the language dropdown
4. Modified the `createPost()` function to prevent posting if there's a validation error

### Backend (routes.py)
1. The existing `/api/detect-language` endpoint is used for language detection
2. The endpoint uses AI-based language detection with fallback to keyword-based detection
3. Authentication is required for API access

### Styling (posts.css)
1. Added CSS rules for error message display
2. Error messages are displayed in red (#e74c3c) to match the theme

## How It Works
1. When a user opens the create post modal, real-time validation is initialized
2. As the user types in the code area, validation is triggered after 500ms of inactivity (debounced)
3. When the user changes the language selection, validation is triggered immediately
4. The system calls the `/api/detect-language` endpoint to detect the language of the code
5. If the detected language doesn't match the selected language (and the selected language is not "Other"), an error message is displayed
6. If the user tries to create a post while there's a validation error, they are prompted to fix it first

## Error Handling
- If the API call fails, no error is shown to the user to avoid confusion
- Validation is skipped if the code hasn't changed since the last validation
- Error messages are cleared when the modal is closed or when valid code is entered

## Edge Cases
- Empty code fields don't trigger validation
- The "Other" language option bypasses validation (allows any code)
- Validation is debounced to avoid excessive API calls