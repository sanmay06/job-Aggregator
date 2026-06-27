import React, { useState, useEffect } from "react";
import "./styles.css";
import { useAuth } from "../Authorize";
import api from "../API";
import { Link } from "react-router-dom";

function NavBar(props) {
  const { Logout, user } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Scroll detection for navbar styling
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Load user profiles
  useEffect(() => {
    api
      .get(`/getprofiles?user=${user}`)
      .then((response) => setProfiles(response.data.names))
      .catch((error) => console.error("Error fetching profiles:", error));
  }, [user]);

  return (
    <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
      <div className="navbar-container">
        {/* Mobile hamburger toggle */}
        <button
          className={`navbar-toggle ${menuOpen ? "open" : ""}`}
          type="button"
          aria-label="Toggle navigation"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        {/* Profiles list */}
        <ul className={`profiles ${menuOpen ? "active" : ""}`}>
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

        {/* Main navigation links */}
        <ul className={`navbar-links ${menuOpen ? "active" : ""}`}>
          <li>
            {!props.home && <Link to="/home">Home</Link>}
          </li>
          <li>
            <a href="/login" onClick={Logout}>Logout</a>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default NavBar;
