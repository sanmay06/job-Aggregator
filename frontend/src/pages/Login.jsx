import React, { useState } from "react";
import { useAuth } from "../Authorize";
import { useNavigate } from "react-router-dom";
import './styles.css';
import Cookies from 'js-cookie';
import FormInput from '../components/FormInput';
import api from "../API";

function Login() {
    const { login, user } = useAuth();
    const navigate = useNavigate();
    const [msg, setmsg] = useState(null);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    async function SignIn(event) {
        event.preventDefault();
        api.post("/login", { username: username.trim(), password: password.trim() })
          .then(response => {
            const { msg, token, user } = response.data;
            setmsg(msg);
            if (msg === "success") {
              login(user);
              // Store JWT token for subsequent requests
              Cookies.set('token', token, { expires: 365 * 10 });
              navigate('/home', { replace: true });
            }
          })
          .catch(e => console.log(e));
    }

    return (
        <div className="login-container">
            <form className="login-card" onSubmit={SignIn}>
                <h1>Login</h1>
                <label>Username or Email:</label>
                <FormInput type="text" name="username" value={username} onChange={e => setUsername(e.target.value)} required />
                <label>Password:</label>
                <FormInput type="password" name="password" value={password} onChange={e => setPassword(e.target.value)} required />
                <div hidden>
                    <label>Stay Signed in</label>
                </div>
                <button type="submit">Sign In</button>
                <div className="message">{msg}</div>
                <hr />
                <button
                    type="button"
                    onClick={() => navigate("/Sign In")}
                    style={{
                        backgroundColor: "#ddd",
                        color: "#333",
                        marginTop: "10px",
                    }}
                >
                    Sign Up
                </button>
            </form>
        </div>
    );
}

export default Login;
