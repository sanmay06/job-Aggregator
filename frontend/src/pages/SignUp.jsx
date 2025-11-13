import React, { useEffect, useState } from "react";
import './styles.css';
import api from "../API";

function SignIn() {
    const [pass, setPass] = useState("");
    const [conPass, setConPass] = useState("");
    const [error, setError] = useState("");
    const [msg, setmsg] = useState("");

    async function SignUp(event) {
        event.preventDefault();
        await api.post("/reg", { 'email':event.target.email.value.trim(), 'username': event.target.username.value.trim(), 'password': event.target.password.value.trim() } )
        .then(response => setmsg(response.data.msg)).catch(e => console.log(e)) 
        setError("");
        // setmsg("Account created successfully!");
    }
    
    useEffect(()=>{
        if (pass !== conPass)
            setmsg("password doesnt match");
        else if(conPass === "")
            setmsg("");
        else
            setmsg("");
    },[conPass])

    return (
        <div className="reg-center-container">
            <form className="reg-card" onSubmit={SignUp}>
                <h1>Sign Up</h1>
                <label>Email:</label>
                <input type="email" name="email" required />
                <label>Username:</label>
                <input type="text" name="username" required />
                <label>Password:</label>
                <input
                    type="password"
                    name="password"
                    value={pass}
                    onChange={(e) => setPass(e.target.value)}
                    required
                />
                <label>Confirm Password:</label>
                <input
                    type="password"
                    name="confirmPassword"
                    value={conPass}
                    onChange={(e) => {setConPass(e.target.value)}}
                    required
                />
                {error && <p className="error">{error}</p>}
                <button type="submit">Submit</button>
                <div className="message">{msg}</div>
            </form>
        </div>
    );
}

export default SignIn;
