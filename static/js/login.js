document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector("form");
    const loginButton = document.querySelector(".login-btn");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault(); 

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!email || !password) {
            alert("Email and password are required.");
            return;
        }

        loginButton.disabled = true; 

        const loginData = { email, password };

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(loginData),
            });

            const result = await response.json();

            if (response.ok) {
                alert("Login Successful!");
                window.location.href = "/open-streamlit"; // Redirect to the chatbot
            } else {
                alert(result.error || "Login failed, please try again.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again later.");
        } finally {
            loginButton.disabled = false; // Re-enable button
        }
    });
});
