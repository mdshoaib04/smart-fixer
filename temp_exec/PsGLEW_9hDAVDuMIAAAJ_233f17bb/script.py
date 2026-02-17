<!DOCTYPE html>
<html>
<head>
    <title>Greeting Page</title>
    <style>
        body {
            background-color: #f0f8ff; /* light blue background */
            text-align: center;
            font-family: Arial, sans-serif;
        }
        h1 {
            color: #ff4500; /* orange-red text */
            cursor: pointer;
            transition: transform 0.3s, color 0.3s;
        }
        h1:hover {
            color: #008000; /* green on hover */
            transform: scale(1.2);
        }
    </style>
</head>
<body>
    <h1 onclick="sayWelcome()">Hey Shoaib</h1>

    <script>
        function sayWelcome() {
            alert("Welcome Shoaib!");
            // Redirect to a new page (example: Google)
            window.location.href = "https://www.google.com";
        }
    </script>
</body>
</html>
