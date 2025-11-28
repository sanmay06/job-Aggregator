import React, { useEffect, useState } from "react";
import "./styles.css";
import NavBar from "../components/Navbar";
import Table from "../components/Table";
import { useParams } from "react-router-dom";
import { useAuth } from "../Authorize";
import api from "../API";

function Home() {
    const { user } = useAuth();
    const [id, setId] = useState(null);
    const param = useParams();
    const [profiles, setProfiles] = useState();

    useEffect(() => {
        document.title = "home";
    }, []);

    useEffect(() => {
        if (param.id) {
            setId(param.id);
        } else {
            api.get(`/getprofiles?user=${user}`)
                .then((response) => {
                    const names = response.data.names || [];
                    setProfiles(names);
                    if (names.length > 0) {
                        setId(names[0]);
                    }
                })
                .catch((error) => {
                    console.error("Error fetching profiles:", error);
                });
        }
    }, [param.id, user]);

    return (
        <section>
            <NavBar home={true} />
            {profiles && profiles.length === 0 ? (
                <p>No profiles found. Try creating a new one.</p>
            ) : (
                <Table profile={id} />
            )}
        </section>
    );
}

export default Home;