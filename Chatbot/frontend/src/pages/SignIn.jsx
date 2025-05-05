import React, { useState, useEffect } from "react";
import "../styles/register.css";
import logo from "../assets/logo.png";

const GLOBAL_IP = 'http://localhost:5001';

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [isValid, setIsValid] = useState(false);

  const validate = () => {
    const newErrors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(formData.email)) newErrors.email = "Enter a valid email.";
    if (formData.password.length < 6) newErrors.password = "Password must be at least 6 characters.";
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Passwords do not match.";

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

      const res = await fetch(`${GLOBAL_IP}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
  
      const result = await res.json();
  
      if (result.success) {
        alert("Registration successful!");
        const userId = result.userid;
        console.log("userid in signin", userId);

  
        //store email & name
        localStorage.setItem("useremail", formData.email);
        localStorage.setItem("userid", userId);
        window.location.href = "/profile"; //?userid=${userId}
  
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
