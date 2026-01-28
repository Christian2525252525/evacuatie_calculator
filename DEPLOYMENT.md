# Evacuatie Calculator - Web Deployment

## Overzicht

De web versie bestaat uit:
- **Frontend**: React app (GitHub Pages)
- **Backend**: FastAPI (optioneel, voor geavanceerde berekeningen)

De frontend bevat lokale berekeningen en werkt zonder backend!

---

## Stap 1: GitHub Repository voorbereiden

### In VS Code:
1. Open Source Control (Ctrl+Shift+G)
2. Klik "Initialize Repository"
3. Stage alle bestanden (+ knop)
4. Commit met bericht: "Initial web version"

### Push naar GitHub:
```bash
git remote add origin https://github.com/Christian2525252525/bbl-evacuatie-calculator.git
git branch -M main
git push -u origin main --force
```

---

## Stap 2: Frontend deployen naar GitHub Pages

### Optie A: Handmatig (eenvoudigste)

1. Ga naar je repository op GitHub
2. Ga naar Settings > Pages
3. Source: Deploy from a branch
4. Branch: `gh-pages` (wordt automatisch aangemaakt)

### Optie B: Via command line

```bash
cd web
npm install
npm run deploy
```

Dit bouwt de app en pusht naar de `gh-pages` branch.

**URL wordt**: `https://christian2525252525.github.io/bbl-evacuatie-calculator`

---

## Stap 3: (Optioneel) Backend deployen naar Railway

Als je de volledige simulatie wilt gebruiken:

### 1. Maak Railway account
Ga naar [railway.app](https://railway.app) en log in met GitHub.

### 2. Nieuw project
- Klik "New Project"
- Selecteer "Deploy from GitHub repo"
- Kies `bbl-evacuatie-calculator`

### 3. Environment
Railway detecteert automatisch Python en installeert dependencies.

### 4. Kopieer de URL
Na deployment krijg je een URL zoals:
`https://bbl-evacuatie-calculator-production.up.railway.app`

### 5. Update frontend
In `web/src/App.js`, wijzig:
```javascript
const API_URL = 'https://jouw-railway-url.up.railway.app';
```

---

## Projectstructuur

```
evacuatie_calculator/
├── api/                    # FastAPI backend
│   ├── main.py
│   └── requirements.txt
├── web/                    # React frontend
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
├── berekeningen/           # Python berekeningen (backend)
├── models/                 # Data models (backend)
├── Procfile               # Railway deployment
└── railway.json           # Railway config
```

---

## Lokale ontwikkeling

### Frontend alleen:
```bash
cd web
npm install
npm start
```
Open http://localhost:3000

### Met backend:
```bash
# Terminal 1: Backend
pip install -r api/requirements.txt
python -m uvicorn api.main:app --reload

# Terminal 2: Frontend
cd web
npm start
```

---

## Troubleshooting

### "npm not found"
Installeer Node.js: https://nodejs.org

### GitHub Pages toont oude versie
Wacht 2-3 minuten, of forceer refresh (Ctrl+Shift+R)

### CORS error
Backend staat niet goed geconfigureerd. Check `allow_origins` in `api/main.py`

---

## Voordelen van deze setup

1. **Gratis hosting** - GitHub Pages + Railway free tier
2. **Geen installatie nodig** - Werkt in elke browser
3. **Offline capable** - Frontend berekeningen werken zonder backend
4. **Makkelijk te updaten** - Push naar GitHub = automatische deploy
