const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure uploads directory exists
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Configure Multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => {
    // Optionally sanitize or timestamp filenames
    const timestamp = Date.now();
    const ext = path.extname(file.originalname) || '.xml';
    const base = path.basename(file.originalname, ext);
    cb(null, `${base}-${timestamp}${ext}`);
  },
});

const fileFilter = (req, file, cb) => {
  // Basic check for XML mimetypes
  const allowed = ['text/xml', 'application/xml'];
  if (allowed.includes(file.mimetype) || file.originalname.toLowerCase().endsWith('.xml')) {
    cb(null, true);
  } else {
    cb(new Error('Only XML files are allowed.'));
  }
};

const upload = multer({ storage, fileFilter });

const app = express();

// Serve the static index.html
app.use(express.static(path.join(__dirname)));

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'No file uploaded.' });
  }
  return res.json({
    message: 'File uploaded successfully.',
    filename: req.file.filename,
    path: `upload/${req.file.filename}`,
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});