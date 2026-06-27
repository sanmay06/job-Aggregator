import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import './styles.css';
import FormInput from '../components/FormInput';
import api from "../API";

function SignIn() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [pass, setPass] = useState("");
    const [conPass, setConPass] = useState("");
    const [error, setError] = useState("");
    const [msg, setmsg] = useState("");

    async function SignUp(event) {
        event.preventDefault();
        if (pass !== conPass) {
            setError("Passwords do not match");
            return;
        }
        await api.post("/reg", {
            email: email.trim(),
            username: username.trim(),
            password: pass.trim()
        })
        .then(response => {
            setmsg("Created successfully");
            setTimeout(() => {
                navigate('/Sign In', { replace: true });
            }, 1500);
        })
        .catch(e => {
            console.log(e);
            setError("Registration failed. Please try again.");
        });
    }

    useEffect(() => {
        if (pass !== conPass)
            setError("Passwords do not match");
        else
            setError("");
    }, [conPass, pass])

    return (
        <div className="reg-center-container">
            <form className="reg-card" onSubmit={SignUp}>
                <h1>Sign Up</h1>
                <label>Email:</label>
                <FormInput type="email" name="email" value={email} onChange={e => setEmail(e.target.value)} required />
                <label>Username:</label>
                <FormInput type="text" name="username" value={username} onChange={e => setUsername(e.target.value)} required />
                <label>Password:</label>
                <FormInput
                    type="password"
                    name="password"
                    value={pass}
                    onChange={e => setPass(e.target.value)}
                    required
                />
                <label>Confirm Password:</label>
                <FormInput
                    type="password"
                    name="confirmPassword"
                    value={conPass}
                    onChange={e => setConPass(e.target.value)}
                    required
                />
                {error && <p className="error">{error}</p>}
                <button type="submit" disabled={!!error || pass !== conPass}>Submit</button>
                {msg && <p className="success" style={{color: 'green', marginTop: '10px'}}>{msg}</p>}
            </form>
        </div>
    );
}

export default SignIn;
