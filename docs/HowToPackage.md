# Building the Desktop Package

This guide builds the desktop app from the three parts of the project:

| Part | Tech | Role |
|---|---|---|
| `frontend/` | Next.js (static export) | The UI shown in the app window |
| `backend/` + `pipeline/` | FastAPI, bundled by PyInstaller | Runs ESBMC, parses output, calls Gemini. Shipped as a **sidecar** executable |
| `desktop/` | Tauri (Rust) | Native window that loads the frontend and launches the backend |

ESBMC and the Gemini API key are **not bundled**. Users install ESBMC themselves and enter their own key in Settings.

---

## 1. Repository layout

```
cos700-model-checking-nlp/
├── backend/            
├── pipeline/           
│   └── nlp/prompts/    
├── frontend/           
├── data/               
└── desktop/
    └── src-tauri/
        ├── tauri.conf.json
        ├── capabilities/default.json
        ├── src/lib.rs
        └── binaries/   
```

---

## 2. Package installation

| Tool | Notes |
|---|---|
| Python 3.10+ with a venv | `pip install -r requirements.txt pyinstaller` inside `backend/venv` |

---

## 3. Build steps

Run these from the **project root**, in this order. 

### Step 1: Backend sidecar (PyInstaller)

```bash
source backend/venv/bin/activate
pip install pyinstaller

pyinstaller --noconfirm --onefile --name backend-server --paths . \
  --add-data "pipeline/nlp/prompts:pipeline/nlp/prompts" \
  backend/main.py
```

(On Windows the `--add-data` separator is `;`, not `:`.)

Test it on its own before involving Tauri:

```bash
./dist/backend-server &
curl http://127.0.0.1:8000/health      # expect {"status":"ok"}
pkill -f backend-server
```

Tauri requires the binary name to end in your platform's target triple:

```bash
TRIPLE=$(rustc -vV | sed -n 's/host: //p')     # e.g. x86_64-unknown-linux-gnu
mkdir -p desktop/src-tauri/binaries
cp dist/backend-server "desktop/src-tauri/binaries/backend-server-$TRIPLE"
```

### Step 2: Build the frontend

```bash
cd frontend
npm install
npm run build          # produces frontend/out/
cd ..
```

### Step 3: Build the Tauri package

```bash
cd desktop
npm install
npm run tauri build
```


### Step 4: Locate the output

```
desktop/src-tauri/target/release/bundle/
├── deb/        <package name>.deb
└── appimage/   <package name>.AppImage
```

## 4. Installing and running the package

**AppImage (portable, recommended for testing):**

```bash
mkdir -p ~/appimage-test
cp desktop/src-tauri/target/release/bundle/appimage/*.AppImage ~/appimage-test/
cd ~/appimage-test
chmod +x *.AppImage
./*.AppImage
```

Running it from outside the project directory checks that the app doesn't depend on project-relative paths.

**Debian package:**

```bash
sudo apt install ./desktop/src-tauri/target/release/bundle/deb/desktop_0.1.0_amd64.deb
sudo apt remove desktop          # to uninstall
```

---

## 5. Runtime requirements (for end users)

| Requirement | How |
|---|---|
| **ESBMC** on the `PATH` | Install from <https://github.com/esbmc/esbmc/releases>. Verify with `esbmc --version` |
| **Gemini API key** | Create one at <https://aistudio.google.com/apikey>, then open **Settings** in the app and save it |
| **Network access** | Needed for Gemini and the PlantUML diagram server |

The key is stored in plain text in the app's `settings.json`. Revoke it in Google AI Studio if you ever use a shared machine.

---

## 6. Troubleshooting

| Symptom  | Fix |
|---|---|
| Missing ESBMC|  Verify that ESBMC is installed and that esbmc --version works in the environment used to launch the application. If ESBMC is installed, reload the page. |
| Issues with frontend rendering| Run with this command: WEBKIT_DISABLE_DMABUF_RENDERER=1 WEBKIT_DISABLE_COMPOSITING_MODE=1 ./'<package name>.AppImage' |