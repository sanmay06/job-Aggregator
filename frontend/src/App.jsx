import React from "react";
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Login from "./pages/Login";
import Home from "./pages/Home";
import SignUp from "./pages/SignUp";
import Error404 from "./pages/ErrorPage";
import Profiles from "./pages/Profiles.jsx";

function App () {
    const router =createBrowserRouter([
        {
            path:'/',
            element: <Login />,
            errorElement: <Error404 />,
        },
        {
            path:'/home',
            element: <Home />
        },
        {
            path:'/home/:id',
            element: <Home />
        },
        {
            path:'/Sign In',
            element: <SignUp />
        },
        {
            path:'/home/profile/:id',
            element:<Profiles />
        }
    ])
    return <>
        <RouterProvider router={router} />
        
    </>
}

export default App;