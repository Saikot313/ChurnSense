import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8000";

const defaultForm = {
  CreditScore: 650,
  Geography: "France",
  Gender: "Male",
  Age: 35,
  Tenure: 5,
  Balance: 75000,
  NumOfProducts: 2,
  HasCrCard: 1,
  IsActiveMember: 1,
  EstimatedSalary: 50000,
  SatisfactionScore: 3,
  CardType: "GOLD",
  PointEarned: 400,
};

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [options, setOptions] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API}/options`).then((res) => setOptions(res.data)).catch(() => {});
  }, []);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "number" ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post(`${API}/predict`, form);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "API connection failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const riskColor = { Low: "#00c896", Medium: "#f5a623", High: "#e63946" };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">⬡</span>
            <span className="logo-text">ChurnSense</span>
          </div>
          <p className="header-sub">Bank Customer Churn Prediction</p>
        </div>
      </header>

      <main className="main">
        <div className="card form-card">
          <h2 className="card-title">Customer Profile</h2>
          <p className="card-desc">Fill in the customer details to predict churn risk.</p>

          <div className="form-grid">
            <div className="field">
              <label>Credit Score</label>
              <input type="number" name="CreditScore" value={form.CreditScore} onChange={handleChange} min={300} max={850} />
            </div>
            <div className="field">
              <label>Geography</label>
              <select name="Geography" value={form.Geography} onChange={handleChange}>
                {(options?.Geography || ["France", "Germany", "Spain"]).map((g) => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Gender</label>
              <select name="Gender" value={form.Gender} onChange={handleChange}>
                {(options?.Gender || ["Female", "Male"]).map((g) => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Age</label>
              <input type="number" name="Age" value={form.Age} onChange={handleChange} min={18} max={100} />
            </div>
            <div className="field">
              <label>Tenure (years)</label>
              <input type="number" name="Tenure" value={form.Tenure} onChange={handleChange} min={0} max={10} />
            </div>
            <div className="field">
              <label>Balance ($)</label>
              <input type="number" name="Balance" value={form.Balance} onChange={handleChange} min={0} />
            </div>
            <div className="field">
              <label>Number of Products</label>
              <select name="NumOfProducts" value={form.NumOfProducts} onChange={handleChange}>
                {[1,2,3,4].map((n) => <option key={n}>{n}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Has Credit Card</label>
              <select name="HasCrCard" value={form.HasCrCard} onChange={handleChange}>
                <option value={1}>Yes</option>
                <option value={0}>No</option>
              </select>
            </div>
            <div className="field">
              <label>Active Member</label>
              <select name="IsActiveMember" value={form.IsActiveMember} onChange={handleChange}>
                <option value={1}>Yes</option>
                <option value={0}>No</option>
              </select>
            </div>
            <div className="field">
              <label>Estimated Salary ($)</label>
              <input type="number" name="EstimatedSalary" value={form.EstimatedSalary} onChange={handleChange} min={0} />
            </div>
            <div className="field">
              <label>Satisfaction Score (1–5)</label>
              <select name="SatisfactionScore" value={form.SatisfactionScore} onChange={handleChange}>
                {[1,2,3,4,5].map((n) => <option key={n}>{n}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Card Type</label>
              <select name="CardType" value={form.CardType} onChange={handleChange}>
                {(options?.CardType || ["DIAMOND","GOLD","PLATINUM","SILVER"]).map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Points Earned</label>
              <input type="number" name="PointEarned" value={form.PointEarned} onChange={handleChange} min={0} />
            </div>
          </div>

          <button className="predict-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? <span className="spinner" /> : "Predict Churn Risk"}
          </button>

          {error && <div className="error-box">{error}</div>}
        </div>

        {result && (
          <div className="card result-card" style={{ borderTop: `4px solid ${riskColor[result.risk_level]}` }}>
            <h2 className="card-title">Prediction Result</h2>
            <div className="result-main">
              <div className="result-verdict" style={{ color: riskColor[result.risk_level] }}>
                {result.churn_prediction === 1 ? "⚠ Will Churn" : "✓ Will Stay"}
              </div>
              <p className="result-message">{result.message}</p>
            </div>
            <div className="result-stats">
              <div className="stat">
                <span className="stat-label">Churn Probability</span>
                <span className="stat-value">{(result.churn_probability * 100).toFixed(1)}%</span>
                <div className="prob-bar">
                  <div className="prob-fill" style={{ width: `${result.churn_probability * 100}%`, background: riskColor[result.risk_level] }} />
                </div>
              </div>
              <div className="stat">
                <span className="stat-label">Risk Level</span>
                <span className="risk-badge" style={{ background: riskColor[result.risk_level] + "22", color: riskColor[result.risk_level] }}>
                  {result.risk_level} Risk
                </span>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        Built with FastAPI + Random Forest + React · Model Accuracy: 86.7%
      </footer>
    </div>
  );
}
