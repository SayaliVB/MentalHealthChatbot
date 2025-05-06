import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/login.css";
import logo from "../assets/logo.png";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const GLOBAL_IP = 'http://localhost:5001';

  const handleLogin = async (e) => {
    e.preventDefault();
  
    if (!email || !password) {
      alert("Email and password are required.");
      return;
    }
  
    setIsSubmitting(true);
  
    try {
      const response = await fetch(`${GLOBAL_IP}/verify_login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      const result = await response.json();
      console.log("Login result:", result); 
  
      if (response.ok && result.success && result.user) {
        localStorage.setItem("userId", result.user.id);
        localStorage.setItem("username", result.user.firstname);
        localStorage.setItem("useremail", result.user.email);
        localStorage.setItem("culture", result.user.culture);   
             
        alert("Login Successful!");
        navigate("/dashboard");
      } else {
        alert(result.error || "Login failed. Please check your credentials.");
      }
  
    } catch (error) {
      console.error("Login error:", error);
      alert("Something went wrong. Try again later.");
    } finally {
      setIsSubmitting(false);
    }
  };  

  return (
    <div className="login-container">
      <div className="logo">
        <img src={logo} alt="Empower Mental Health Logo" />
      </div>
      <h2>Empower Mental Health</h2>
      <form onSubmit={handleLogin}>
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <a href="#" className="forgot-password">
          Forgot Password?
        </a>

        <button type="submit" className="login-btn" disabled={isSubmitting}>
          {isSubmitting ? "Logging in..." : "Login"}
        </button>

        <p>
          Don't have an account? <a href="/signin">Sign Up</a>
        </p>
      </form>
    </div>
  );
};

export default Login;
