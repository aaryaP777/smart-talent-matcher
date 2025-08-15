// server.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const multer = require("multer");

const app = express();

// --- Config ---
const PORT = process.env.PORT || 5000;
const FRONTEND_ORIGIN = process.env.FRONTEND_ORIGIN || "http://localhost:5173";

// CORS for the Vite dev server
app.use(cors({ origin: FRONTEND_ORIGIN, credentials: true }));

// Body parsers
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: true }));

// Multer (in-memory) for quick start
const upload = multer({ storage: multer.memoryStorage() });

// --- Health check ---
app.get("/api/health", (req, res) => {
  res.json({ ok: true, service: "smart-talent-matcher-backend" });
});

// --- Upload JD (PDF/TXT/DOCX later; for now just text or any file) ---
app.post("/api/jd/upload", upload.single("file"), async (req, res) => {
  try {
    // If sending plain text instead of a file:
    const jdText = req.body.text;

    // If sending as a file:
    const fileMeta = req.file
      ? {
          originalname: req.file.originalname,
          size: req.file.size,
          mimetype: req.file.mimetype,
        }
      : null;

    // TODO: send to Python AI service for parsing (next steps)
    // For now, return a mock parse so the UI can move forward.
    const parsedJD = {
      job_title: "React Developer",
      skills: ["React", "Node.js", "MongoDB"],
      experience_years_min: 3,
      qualifications: ["B.Tech CS (preferred)"],
    };

    res.json({
      received: { jdText: !!jdText, file: fileMeta },
      parsed: parsedJD,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "JD upload failed" });
  }
});

// --- Upload Resume ---
app.post("/api/resume/upload", upload.single("file"), async (req, res) => {
  try {
    const resumeText = req.body.text;
    const fileMeta = req.file
      ? {
          originalname: req.file.originalname,
          size: req.file.size,
          mimetype: req.file.mimetype,
        }
      : null;

    // TODO: send to Python AI service for parsing (next steps)
    const parsedResume = {
      name: "John Doe",
      skills: ["React", "Node.js", "MongoDB"],
      experience_years: 4,
      education: [{ degree: "B.Tech", field: "CSE" }],
    };

    res.json({
      received: { resumeText: !!resumeText, file: fileMeta },
      parsed: parsedResume,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Resume upload failed" });
  }
});

// --- Matching endpoint (mock for now) ---
app.post("/api/match", express.json(), (req, res) => {
  const { parsedJD, parsedResume } = req.body || {};
  // super simple mock scoring
  const jdSkills = new Set(
    (parsedJD?.skills || []).map((s) => s.toLowerCase())
  );
  const resumeSkills = new Set(
    (parsedResume?.skills || []).map((s) => s.toLowerCase())
  );
  let overlap = 0;
  jdSkills.forEach((s) => {
    if (resumeSkills.has(s)) overlap++;
  });

  const score = jdSkills.size ? Math.round((overlap / jdSkills.size) * 100) : 0;
  const explanation =
    score >= 80
      ? "Candidate meets most skill requirements and likely experience criteria."
      : "Partial skill match. Consider training or alternative role.";

  res.json({ score, explanation });
});

// --- Start ---
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
