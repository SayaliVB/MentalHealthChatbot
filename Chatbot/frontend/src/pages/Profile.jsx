import React, { useState, useEffect } from "react";
import "../styles/register.css";
import logo from "../assets/logo.png";

const Profile = () => {

  // const userid = parseInt(params.get('userid'), 10);
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
      const res = await fetch("http://127.0.0.1:5000/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
  
      const result = await res.json();
  
      if (result.success) {
        alert("Profile Completed!");
  
        window.location.href = "/login";
      } else {
        alert(result.message || "Profile failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }
  };
  

  return (
    <div className="profile-container">
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

        <div className="name-container">
          <div className="input-group">
            <label>Age:</label>
            <input name="age" type="number" onChange={handleChange} min="18" max="35" required />
            <span className="error-message">{errors.age}</span>
          </div>
          <div className="input-group">
            <label>Gender:</label>
            <input name="gender" type="text" onChange={handleChange} required />
            <span className="error-message">{errors.gender}</span>
          </div>
        </div>

        <label>Cultural Background:</label>
        <input name="culture" type="text" onChange={handleChange} />

        <label>Any history of mental problems?:</label>
        <input name="history" type="text" onChange={handleChange} />

        <button type="submit" className="signup-btn" disabled={!isValid}>
          Complete Profile
        </button>

      </form>
    </div>
  );
};

export default Profile;
