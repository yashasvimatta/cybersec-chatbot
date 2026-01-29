# C&S Wholesale Groceries - Cybersecurity Chat Assistant

AI-powered cybersecurity assistant built with React and Node.js.

## Quick Start

### Prerequisites
- Node.js 20+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd cybersec-chatbot
```

**2. Setup Backend**
```bash
cd backend
npm install
cp .env.example .env
# Edit .env and add your Google Gemini API key
npm start
```

**3. Setup Frontend (new terminal)**
```bash
cd frontend
npm install
npm run dev
```

**4. Open in browser**
```
http://localhost:5173
```

## 📁 Project Structure

```
├── backend/          # Node.js + Express API
│   ├── server.js
│   └── package.json
│
└── frontend/         # Vue.js + Vite
    ├── src/
    ├── main.jsx
    └── package.json
```

## 🔧 Configuration

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3-flash-preview
DRIVE_FOLDER=your_drive_folder_id_or_link_here
DRIVE_SYNC_INTERVAL_MINUTES=30
RAG_TOP_K=5
PORT=3001
```

### Knowledge base (Google Drive → Gemini RAG)
- **What it does**: the backend periodically scans the Drive folder, downloads text from supported files (Google Docs/Sheets/Slides + text-ish files), chunks + embeds it, and then injects the most relevant snippets into each chat request.
- **Auth**: uses Google Drive API via Application Default Credentials (recommended: set `GOOGLE_APPLICATION_CREDENTIALS` to a service-account JSON, then share the folder with that service account email).

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Axios
- **Backend:** Node.js, Express, Google Gemini API
- **Styling:** CSS3

## 📝 Features

✅ AI-powered cybersecurity guidance  
✅ Conversation memory (10 exchanges)  
✅ Real-time responses  
✅ Clean component architecture  
✅ Responsive design  

## ⚠️ Security Notes

- Never commit `.env` files
- Keep your Google Gemini API key private
- This is a demo - add authentication for production use

## 📄 License

MIT

---

Built for C&S Wholesale Groceries 🏪
