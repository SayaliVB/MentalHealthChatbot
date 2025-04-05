document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registration-form");
    const firstName = document.getElementById("first-name");
    const lastName = document.getElementById("last-name");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm-password");
    const age = document.getElementById("age");
    const submitBtn = document.getElementById("submit-btn");

    const errorMessages = {
        firstName: document.getElementById("first-name-error"),
        lastName: document.getElementById("last-name-error"),
        email: document.getElementById("email-error"),
        password: document.getElementById("password-error"),
        confirmPassword: document.getElementById("confirm-password-error"),
        age: document.getElementById("age-error"),
    };

    function validateInputs() {
        let isValid = true;

        // First Name Validation
        if (firstName.value.trim() === "") {
            errorMessages.firstName.textContent = "First name is required.";
            isValid = false;
        } else {
            errorMessages.firstName.textContent = "";
        }

        // Last Name Validation
        if (lastName.value.trim() === "") {
            errorMessages.lastName.textContent = "Last name is required.";
            isValid = false;
        } else {
            errorMessages.lastName.textContent = "";
        }

        // Email Validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            errorMessages.email.textContent = "Enter a valid email.";
            isValid = false;
        } else {
            errorMessages.email.textContent = "";
        }

        // Password Validation
        if (password.value.length < 6) {
            errorMessages.password.textContent = "Password must be at least 6 characters.";
            isValid = false;
        } else {
            errorMessages.password.textContent = "";
        }

        // Confirm Password Validation
        if (password.value !== confirmPassword.value) {
            errorMessages.confirmPassword.textContent = "Passwords do not match.";
            isValid = false;
        } else {
            errorMessages.confirmPassword.textContent = "";
        }

        // Age Validation
        if (age.value < 18 || age.value > 35) {
            errorMessages.age.textContent = "Age must be between 18 and 35.";
            isValid = false;
        } else {
            errorMessages.age.textContent = "";
        }

        submitBtn.disabled = !isValid;
    }

    // Attach input event listeners for real-time validation
    [firstName, lastName, email, password, confirmPassword, age].forEach((input) => {
        input.addEventListener("input", validateInputs);
    });

    // Submit form via Fetch API
    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const formData = {
            firstname: firstName.value.trim(),
            lastname: lastName.value.trim(),
            email: email.value.trim(),
            password: password.value.trim(),
            confirmPassword: confirmPassword.value.trim(),
            age: age.value.trim(),
        };

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();
            
            if (result.success) {
                alert("Registration successful! Redirecting to login...");
                window.location.href = "/login";
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error("Error submitting form:", error);
            alert("Something went wrong. Please try again.");
        }
    });
});
