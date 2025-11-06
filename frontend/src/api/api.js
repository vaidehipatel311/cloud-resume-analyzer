import axios from "axios";
const API_URL = "http://127.0.0.1:5000";

export const uploadJobDescription = async (jobDescription) => {
  const res = await axios.post(`${API_URL}/upload-job`, {
    job_description: jobDescription,
  });
  return res.data;
};

export const getResumeList = async () => {
  const res = await axios.get(`${API_URL}/get-resume-list`);
  return res.data.resumes;
};
