document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registration-form");
    const submitButton = document.getElementById("submit-btn");

    const firstName = document.getElementById("first-name");
    const lastName = document.getElementById("last-name");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirm-password");
    const age = document.getElementById("age");

    // Error message elements
    const errors = {
        "first-name": document.getElementById("first-name-error"),
        "last-name": document.getElementById("last-name-error"),
        "email": document.getElementById("email-error"),
        "password": document.getElementById("password-error"),
        "confirm-password": document.getElementById("confirm-password-error"),
        "age": document.getElementById("age-error"),
    };

    function validateForm() {
        let isValid = true;

        // First Name & Last Name Validation
        const nameRegex = /^[A-Za-z\s]+$/;
        if (!nameRegex.test(firstName.value.trim())) {
            errors["first-name"].innerText = "Only letters allowed.";
            isValid = false;
        } else {
            errors["first-name"].innerText = "";
        }

        if (!nameRegex.test(lastName.value.trim())) {
            errors["last-name"].innerText = "Only letters allowed.";
            isValid = false;
        } else {
            errors["last-name"].innerText = "";
        }

        // Email Validation
        const emailRegex = /^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$/;
        if (!emailRegex.test(email.value.trim())) {
            errors["email"].innerText = "Invalid email format.";
            isValid = false;
        } else {
            errors["email"].innerText = "";
        }

        // Password Validation
        const passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$/;
        if (!passwordRegex.test(password.value)) {
            errors["password"].innerText = "At least 8 chars, 1 uppercase, 1 number, 1 symbol.";
            isValid = false;
        } else {
            errors["password"].innerText = "";
        }

        if (password.value !== confirmPassword.value) {
            errors["confirm-password"].innerText = "Passwords do not match.";
            isValid = false;
        } else {
            errors["confirm-password"].innerText = "";
        }

        // Age Validation
        const ageValue = parseInt(age.value, 10);
        if (isNaN(ageValue) || ageValue < 18 || ageValue > 35) {
            errors["age"].innerText = "Age must be between 18 and 35.";
            isValid = false;
        } else {
            errors["age"].innerText = "";
        }

        // Enable or disable submit button
        submitButton.disabled = !isValid;
    }

    // Event Listeners
    [firstName, lastName, email, password, confirmPassword, age].forEach((field) => {
        field.addEventListener("input", validateForm);
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        if (!submitButton.disabled) {
            alert("Form submitted successfully!");
            form.submit();
        }
    });
});
