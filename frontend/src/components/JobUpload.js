import React, { useState, useEffect } from "react";
import axios from "axios";

const JobUpload = () => {
  const [jobDesc, setJobDesc] = useState("");
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:5000/resumes").then(res => {
      setResumes(res.data.resumes);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.post("http://localhost:5000/upload-job", { job: jobDesc });
    alert("✅ Job description uploaded to S3!");
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Job Description Upload</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="Enter job description"
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
          rows={6}
          cols={50}
        />
        <br />
        <button type="submit">Upload Job Description</button>
      </form>

      <h3>Available Resumes</h3>
      <ul>
        {resumes.map((file) => (
          <li key={file}>{file}</li>
        ))}
      </ul>
    </div>
  );
};

export default JobUpload;
