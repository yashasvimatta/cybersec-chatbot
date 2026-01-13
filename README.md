# C&S Wholesale Groceries - Cybersecurity Chat Assistant

AI-powered cybersecurity assistant built with Vue.js and Node.js.

## Quick Start

### Prerequisites
- Node.js 16+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

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
# Edit .env and add your OpenAI API key
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
    ├── components/
    ├── App.vue
    └── package.json
```

## 🔧 Configuration

### Backend (.env)
```env
OPENAI_API_KEY=sk-proj-your_key_here
OPENAI_MODEL=gpt-4o-mini
PORT=3001
```

## 🛠️ Tech Stack

- **Frontend:** Vue 3, Vite, Axios
- **Backend:** Node.js, Express, OpenAI API
- **Styling:** CSS3

## 📝 Features

✅ AI-powered cybersecurity guidance  
✅ Conversation memory (10 exchanges)  
✅ Real-time responses  
✅ Clean component architecture  
✅ Responsive design  

## ⚠️ Security Notes

- Never commit `.env` files
- Keep your OpenAI API key private
- This is a demo - add authentication for production use

## 📄 License

MIT

---

Built for C&S Wholesale Groceries 🏪
