# 🧵 Threads Bot Dashboard

A full-stack React + Express dashboard for managing your Threads Bot accounts, captions, and images.

## 🚀 Features

### **Dashboard Overview**
- 📊 Real-time bot status and statistics
- 📈 Account, caption, and image counts
- 🕐 24/7 posting schedule information
- 🎯 Success rate tracking

### **Accounts Management**
- 👤 Add, edit, and delete Threads accounts
- 🔐 Secure password management with visibility toggle
- ✅ Enable/disable accounts
- 📝 Account descriptions and metadata
- 🎨 Modern card-based interface

### **Captions Management**
- 💬 Add, edit, and delete captions
- 📝 Rich text editing with multiline support
- 🔄 Real-time updates
- 📋 List view with inline editing

### **Images Management**
- 🖼️ Drag & drop image upload
- 📁 Support for JPG, PNG, GIF files
- 🖼️ Image preview with thumbnails
- 🗑️ Easy deletion with confirmation
- 📱 Responsive grid layout

## 🛠️ Tech Stack

### **Frontend**
- **React 18** - Modern UI framework
- **Material-UI** - Beautiful component library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls

### **Backend**
- **Express.js** - Fast, unopinionated web framework
- **Multer** - File upload handling
- **CORS** - Cross-origin resource sharing
- **fs-extra** - Enhanced file system operations

## 📦 Installation

1. **Clone the repository**
   ```bash
   cd threads-bot-dashboard
   ```

2. **Install all dependencies**
   ```bash
   npm run install-all
   ```

3. **Start the development servers**
   ```bash
   npm start
   ```

This will start both the backend server (port 5000) and frontend development server (port 3000).

## 🏃‍♂️ Running the Application

### **Development Mode**
```bash
# Start both servers
npm start

# Or start individually
npm run server  # Backend on port 5000
npm run client  # Frontend on port 3000
```

### **Production Build**
```bash
# Build the React app
npm run build

# The built files will be in client/build/
```

## 📁 Project Structure

```
threads-bot-dashboard/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Dashboard.js
│   │   │   ├── Accounts.js
│   │   │   ├── Captions.js
│   │   │   ├── Images.js
│   │   │   └── Navigation.js
│   │   └── App.js
│   └── package.json
├── server/                 # Express backend
│   ├── server.js          # Main server file
│   └── package.json
├── images/                # Uploaded images
├── accounts.json          # Bot accounts data
├── captions.txt          # Bot captions data
└── package.json
```

## 🔌 API Endpoints

### **Accounts**
- `GET /api/accounts` - Get all accounts
- `POST /api/accounts` - Create new account
- `PUT /api/accounts/:id` - Update account
- `DELETE /api/accounts/:id` - Delete account

### **Captions**
- `GET /api/captions` - Get all captions
- `POST /api/captions` - Add new caption
- `PUT /api/captions/:index` - Update caption
- `DELETE /api/captions/:index` - Delete caption

### **Images**
- `GET /api/images` - Get all images
- `POST /api/images` - Upload image
- `DELETE /api/images/:filename` - Delete image

### **Status**
- `GET /api/status` - Get bot status and statistics

## 🎨 UI Features

### **Dark Theme**
- 🌙 Modern dark theme throughout
- 🎨 Consistent Material-UI design
- 📱 Fully responsive layout

### **Navigation**
- 🧭 Sidebar navigation
- 🎯 Active page highlighting
- 📱 Mobile-friendly design

### **Interactive Elements**
- 🔄 Real-time updates
- ⚡ Loading states
- 🚨 Error handling
- ✅ Success notifications

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file in the server directory:
```env
PORT=5000
NODE_ENV=development
```

### **Bot Integration**
The dashboard reads and writes to the same files used by the Threads Bot:
- `accounts.json` - Account configurations
- `captions.txt` - Caption list
- `images/` - Image directory

## 🚀 Deployment

### **Development**
```bash
npm start
```

### **Production**
1. Build the React app:
   ```bash
   npm run build
   ```

2. Serve the built files with Express:
   ```bash
   cd server
   npm start
   ```

## 🔒 Security Notes

- 🔐 Passwords are stored in plain text (consider encryption for production)
- 🚫 Never commit `accounts.json` with real credentials
- 🔒 Use environment variables for sensitive data
- 🛡️ Implement proper authentication for production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- 📧 Create an issue on GitHub
- 📚 Check the documentation
- 🔍 Search existing issues

---

**🧵 Threads Bot Dashboard** - Manage your Threads Bot with ease! 