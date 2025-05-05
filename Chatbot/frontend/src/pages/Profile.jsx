import React, { useState, useEffect } from "react";
import "../styles/Profile.css";
import logo from "../assets/logo.png";

const GLOBAL_IP = 'http://localhost:5001';

const Profile = () => {
  const userId = parseInt(localStorage.getItem('userid'), 10);
  console.log("userid in profile", userId);

  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    age: "",
    gender: "",
    culture: "",
    history: "",
    userid: userId,
  });

  const [errors, setErrors] = useState({});
  const [isValid, setIsValid] = useState(false);

  const validate = () => {
    const newErrors = {};

    if (!formData.firstname.trim()) newErrors.firstname = "First name is required.";
    if (!formData.lastname.trim()) newErrors.lastname = "Last name is required.";
    if (!formData.gender.trim()) newErrors.gender = "Gender is required.";
    if (formData.age < 18 || formData.age > 35 || !formData.age) newErrors.age = "Age must be between 18 and 35.";

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
      const res = await fetch(`${GLOBAL_IP}/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const result = await res.json();

      if (result.success) {
        alert("Profile Completed Successfully!");
        window.location.href = "/login"; 
      } else {
        alert(result.message || "Profile creation failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="signup-container">
      <div className="logo">
        <img src={logo} alt="Logo" />
      </div>
      <h1>Get Started Now!</h1>

      <form onSubmit={handleSubmit}>
        <div className="name-container">
          <div className="input-group">
            <label>First Name:</label>
            <input 
              name="firstname" 
              type="text" 
              value={formData.firstname} 
              onChange={handleChange} 
              required 
            />
            {errors.firstname && <span className="error-message">{errors.firstname}</span>}
          </div>

          <div className="input-group">
            <label>Last Name:</label>
            <input 
              name="lastname" 
              type="text" 
              value={formData.lastname} 
              onChange={handleChange} 
              required 
            />
            {errors.lastname && <span className="error-message">{errors.lastname}</span>}
          </div>
        </div>

        <div className="age-gender-container">
          <div className="input-group">
            <label>Age:</label>
            <input 
              name="age" 
              type="number" 
              value={formData.age} 
              onChange={handleChange} 
              min="18" 
              max="35" 
              required 
            />
            {errors.age && <span className="error-message">{errors.age}</span>}
          </div>

          <div className="input-group">
          <label>Gender:</label>
          <select name="gender" onChange={handleChange} required>
            <option value="">Select Gender</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
            {errors.gender && <span className="error-message">{errors.gender}</span>}
          </div>
        </div>

        <div className="input-group full-width">
        <label>Cultural Background:</label>
        <select name="culture" onChange={handleChange}>
          <option value="">Select Country</option>
          <option value="India">India</option>
          <option value="Iran">Iran</option>
          <option value="China">China</option>
          <option value="United States">United States</option>
          <option value="Canada">Canada</option>
          <option value="Germany">Germany</option>
          <option value="Other">Other</option>
        </select>
        </div>

        <div className="input-group full-width">
          <label>Any history of mental problems?</label>
          <input 
            name="history" 
            type="text" 
            value={formData.history} 
            onChange={handleChange} 
          />
        </div>

        <button type="submit" className="signup-btn" disabled={!isValid}>
          Complete Profile
        </button>
      </form>
    </div>
  );
};

export default Profile;
