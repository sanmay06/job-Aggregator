import React from "react";
import { Link } from "react-router-dom";

function Error404() {
    return(
        <section className="error">
            there was some error in link
            < Link to = "/">Login</Link>
        </section>
    );
}

export default Error404;