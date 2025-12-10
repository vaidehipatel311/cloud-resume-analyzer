import React, { useState } from "react";
import axios from "axios";

const JobUpload = () => {
  const [jobDesc, setJobDesc] = useState("");
  const [matchedResumes, setMatchedResumes] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:5000/upload-jobdesc",
        { job_description: jobDesc }
      );
      const matches = response.data.matches;
      console.log("Matches received:", matches);
      if (matches.length === 0) {
        alert("No resumes matched this job description.");
      } else {
        setMatchedResumes(matches);
      }
      setMatchedResumes(response.data.matches);
    } catch (error) {
      console.error("Error uploading job description:", error);
      alert("Failed to upload job description");
    }
  };



  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>CLOUD RESUME ANALYZER</h2>
      <h2 style={styles.heading}>Job Description Upload</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          placeholder="Enter job description"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          rows={6}
          cols={50}
          style={styles.textarea}
        />
        <button type="submit" style={styles.button}>
          Upload & Find Matches
        </button>
      </form>

      {matchedResumes.length > 0 && (
        <div style={styles.results}>
          <h3 style={styles.subheading}>Matched Resumes</h3>
          <table style={styles.table}>
            <thead>
              <tr style={styles.tableHeader}>
                <th>Resume ID</th>
                <th>Similarity</th>
              </tr>
            </thead>
            <tbody>
              {matchedResumes.map((resume) => (
                <tr key={resume.resume_id} style={styles.tableRow}>
                  <td>{resume.resume}</td>
                  <td>{(resume.similarity * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: 30,
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    backgroundColor: "#e0f2f1", // soft sea green background
    minHeight: "100vh",
  },
  heading: {
    textAlign: "center",
    color: "#00796b",
    marginBottom: 20,
  },
  subheading: {
    color: "#004d40",
    marginBottom: 10,
    textAlign: "center",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginBottom: 30,
  },
  textarea: {
    width: "80%",
    padding: 15,
    borderRadius: 10,
    border: "1px solid #00796b",
    resize: "vertical",
    fontSize: 16,
    marginBottom: 15,
    boxShadow: "2px 2px 6px rgba(0,0,0,0.1)",
  },
  button: {
    backgroundColor: "#00796b",
    color: "#fff",
    padding: "12px 25px",
    border: "none",
    borderRadius: 10,
    fontSize: 16,
    cursor: "pointer",
    transition: "all 0.3s ease",
    boxShadow: "2px 2px 6px rgba(0,0,0,0.2)",
  },
  results: {
    width: "90%",
    margin: "0 auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    backgroundColor: "#ffffff",
    borderRadius: 10,
    overflow: "hidden",
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
  },
  tableHeader: {
    backgroundColor: "#004d40",
    color: "#ffffff",
    textAlign: "left",
  },
  tableRow: {
    borderBottom: "1px solid #e0f2f1",
    transition: "background 0.3s",
  },
  tableRowHover: {
    backgroundColor: "#b2dfdb",
  },
};

export default JobUpload;
