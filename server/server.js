const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs-extra');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Serve images directory
app.use('/images', express.static(path.join(__dirname, '../images')));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadPath = path.join(__dirname, '../images');
    fs.ensureDirSync(uploadPath);
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'));
    }
  }
});

// File paths
const ACCOUNTS_FILE = path.join(__dirname, '../accounts.json');
const CAPTIONS_FILE = path.join(__dirname, '../captions.txt');
const IMAGES_DIR = path.join(__dirname, '../images');

// Ensure directories exist
fs.ensureDirSync(IMAGES_DIR);

// Helper function to read accounts
async function readAccounts() {
  try {
    const data = await fs.readFile(ACCOUNTS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('Creating new accounts.json file');
    return [];
  }
}

// Helper function to write accounts
async function writeAccounts(accounts) {
  await fs.writeFile(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2));
}

// Helper function to read captions
async function readCaptions() {
  try {
    const data = await fs.readFile(CAPTIONS_FILE, 'utf8');
    return data.split('\n').filter(line => line.trim() !== '');
  } catch (error) {
    console.log('Creating new captions.txt file');
    return [];
  }
}

// Helper function to write captions
async function writeCaptions(captions) {
  await fs.writeFile(CAPTIONS_FILE, captions.join('\n'));
}

// Helper function to get images
async function getImages() {
  try {
    const files = await fs.readdir(IMAGES_DIR);
    return files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ['.jpg', '.jpeg', '.png', '.gif'].includes(ext);
    });
  } catch (error) {
    return [];
  }
}

// API Routes

// Get all accounts
app.get('/api/accounts', async (req, res) => {
  try {
    const accounts = await readAccounts();
    res.json(accounts);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read accounts' });
  }
});

// Create new account
app.post('/api/accounts', async (req, res) => {
  try {
    const accounts = await readAccounts();
    const newAccount = {
      id: Date.now().toString(),
      username: req.body.username,
      email: req.body.email,
      password: req.body.password,
      enabled: req.body.enabled || true,
      posting_schedule: {
        frequency: "every_5_minutes",
        interval_minutes: 5,
        timezone: "UTC",
        start_time: "00:00",
        end_time: "23:59"
      },
      description: req.body.description || "",
      posting_config: {
        use_random_caption: true,
        use_random_image: true,
        max_posts_per_day: 288,
        delay_between_posts_seconds: 300
      }
    };
    
    accounts.push(newAccount);
    await writeAccounts(accounts);
    res.json(newAccount);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create account' });
  }
});

// Update account
app.put('/api/accounts/:id', async (req, res) => {
  try {
    const accounts = await readAccounts();
    const accountIndex = accounts.findIndex(acc => acc.id === req.params.id);
    
    if (accountIndex === -1) {
      return res.status(404).json({ error: 'Account not found' });
    }
    
    accounts[accountIndex] = { ...accounts[accountIndex], ...req.body };
    await writeAccounts(accounts);
    res.json(accounts[accountIndex]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to update account' });
  }
});

// Delete account
app.delete('/api/accounts/:id', async (req, res) => {
  try {
    const accounts = await readAccounts();
    const filteredAccounts = accounts.filter(acc => acc.id !== req.params.id);
    await writeAccounts(filteredAccounts);
    res.json({ message: 'Account deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete account' });
  }
});

// Get all captions
app.get('/api/captions', async (req, res) => {
  try {
    const captions = await readCaptions();
    res.json(captions);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read captions' });
  }
});

// Add new caption
app.post('/api/captions', async (req, res) => {
  try {
    const captions = await readCaptions();
    captions.push(req.body.caption);
    await writeCaptions(captions);
    res.json({ message: 'Caption added successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to add caption' });
  }
});

// Update caption
app.put('/api/captions/:index', async (req, res) => {
  try {
    const captions = await readCaptions();
    const index = parseInt(req.params.index);
    
    if (index < 0 || index >= captions.length) {
      return res.status(404).json({ error: 'Caption not found' });
    }
    
    captions[index] = req.body.caption;
    await writeCaptions(captions);
    res.json({ message: 'Caption updated successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update caption' });
  }
});

// Delete caption
app.delete('/api/captions/:index', async (req, res) => {
  try {
    const captions = await readCaptions();
    const index = parseInt(req.params.index);
    
    if (index < 0 || index >= captions.length) {
      return res.status(404).json({ error: 'Caption not found' });
    }
    
    captions.splice(index, 1);
    await writeCaptions(captions);
    res.json({ message: 'Caption deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete caption' });
  }
});

// Get all images
app.get('/api/images', async (req, res) => {
  try {
    const images = await getImages();
    res.json(images);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read images' });
  }
});

// Upload image
app.post('/api/images', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image file uploaded' });
    }
    
    res.json({ 
      message: 'Image uploaded successfully',
      filename: req.file.filename
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to upload image' });
  }
});

// Delete image
app.delete('/api/images/:filename', async (req, res) => {
  try {
    const imagePath = path.join(IMAGES_DIR, req.params.filename);
    await fs.remove(imagePath);
    res.json({ message: 'Image deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete image' });
  }
});

// Get bot status
app.get('/api/status', async (req, res) => {
  try {
    const accounts = await readAccounts();
    const captions = await readCaptions();
    const images = await getImages();
    
    const enabledAccounts = accounts.filter(acc => acc.enabled);
    
    res.json({
      totalAccounts: accounts.length,
      enabledAccounts: enabledAccounts.length,
      totalCaptions: captions.length,
      totalImages: images.length,
      botStatus: 'ready'
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get bot status' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Threads Bot Dashboard Server running on port ${PORT}`);
  console.log(`📊 API available at http://localhost:${PORT}/api`);
}); 