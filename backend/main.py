from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import json
import numpy as np

# ── Load Model & Artifacts ────────────────────────────────────────────────────
model = joblib.load("churn_model.pkl")
scaler = joblib.load("scaler.pkl")

with open("encoder_info.json") as f:
    encoder_info = json.load(f)

with open("feature_names.json") as f:
    feature_names = json.load(f)

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Bank Customer Churn Prediction API",
    description="Predicts whether a bank customer will churn based on their profile.",
    version="1.0.0"
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Schema ────────────────────────────────────────────────────────────
class CustomerData(BaseModel):
    CreditScore: int = Field(..., ge=300, le=850, example=650)
    Geography: str = Field(..., example="France")
    Gender: str = Field(..., example="Male")
    Age: int = Field(..., ge=18, le=100, example=35)
    Tenure: int = Field(..., ge=0, le=10, example=5)
    Balance: float = Field(..., ge=0, example=75000.0)
    NumOfProducts: int = Field(..., ge=1, le=4, example=2)
    HasCrCard: int = Field(..., ge=0, le=1, example=1)
    IsActiveMember: int = Field(..., ge=0, le=1, example=1)
    EstimatedSalary: float = Field(..., ge=0, example=50000.0)
    SatisfactionScore: int = Field(..., ge=1, le=5, example=3)
    CardType: str = Field(..., example="GOLD")
    PointEarned: int = Field(..., ge=0, example=400)

# ── Response Schema ───────────────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    churn_prediction: int
    churn_probability: float
    risk_level: str
    message: str

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Churn Prediction API is running!"}


@app.get("/options")
def get_options():
    """Returns valid options for categorical fields — used by React frontend."""
    return {
        "Geography": encoder_info["Geography"],
        "Gender": encoder_info["Gender"],
        "CardType": encoder_info["Card Type"],
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerData):
    # Validate categorical inputs
    if customer.Geography not in encoder_info["Geography"]:
        raise HTTPException(status_code=400, detail=f"Invalid Geography. Choose from {encoder_info['Geography']}")
    if customer.Gender not in encoder_info["Gender"]:
        raise HTTPException(status_code=400, detail=f"Invalid Gender. Choose from {encoder_info['Gender']}")
    if customer.CardType not in encoder_info["Card Type"]:
        raise HTTPException(status_code=400, detail=f"Invalid CardType. Choose from {encoder_info['Card Type']}")

    # Encode categorical values
    geo_encoded = encoder_info["Geography"].index(customer.Geography)
    gender_encoded = encoder_info["Gender"].index(customer.Gender)
    card_encoded = encoder_info["Card Type"].index(customer.CardType)

    # Build feature array in correct order
    features = np.array([[
        customer.CreditScore,
        geo_encoded,
        gender_encoded,
        customer.Age,
        customer.Tenure,
        customer.Balance,
        customer.NumOfProducts,
        customer.HasCrCard,
        customer.IsActiveMember,
        customer.EstimatedSalary,
        customer.SatisfactionScore,
        card_encoded,
        customer.PointEarned,
    ]])

    # Scale & Predict
    features_scaled = scaler.transform(features)
    prediction = int(model.predict(features_scaled)[0])
    probability = float(model.predict_proba(features_scaled)[0][1])

    # Risk level
    if probability < 0.3:
        risk_level = "Low"
    elif probability < 0.6:
        risk_level = "Medium"
    else:
        risk_level = "High"

    message = "This customer is likely to churn." if prediction == 1 else "This customer is likely to stay."

    return PredictionResponse(
        churn_prediction=prediction,
        churn_probability=round(probability, 4),
        risk_level=risk_level,
        message=message
    )
