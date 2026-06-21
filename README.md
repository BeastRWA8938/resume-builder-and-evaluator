# Career Intelligence System — AI ATS Analyzer & Resume Studio

The **Career Intelligence System** is an ultra-premium, local-first web application that merges a **FastAPI backend** with a sleek glassmorphic **single-page frontend**. It serves as a unified command center for career asset optimization:

1. **Knowledge Vault**: A structured SQLite repository for storing your career experiences, projects, and achievements. Paste raw logs or text, extract structured records with Gemini AI, edit details, and manage them in the Explorer.
2. **ATS Resume Analyzer**: Evaluates resumes against target job descriptions, computes match scores, outlines skill gaps, audits keywords, and generates formatting feedback.
3. **AI LaTeX Resume Generator (Resume Studio)**: Tailors custom XeLaTeX resumes based on candidate details in your Knowledge Base and compiled directly into PDF format.

---

## ✨ Features

### 1. Knowledge Vault (V1)
- **AI Extraction**: Paste raw work descriptions or bullet points. The system extracts structured records (achievements, technologies, skills, dates).
* **Interactive Editing & Verification**: Review extracted data side-by-side with original text. Modify titles, bullet points, and skills before saving.
* **Workspace Explorer**: Search, filter, and view saved experiences and projects in a responsive grid.
* **SQLite Persistence**: Stores all assets locally in a structured database schema with cascading relations.

### 2. ATS Scanner & Analyzer
- **Document Text Extractor**: Supports uploading `.pdf`, `.docx`, and `.txt` files directly.
- **Intelligent ATS Scoring**: Computes compatibility match scores (0-100) using Gemini's structured models.
- **Skill Gap Analysis**: Divides skills into categorized domains with Side-by-Side matches & missing skills lists.
- **Keyword Auditing**: Visual tags indicating which target job keywords are matched vs. missing.
- **Scan History Sidebar**: Persists all scans locally via SQLite so you can re-load or delete past analyses.

### 3. LaTeX Resume Generator
- **Knowledge Base Aggregator**: Recursively crawls and aggregates markdown files from `Knowledge Base/Projects` and `Knowledge Base/Work` (integrations with the SQLite Knowledge Vault are planned for V2).
- **Target Company Check**: Researches the target company engineering culture and tech stack using Google Search Grounding to align the tailored resume.
- **XeLaTeX Compilation**: Automatically customizes LaTeX code based on the PlushCV template and compiles it into a single-page PDF locally.
- **Interactive Preview & Downloads**: Instantly preview the compiled PDF in the browser iframe and download both the compiled `.pdf` and `.tex` source files.

---

## 🐳 Docker Deployment (Recommended)

Running the application using Docker is the simplest method, as it packages the FastAPI backend, the frontend, the SQLite database, and the complete **XeLaTeX** compilation engine (TeX Live packages) without requiring manual system package installations.

### 1. Requirements
Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 2. Configure Environment Variables
Create a `.env` file in the root folder of the project:
```env
# Google Gemini API Key - Required for resume analysis and extraction
GEMINI_API_KEY=your_gemini_api_key_here

# (Optional) Map where compiled resumes are saved on your host device (defaults to ./Resumes)
RESUME_OUTPUT_PATH=c:/Users/YourUsername/Documents/Resume
```

### 3. Start the Containers
Open a terminal in the root directory and run:
```bash
docker-compose up --build -d
```

The application will be accessible at **[http://localhost:8000](http://localhost:8000)**. 
- All output resumes will automatically be saved directly to your host's local directories via volume mapping.
- Live front-end updates and database states are persisted inside volume mounts.

---

## 🛠️ Step-by-Step Local (Non-Docker) Installation Guide

If you prefer to run the application natively on your system:

### Step 1: Install Python (3.9 or higher)
1. Download Python from the [official website](https://www.python.org/downloads/).
2. **Important for Windows**: During installation, check the box that says **"Add Python to PATH"**.
3. Verify your installation:
   ```bash
   python --version
   ```

### Step 2: Install XeLaTeX Compiler
To compile the tailored LaTeX code into a PDF resume natively:

#### 🪟 Windows (MiKTeX)
1. Go to the [MiKTeX Download Page](https://miktex.org/download) and download the Windows Installer.
2. Run the installer.
3. **CRITICAL STEP**: During the installation wizard, under the **"Auto-install missing packages"** option, select **"Yes"** (or "Ask me first"). The PlushCV template relies on several LaTeX packages (like `textpos`, `isodate`, `substr`, `titlesec`, `fancyhdr`). Choosing "Yes" allows MiKTeX to install these packages on-the-fly when compiling your first resume.
4. Verify XeLaTeX is available in your PATH:
   ```powershell
   xelatex --version
   ```

#### 🍎 macOS (MacTeX or BasicTeX)
1. Install using Homebrew:
   ```bash
   brew install --cask mactex-no-gui
   ```
2. Verify XeLaTeX:
   ```bash
   xelatex --version
   ```

#### 🐧 Linux (Debian/Ubuntu)
1. Install TeX Live with XeTeX support via `apt`:
   ```bash
   sudo apt update
   sudo apt-get install -y texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-plain-generic
   ```
2. Verify XeLaTeX:
   ```bash
   xelatex --version
   ```

### Step 3: Setup Virtual Environment & Python dependencies
1. Navigate to the root directory `ResumeATSAnalyzer`.
2. Create the virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the environment:
   - **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
   - **Windows (CMD)**: `.\venv\Scripts\activate.bat`
   - **macOS / Linux**: `source venv/bin/activate`
4. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Step 4: Setup Local directories
1. Create a directory named `Knowledge Base` in the project root.
2. Inside `Knowledge Base/`, create two subdirectories: `Projects/` and `Work/`.
3. Add your project descriptions as individual `.md` files inside `Projects/` (e.g. `Projects/smart-blind-stick.md`).
4. Add your work experience and internship histories as individual `.md` files inside `Work/` (e.g. `Work/think-of-it-foundation.md`).
5. (Note: These files are git-ignored by default to protect your privacy).

### Step 5: Launch the Server
1. Start the development server natively:
   ```bash
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```
2. Open your browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
