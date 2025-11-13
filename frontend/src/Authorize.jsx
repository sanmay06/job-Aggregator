import React, { createContext, useContext, useEffect, useState } from "react";
import Cookies from 'js-cookie';

const AuthorizeContext = createContext();

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(Cookies.get('user') || null);

    function login(username) {
        setUser(username);
        Cookies.set('user', username, { expires:365*10});
    }

    useEffect(() => {
        console.log("User:", user + ".end");
    }, [user]);

    const Logout = () => {
        setUser(null);
        Cookies.remove('user');
    }

    return (<AuthorizeContext.Provider value={{user, login, Logout }}>
        {children}
    </AuthorizeContext.Provider>);

};

export const useAuth = () => useContext(AuthorizeContext);