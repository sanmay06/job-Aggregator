import React, { useState, useEffect } from "react";
import api from "../API";
import { useAuth } from "../Authorize";

function Table(props) {
    const { user } = useAuth();
    const [title, settitle] = useState(false);
    const [company, setcompany] = useState(false);
    const [salary, setsalary] = useState(true);
    const [location, setlocation] = useState(false);
    const [website, setwebsite] = useState(false);
    const [jobs, setjobs] = useState([]);
    const [status, setstatus] = useState(false);
    const [msg, setmsg] = useState({});
    const [currentPage, setCurrentPage] = useState(1);
    const jobsPerPage = 30;

    useEffect(() => {
        console.log(jobs);
    }, [jobs]);

    function ordering(o) {
        const sortedJobs = [...jobs];
        sortedJobs.sort((a, b) => {
            let salaryA = a.salary !== null ? parseFloat(a.salary) : (a.minsalary && a.maxsalary ? (parseFloat(a.minsalary) + parseFloat(a.maxsalary)) / 2 : 0);
            let salaryB = b.salary !== null ? parseFloat(b.salary) : (b.minsalary && b.maxsalary ? (parseFloat(b.minsalary) + parseFloat(b.maxsalary)) / 2 : 0);
            return o === "i" ? salaryA - salaryB : salaryB - salaryA;
        });
        setjobs(sortedJobs);
        setCurrentPage(1); // Reset to first page on reorder
    }

    const scrapeAndFetchJobs = async (profile, user) => {
        const sources = ["internshalla", "adzuna", "jobrapido"];

        try {
            await Promise.all(
                sources.map(source => {
                    setmsg(prev => ({ ...prev, [source]: "fetching started" }));
                    return api.get(`/scrape_jobs/${source}/${profile}?user=${user}`).then(() => {
                        setmsg(prev => ({ ...prev, [source]: "fetching finished" }));
                    });
                })
            );

            console.log("Scraping started for all sources");

            setTimeout(async () => {
                try {
                    const pages = await api.get(`/get_pages/${profile}?user=${user}`);
                    setmsg(prev => ({ ...prev, jobs: "fetching started" }));
                    const allJobs = [];
                    console.log(pages.data.pages);
                    for (let i = 0; i < pages.data.pages; i++) {
                        try {
                            const resp = await api.get(`/fetch_jobs/${profile}/${i + 1}?user=${user}`);
                            if (resp.data && resp.data.jobs) {
                                allJobs.push(...resp.data.jobs);
                            }
                        } catch (pageError) {
                            console.log(`Error fetching page ${i + 1}:`, pageError);
                        }
                    }

                    setjobs(allJobs);
                    setmsg(prev => ({ ...prev, jobs: "Jobs fetched successfully" }));
                    setCurrentPage(1);
                } catch (fetchError) {
                    console.log("Error fetching jobs:", fetchError);
                    setmsg(prev => ({ ...prev, jobs: "Error fetching jobs" }));
                } finally {
                    setstatus(true);
                }
            }, 5000);
        } catch (scrapeError) {
            console.log("Error scraping jobs:", scrapeError);
        }
    };

    useEffect(() => {
        if (props.profile) {
            scrapeAndFetchJobs(props.profile, user);
        }
    }, [props.profile, user]);

    const printTable = () => {
        const fullTableRows = jobs.map((job, index) => {
            let sal = job.salary != null
                ? job.salary
                : job.minsalary && job.maxsalary
                    ? `${job.minsalary} - ${job.maxsalary}`
                    : "N/A";

            return `
                <tr>
                    <td>${index + 1}</td>
                    ${title ? `<td>${job.job_title || "N/A"}</td>` : ""}
                    ${company ? `<td>${job.companyname || "N/A"}</td>` : ""}
                    ${location ? `<td>${job.location || "N/A"}</td>` : ""}
                    <td><a href="${job.link}" target="_blank">View</a></td>
                    ${salary ? `<td>${sal}</td>` : ""}
                    ${website ? `<td>${job.website || "N/A"}</td>` : ""}
                </tr>
            `;
        }).join("");

        const tableHeaders = `
            <tr>
                <th>S.No</th>
                ${title ? "<th>Job Title</th>" : ""}
                ${company ? "<th>Company</th>" : ""}
                ${location ? "<th>Location</th>" : ""}
                <th>Link</th>
                ${salary ? "<th>Salary</th>" : ""}
                ${website ? "<th>Website</th>" : ""}
            </tr>
        `;

        const printWindow = window.open("", "_blank");
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print Table</title>
                    <style>
                        table { width: 100%; border-collapse: collapse; }
                        th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                        a { color: blue; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <h2>Job Listings (All Pages)</h2>
                    <table>
                        <thead>${tableHeaders}</thead>
                        <tbody>${fullTableRows}</tbody>
                    </table>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    };


    // Pagination Logic
    const indexOfLastJob = currentPage * jobsPerPage;
    const indexOfFirstJob = indexOfLastJob - jobsPerPage;
    const currentJobs = jobs.slice(indexOfFirstJob, indexOfLastJob);

    const nextPage = () => {
        if (indexOfLastJob < jobs.length) {
            setCurrentPage(prev => prev + 1);
        }
    };

    const prevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(prev => prev - 1);
        }
    };

    return (
        <div className="center-container">
            <h1 hidden={status}>Loading....</h1>
            <div hidden={status}>
                <Status msg={msg} />
            </div>
            <div hidden={!status}>
                <form className="filter-form">
                    <label>
                        <input type="checkbox" checked={title} onChange={() => settitle(!title)} />
                        Job Title
                    </label>
                    <label>
                        <input type="checkbox" checked={company} onChange={() => setcompany(!company)} />
                        Company
                    </label>
                    <label>
                        <input type="checkbox" checked={salary} onChange={() => setsalary(!salary)} />
                        Salary
                    </label>
                    <label>
                        <input type="checkbox" checked={location} onChange={() => setlocation(!location)} />
                        Location
                    </label>
                    <label>
                        <input type="checkbox" checked={website} onChange={() => setwebsite(!website)} />
                        Website
                    </label>
                    <br />
                    <button onClick={printTable}>Print Table</button>
                    <button onClick={(e) => { e.preventDefault(); ordering("i"); }}>Sort Salary ↑</button>
                    <button onClick={(e) => { e.preventDefault(); ordering("d"); }}>Sort Salary ↓</button>
                </form>

                <table>
                    <thead>
                        <tr>
                            <th>S.No</th>
                            <th hidden={!title}>Job Title</th>
                            <th hidden={!company}>Company</th>
                            <th hidden={!location}>Location</th>
                            <th>Link</th>
                            <th hidden={!salary}>Salary</th>
                            <th hidden={!website}>Website</th>
                        </tr>
                    </thead>
                    <tbody>
                        {currentJobs.map((job, index) => {
                            let sal = job.salary != null
                                ? job.salary
                                : job.minsalary && job.maxsalary
                                    ? `${job.minsalary} - ${job.maxsalary}`
                                    : "N/A";
                            return (
                                <tr key={index}>
                                    <td>{indexOfFirstJob + index + 1}</td>
                                    <td hidden={!title}>{job.job_title || "N/A"}</td>
                                    <td hidden={!company}>{job.companyname || "N/A"}</td>
                                    <td hidden={!location}>{job.location || "N/A"}</td>
                                    <td><a href={job.link} target="_blank" rel="noopener noreferrer">View</a></td>
                                    <td hidden={!salary}>{sal}</td>
                                    <td hidden={!website}>{job.website || "N/A"}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>

                <div className="pagination">
                    <button onClick={prevPage} disabled={currentPage === 1}>Previous</button>
                    <span> Page {currentPage} </span>
                    <button onClick={nextPage} disabled={indexOfLastJob >= jobs.length}>Next</button>
                </div>
            </div>
        </div>
    );
}

const Status = ({ msg }) => {
    const style = {
        label: {
            fontWeight: "bold",
            marginRight: "10px",
            color: "blue",
        },
        value: {
            color: "green",
        }
    };
    return (
        <div className="status-container">
            <h2>Status</h2>
            {msg && Object.entries(msg).map(([key, value]) => (
                <div key={key}>
                    <strong style={style.label}>{key}:</strong>
                    <span style={style.value}>{value}</span>
                </div>
            ))}
        </div>
    );
};

export default Table;
