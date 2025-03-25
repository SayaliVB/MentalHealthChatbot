import React, { useState, useEffect } from "react";
import "../styles/register.css";
import logo from "../assets/logo.png";

const SignIn = () => {
  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    email: "",
    password: "",
    confirmPassword: "",
    age: "",
  });

  const [errors, setErrors] = useState({});
  const [isValid, setIsValid] = useState(false);

  const validate = () => {
    const newErrors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formData.firstname.trim()) newErrors.firstname = "First name is required.";
    if (!formData.lastname.trim()) newErrors.lastname = "Last name is required.";
    if (!emailRegex.test(formData.email)) newErrors.email = "Enter a valid email.";
    if (formData.password.length < 6) newErrors.password = "Password must be at least 6 characters.";
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords do not match.";
    if (formData.age < 18 || formData.age > 35) newErrors.age = "Age must be between 18 and 35.";

    setErrors(newErrors);
    setIsValid(Object.keys(newErrors).length === 0);
  };

  useEffect(() => {
    validate();
  }, [formData]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    try {
      const res = await fetch("http://localhost:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
  
      const result = await res.json();
  
      if (result.success) {
        alert("Registration successful!");
  
        //store email & name
        localStorage.setItem("useremail", formData.email);
        localStorage.setItem("username", formData.firstname);
  
        window.location.href = "/login";
      } else {
        alert(result.message || "Registration failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }
  };
  

  return (
    <div className="signup-container">
      <div className="logo">
        <img src={logo} alt="Logo" />
      </div>
      <h2>Get Started Now!</h2>
      <form id="registration-form" onSubmit={handleSubmit}>
        <div className="name-container">
          <div className="input-group">
            <label>First Name:</label>
            <input name="firstname" type="text" onChange={handleChange} required />
            <span className="error-message">{errors.firstname}</span>
          </div>
          <div className="input-group">
            <label>Last Name:</label>
            <input name="lastname" type="text" onChange={handleChange} required />
            <span className="error-message">{errors.lastname}</span>
          </div>
        </div>

        <label>Email:</label>
        <input name="email" type="email" onChange={handleChange} required />
        <span className="error-message">{errors.email}</span>

        <div className="password-container">
          <div className="input-group">
            <label>Password:</label>
            <input name="password" type="password" onChange={handleChange} required />
            <span className="error-message">{errors.password}</span>
          </div>
          <div className="input-group">
            <label>Confirm Password:</label>
            <input name="confirmPassword" type="password" onChange={handleChange} required />
            <span className="error-message">{errors.confirmPassword}</span>
          </div>
        </div>

        <label>Age:</label>
        <input name="age" type="number" onChange={handleChange} min="18" max="35" required />
        <span className="error-message">{errors.age}</span>

        <button type="submit" className="signup-btn" disabled={!isValid}>
          Sign Up
        </button>

        <p>Already Have An Account? <a href="/login">Login</a></p>

        {/* <div className="divider">OR</div>

        <button type="button" className="google-btn">
          <img src="/images/google.png" alt="Google" />
        </button> */}
      </form>
    </div>
  );
};

export default SignIn;
