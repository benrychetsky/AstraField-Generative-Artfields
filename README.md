# AstraField-Generative-Artfields

🌌 AstraField

AstraField is a generative art tool powered by a Python FastAPI backend and a React frontend.
Inspired by abstract album art (like Hello Meteor), AstraField creates dynamic, geometry- and photo-driven artworks with gradients, halftones, grids, and layered effects.

🚀 Features

🎨 Generative backdrops — gradients, grids, geometric primitives, halftone patterns.

🖼️ Photo integration — upload a mountain, ocean, or forest photo as a base layer.

⚙️ Adjustable parameters — tweak grid density, dot size, palettes, and randomness.

📼 Retro texture — film grain + vignette for a print-inspired aesthetic.

⚡ Modern frontend — React UI with live preview, sliders, and “Generate/Download” buttons.

🛠️ Tech Stack

Backend: FastAPI
 · Pillow
 · NumPy · Matplotlib

Frontend: React (Vite + TypeScript) · pnpm

Other: Python virtual environment for backend, CORS middleware for API calls

📦 Setup
1. Clone the repo
git clone https://github.com/yourusername/AstraField.git
cd AstraField

2. Backend (Python + FastAPI)
cd backend
python -m venv venv
# activate venv
# Windows PowerShell
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload


The API will run on http://localhost:8000
.

3. Frontend (React + Vite + pnpm)
cd frontend
pnpm install
pnpm run dev


The UI will run on http://localhost:5173
.

🎛️ Usage

Upload a base photo (optional).

Adjust sliders (grid density, dot step, palette, etc.).

Click Generate → artwork preview appears.

Download as PNG (SVG export coming soon 🚧).

📂 Project Structure
AstraField/
│
├── backend/          # FastAPI backend
│   ├── main.py       # API entrypoint
│   └── requirements.txt
│
└── frontend/         # React + Vite frontend
    ├── src/
    └── package.json

🔮 Roadmap

 SVG / vector export for print

 Multiple layout presets (Halftone, Bauhaus, Obi Strip, etc.)

 Batch generation & seeds for reproducibility

 Save & share galleries
