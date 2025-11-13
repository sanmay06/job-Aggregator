import React, { useState, useEffect } from "react";
import "./styles.css";
import { useAuth } from "../Authorize";
import api from "../API";
import { Link } from "react-router-dom";

function NavBar(props) {
    const { Logout, user } = useAuth();
    const [profiles, setProfiles] = useState([""]);
    
    useEffect(() => {
        api
            .get(`/getprofiles?user=${user}`)
            .then((response) => {
                setProfiles(response.data.names);
            })
            .catch((error) => {
                console.error("Error fetching profiles:", error);
            });
    }, [user]);

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <ul className="profiles">
                    {profiles.map((profile, index) => (
                        <li key={index}>
                            <Link to={`/home/${profile}`}><button>{profile}</button></Link>
                            <Link to={`/home/profile/${profile}`}><button className="edit">-</button></Link>
                        </li>
                    ))}
                    <li>
                        <Link to={`/home/profile/createNew`}><button>+</button></Link>
                    </li>
                </ul>
                <ul className="navbar-links">
                    <li>
                        <a href="/home" hidden={props.home}>Home</a>
                    </li>
                    <li>
                        <a href="/login" onClick={Logout}>
                            Logout
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    );
}

export default NavBar;
