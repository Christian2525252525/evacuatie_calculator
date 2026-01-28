import React, { useState } from 'react';
import './App.css';

// API URL - wijzig naar je Railway URL na deployment
const API_URL = process.env.REACT_APP_API_URL || 'https://your-api.railway.app';

function App() {
  const [formData, setFormData] = useState({
    doorgang_uitgang_m: 1.2,
    type_uitgang: 'Dubbele deur >= 1.2m',
    locatie: 'Beschermde vluchtroute',
    aantal_verdiepingen: 10,
    breedte_trap_m: 1.1,
    oppervlakte_bordes_m2: 2.0,
    doorgang_naar_trap_m: 0.85,
    type_doorgang: 'Enkele deur < 1.2m'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useLocalCalc, setUseLocalCalc] = useState(true);

  // Lokale berekening (werkt zonder backend)
  const berekenLokaal = () => {
    const { doorgang_uitgang_m, type_uitgang, locatie, aantal_verdiepingen,
            breedte_trap_m, oppervlakte_bordes_m2, doorgang_naar_trap_m, type_doorgang } = formData;

    // Ontruimingstijd op basis van locatie
    const ontruimingstijden = {
      'Veiligheidsvluchtroute': 30,
      'Extra beschermde vluchtroute': 20,
      'Beschermde vluchtroute': 15
    };
    const ontruimingstijd = ontruimingstijden[locatie] || 15;

    // Doorstroomcapaciteit per type
    const getDoorstroom = (type, breedte) => {
      if (type.includes('Enkele')) return breedte * 45;
      return breedte * 90;
    };

    // Bereken doorstroom uitgang
    const doorstroomUitgang = getDoorstroom(type_uitgang, doorgang_uitgang_m);

    // Bereken doorstroom deur naar trap
    const doorstroomDeur = getDoorstroom(type_doorgang, doorgang_naar_trap_m);

    // Doorstroom trap
    const doorstroomTrap = breedte_trap_m * 60;

    // Max totaal (BBL lid 1)
    const maxTotaal = Math.floor(doorstroomUitgang * ontruimingstijd);

    // Opvangcapaciteit per verdieping (BBL lid 2)
    const opvangBordes = oppervlakte_bordes_m2 * 3;
    const aantalTreden = 20; // standaard
    const opvangTreden = aantalTreden * breedte_trap_m * 2;
    const opvangTotaal = opvangBordes + opvangTreden;

    // Max per verdieping = min(opvang, doorstroom deur)
    const maxPerVerdieping = Math.floor(Math.min(opvangTotaal, doorstroomDeur));

    // Bepaal bottleneck
    let bottleneck = 'Uitgang trappenhuis';
    const minDoorstroom = Math.min(doorstroomUitgang, doorstroomDeur, doorstroomTrap);
    if (minDoorstroom === doorstroomDeur) bottleneck = 'Toegangsdeur verdieping';
    else if (minDoorstroom === doorstroomTrap) bottleneck = 'Trapbreedte';

    return {
      success: true,
      max_personen_totaal: maxTotaal,
      max_personen_per_verdieping: maxPerVerdieping,
      bottleneck: bottleneck,
      doorstroom_uitgang_per_min: doorstroomUitgang,
      doorstroom_deur_per_min: doorstroomDeur,
      doorstroom_trap_per_min: doorstroomTrap,
      ontruimingstijd_min: ontruimingstijd,
      opvangcapaciteit: Math.floor(opvangTotaal)
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (useLocalCalc) {
      // Lokale berekening
      const localResult = berekenLokaal();
      setResult(localResult);
      setLoading(false);
      return;
    }

    // API aanroep
    try {
      const response = await fetch(`${API_URL}/api/bereken/snel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('API fout');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('API niet bereikbaar. Lokale berekening wordt gebruikt.');
      const localResult = berekenLokaal();
      setResult(localResult);
    }

    setLoading(false);
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <svg viewBox="0 0 64 64" width="48" height="48">
              <rect x="12" y="16" width="40" height="44" fill="#1565C0" rx="2"/>
              <rect x="16" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="28" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="40" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="16" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="28" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="40" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>
              <rect x="26" y="50" width="12" height="10" fill="#0D47A1" rx="1"/>
              <path d="M54 48 L58 48 L58 52 L62 52 L62 56 L54 56 Z" fill="#FF6F00"/>
              <path d="M56 36 L62 42 L59 42 L59 46 L53 46 L53 42 L50 42 Z" fill="#2E7D32"/>
            </svg>
          </div>
          <div>
            <h1>Evacuatie Calculator</h1>
            <p>BBL Art. 4.80/4.81 - Opvang- en doorstroomcapaciteit</p>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <div className="grid">
            {/* Input Form */}
            <div className="card">
              <h2>Invoer</h2>
              <form onSubmit={handleSubmit}>
                <div className="form-section">
                  <h3>Trappenhuis uitgang</h3>

                  <div className="form-group">
                    <label>Breedte uitgang (m)</label>
                    <input
                      type="number"
                      name="doorgang_uitgang_m"
                      value={formData.doorgang_uitgang_m}
                      onChange={handleChange}
                      step="0.05"
                      min="0.5"
                      max="5"
                    />
                  </div>

                  <div className="form-group">
                    <label>Type uitgang</label>
                    <select name="type_uitgang" value={formData.type_uitgang} onChange={handleChange}>
                      <option>Enkele deur &lt; 1.2m</option>
                      <option>Dubbele deur &gt;= 1.2m</option>
                      <option>Vrije doorgang</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Type vluchtroute</label>
                    <select name="locatie" value={formData.locatie} onChange={handleChange}>
                      <option>Veiligheidsvluchtroute</option>
                      <option>Extra beschermde vluchtroute</option>
                      <option>Beschermde vluchtroute</option>
                    </select>
                    <small>Bepaalt ontruimingstijd (30/20/15 min)</small>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Trappenhuis eigenschappen</h3>

                  <div className="form-group">
                    <label>Aantal verdiepingen</label>
                    <input
                      type="number"
                      name="aantal_verdiepingen"
                      value={formData.aantal_verdiepingen}
                      onChange={handleChange}
                      min="1"
                      max="60"
                    />
                  </div>

                  <div className="form-group">
                    <label>Breedte trap (m)</label>
                    <input
                      type="number"
                      name="breedte_trap_m"
                      value={formData.breedte_trap_m}
                      onChange={handleChange}
                      step="0.05"
                      min="0.8"
                      max="3"
                    />
                  </div>

                  <div className="form-group">
                    <label>Oppervlakte bordes (m²)</label>
                    <input
                      type="number"
                      name="oppervlakte_bordes_m2"
                      value={formData.oppervlakte_bordes_m2}
                      onChange={handleChange}
                      step="0.5"
                      min="0"
                    />
                  </div>
                </div>

                <div className="form-section">
                  <h3>Toegang per verdieping</h3>

                  <div className="form-group">
                    <label>Breedte toegangsdeur (m)</label>
                    <input
                      type="number"
                      name="doorgang_naar_trap_m"
                      value={formData.doorgang_naar_trap_m}
                      onChange={handleChange}
                      step="0.05"
                      min="0.5"
                      max="5"
                    />
                  </div>

                  <div className="form-group">
                    <label>Type toegangsdeur</label>
                    <select name="type_doorgang" value={formData.type_doorgang} onChange={handleChange}>
                      <option>Enkele deur &lt; 1.2m</option>
                      <option>Dubbele deur &gt;= 1.2m</option>
                      <option>Vrije doorgang</option>
                    </select>
                  </div>
                </div>

                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Berekenen...' : 'Bereken capaciteit'}
                </button>
              </form>
            </div>

            {/* Results */}
            <div className="card">
              <h2>Resultaten</h2>

              {error && <div className="alert alert-warning">{error}</div>}

              {result ? (
                <div className="results">
                  <div className="result-card result-primary">
                    <div className="result-label">Max personen totaal</div>
                    <div className="result-value">{result.max_personen_totaal}</div>
                    <div className="result-sub">BBL Art. 4.81 lid 1</div>
                  </div>

                  <div className="result-card result-secondary">
                    <div className="result-label">Max per verdieping</div>
                    <div className="result-value">{result.max_personen_per_verdieping}</div>
                    <div className="result-sub">BBL Art. 4.81 lid 2</div>
                  </div>

                  <div className="result-details">
                    <h3>Details berekening</h3>
                    <table>
                      <tbody>
                        <tr>
                          <td>Ontruimingstijd</td>
                          <td><strong>{result.ontruimingstijd_min} minuten</strong></td>
                        </tr>
                        <tr>
                          <td>Doorstroom uitgang</td>
                          <td>{result.doorstroom_uitgang_per_min?.toFixed(0)} pers/min</td>
                        </tr>
                        <tr>
                          <td>Doorstroom toegangsdeur</td>
                          <td>{result.doorstroom_deur_per_min?.toFixed(0)} pers/min</td>
                        </tr>
                        <tr>
                          <td>Doorstroom trap</td>
                          <td>{result.doorstroom_trap_per_min?.toFixed(0)} pers/min</td>
                        </tr>
                        <tr>
                          <td>Opvangcapaciteit/verd.</td>
                          <td>{result.opvangcapaciteit} personen</td>
                        </tr>
                        <tr className="highlight">
                          <td>Bottleneck</td>
                          <td><strong>{result.bottleneck}</strong></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div className="info-box">
                    <h4>Uitleg</h4>
                    <p>
                      <strong>Max totaal (lid 1):</strong> Maximaal aantal personen dat binnen
                      de ontruimingstijd het gebouw kan verlaten via de uitgang van het trappenhuis.
                    </p>
                    <p>
                      <strong>Max per verdieping (lid 2):</strong> Maximaal aantal personen per
                      verdieping dat binnen 1 minuut het brandcompartiment kan verlaten via de
                      toegangsdeur naar het trappenhuis.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <p>Vul de gegevens in en klik op "Bereken capaciteit"</p>
                </div>
              )}
            </div>
          </div>

          {/* BBL Info */}
          <div className="card info-card">
            <h2>BBL Standaardwaarden</h2>
            <div className="info-grid">
              <div>
                <h4>Doorstroomcapaciteit</h4>
                <ul>
                  <li>Enkele deur (&lt;1.2m): <strong>45 pers/m/min</strong></li>
                  <li>Dubbele deur/vrij: <strong>90 pers/m/min</strong></li>
                  <li>Trap: <strong>60 pers/m/min</strong></li>
                </ul>
              </div>
              <div>
                <h4>Opvangcapaciteit</h4>
                <ul>
                  <li>Bordes: <strong>3 pers/m²</strong></li>
                  <li>Treden: <strong>2 pers/trede/m breedte</strong></li>
                </ul>
              </div>
              <div>
                <h4>Ontruimingstijden (Art. 4.81 lid 1)</h4>
                <ul>
                  <li>Veiligheidsvluchtroute: <strong>30 min</strong></li>
                  <li>Extra beschermde vluchtroute: <strong>20 min</strong></li>
                  <li>Beschermde vluchtroute: <strong>15 min</strong></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Evacuatie Calculator - BBL Art. 4.80/4.81</p>
      </footer>
    </div>
  );
}

export default App;
