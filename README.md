# 🚀 GenAI Image Ad Agent Pipeline

An end-to-end GenAI agent pipeline designed to generate targeted social media advertisements, visual briefs, copy variations, and marketing strategies from product inventory data using LangGraph and FastAPI, paired with an interactive React + Vite frontend.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain, Groq API (`langchain-groq`), Pydantic
- **Frontend**: React 18, TypeScript, Vite, Lucide Icons, Vanilla CSS
- **Streaming**: Server-Sent Events (SSE) for real-time generation feedback

---

## 📁 Project Structure

```text
GENAI_CCA/
├── backend/
│   ├── data/
│   │   └── inventory.json       # Product inventory dataset
│   ├── graph.py                 # LangGraph agent pipeline workflow
│   ├── inventory.py             # Inventory loader / MCP client integration
│   ├── main.py                  # FastAPI server with REST & SSE endpoints
│   ├── models.py                # Pydantic schemas & state models
│   ├── requirements.txt         # Python dependencies
│   ├── tools.py                 # Agent tools
│   ├── .env.example             # Template for environment variables
│   └── .env                     # Local environment file (git-ignored)
├── frontend/
│   ├── src/                     # React application source files
│   ├── index.html               # Entry HTML
│   ├── package.json             # NPM package definitions
│   ├── tsconfig.json            # TypeScript configuration
│   └── vite.config.ts           # Vite bundler configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and `npm` or `pnpm`
- Groq API Key ([Get one here](https://console.groq.com/))

---

### 2. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
   Add your `GROQ_API_KEY`:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key
   INVENTORY_MCP_URL=
   ```

5. **Start the FastAPI backend server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Backend will be running at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

---

### 3. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```
   Frontend will be running at `http://localhost:5173`.

---

## 🛡️ License

This project is licensed under the MIT License.
