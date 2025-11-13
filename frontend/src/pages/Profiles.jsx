import React, { useState,useEffect } from 'react';
import { useParams } from 'react-router-dom';
import NavBar from '../components/Navbar';
import api from '../API';
import { useAuth } from '../Authorize';
import PriceSlider from '../components/Slider';

function Profiles(props) {
    const params = useParams();
    const [sites, setsites] = useState([]);
    const [msg, setmsg] = useState("");
    const [name, setname] = useState("");
    const [site, setsite] = useState("");
    const [min, setmin] = useState(0);
    const [max, setmax] = useState(10000000);
    const [location, setlocation] = useState("");
    const [web, setweb] = useState(true);
    //console.log(params.id);
    const { user } = useAuth(); 

    const isCreateNew = props.create? true: false;

    useEffect(() => {
    if(!isCreateNew && params.id !== "createNew")
      api.get(`/profile/${params.id}?user=${user}`)
      .then( (response)=>{
        console.log(response.data)
        if(response.data.msg==="success"){
            console.log(response.data.profile)
            const profile_data = response.data.profile;
            setname(profile_data.name)
            setsite(profile_data.search)
            if (profile_data.internshalla)
                sitesdeal('Internshala')
            if(profile_data.adzuna)
                sitesdeal('Adzuna')
            if(profile_data.timesjob)
                sitesdeal('TimesJobs')
            if(profile_data.jobrapido)
                sitesdeal( 'JobRapido')
        //     setsites(profile_data.sites)
            setlocation(profile_data.location)
        //     //console.log(typeof(profile_data.max))
            setmax((profile_data.max))
            setmin((profile_data.min))
        //     //console.log(min,max)
        }
        else
            console.log(response.data.e)
      }).catch(e=>console.log(e))
    }, []);

    function submit(e) {
        e.preventDefault();
        if(name === "" || site === "" || sites.length === 0 || location === "")
            return setmsg("Please fill all the fields");
        let url = isCreateNew ? "/profile/create" : `/profile/${params.id}/update`;
        api.post(url, {'name':name,'search':site, 'sites': sites,'user':user,'min':min,'max':max,'location':location, 'oldname': params.id})
        .then((response) => setmsg(response.data.msg)).catch((e)=>console.log(e))
    }

    function sitesdeal(site) {
        setsites(prev => prev.includes(site) ? prev : [...prev, site]); 
    }
    
    function sitesDeal(site) {
        if(sites.includes(site))
            setsites((prev)=>prev.filter(s => s !== site));
        else
            setsites((prev)=>[...prev,site]);
    }

    return (
        <section>
            <NavBar home={false}/>
        <section className='profiles-regandedit'>
            
            <form  onSubmit={(e)=>submit(e)} >
                Enter the name for the profile:
                <input type='text' name='name' value={name} onChange={(e)=> setname(e.target.value)  } required/><br/>
                Enter the field you are searching for:
                <input type='text' name='search' value={site} onChange={(e) => setsite(e.target.value)} required/><br />
                Enter the sites you want to search in:
                <input type='text' value={sites}readOnly />
                <button onClick={(e) => {e.preventDefault();  sitesDeal('Internshala')}} >internshaala</button>
                <button onClick={(e) => {e.preventDefault();  sitesDeal('Adzuna')}} >Adzuna</button>                
                <button onClick={(e) => {e.preventDefault();  sitesDeal('TimesJobs')}} >Times job</button>
                <button onClick={(e) => {e.preventDefault();  sitesDeal('JobRapido')}} >Job Rapido</button>
                <br/>
                Enter the location to search:
                <input type="text" value={location} onChange={(e)=> setlocation(e.target.value)} />
                <PriceSlider min={setmin} max= {setmax} maxval={max} minval = {min}/>
                <input type ='submit' value={"Submit"}/>
                <div>{msg}</div>
            </form>
        </section>
        </section>
    )
}

export default Profiles;