# Evacuatie Calculator - Streamlit Deployment

## Lokaal testen

```bash
# Installeer dependencies
pip install streamlit plotly pandas

# Start de app
streamlit run streamlit_app.py
```

Open vervolgens http://localhost:8501 in je browser.

## Deployen naar Streamlit Cloud (Gratis)

### Stap 1: GitHub Repository
Zorg dat je code op GitHub staat. Als dat nog niet zo is:
```bash
git add streamlit_app.py requirements_streamlit.txt .streamlit/
git commit -m "Add Streamlit web app"
git push
```

### Stap 2: Streamlit Cloud Account
1. Ga naar https://share.streamlit.io
2. Log in met je GitHub account
3. Klik "New app"

### Stap 3: Deploy configuratie
Vul in:
- **Repository**: jouw-username/evacuatie_calculator
- **Branch**: main
- **Main file path**: streamlit_app.py
- **Python version**: 3.10 (of hoger)

### Stap 4: Advanced settings
Klik op "Advanced settings" en stel de requirements file in:
```
requirements_streamlit.txt
```

### Stap 5: Deploy
Klik op "Deploy!" en wacht tot de app live is.

Je krijgt een URL zoals: `https://jouw-app.streamlit.app`

## Bestandsstructuur voor deployment

```
evacuatie_calculator/
├── streamlit_app.py          # Hoofdapplicatie
├── requirements_streamlit.txt # Dependencies voor Streamlit
├── .streamlit/
│   └── config.toml           # Streamlit configuratie
├── models/
│   ├── constanten.py
│   ├── project.py
│   └── trap.py
└── berekeningen/
    ├── capaciteit.py
    ├── simulatie.py
    └── toetsing.py
```

## Troubleshooting

### "ModuleNotFoundError"
Zorg dat alle benodigde modules in requirements_streamlit.txt staan.

### "App crashes on startup"
Check de logs in Streamlit Cloud dashboard voor details.

### Thema aanpassen
Wijzig `.streamlit/config.toml` voor kleuren en fonts.

## Alternatieven voor hosting

Als Streamlit Cloud niet werkt:

1. **Hugging Face Spaces** (gratis)
   - Maak een Space aan op huggingface.co
   - Selecteer "Streamlit" als SDK
   - Upload dezelfde bestanden

2. **Render.com** (gratis tier)
   - Maak een Web Service aan
   - Start command: `streamlit run streamlit_app.py --server.port $PORT`

3. **Railway.app** (gratis tier)
   - Import van GitHub
   - Automatische detectie van Streamlit
