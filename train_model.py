import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import json

# ── 1. Load Data ──────────────────────────────────────────────────────────────
df = pd.read_csv("Customer-Churn-Records.csv")
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing values:\n", df.isnull().sum())
print("\nChurn distribution:\n", df['Exited'].value_counts())

# ── 2. Feature Selection ──────────────────────────────────────────────────────
# Drop irrelevant columns + Complain (data leakage — customer complains after churn decision, not before)
drop_cols = ['RowNumber', 'CustomerId', 'Surname', 'Complain']
df = df.drop(columns=drop_cols)

# ── 3. Encode Categorical Variables ──────────────────────────────────────────
le_geo = LabelEncoder()
le_gender = LabelEncoder()
le_card = LabelEncoder()

df['Geography'] = le_geo.fit_transform(df['Geography'])
df['Gender'] = le_gender.fit_transform(df['Gender'])
df['Card Type'] = le_card.fit_transform(df['Card Type'])

# Save label encoder classes for API use
encoder_info = {
    "Geography": le_geo.classes_.tolist(),
    "Gender": le_gender.classes_.tolist(),
    "Card Type": le_card.classes_.tolist()
}
with open("encoder_info.json", "w") as f:
    json.dump(encoder_info, f)

print("\nGeography classes:", le_geo.classes_)
print("Gender classes:", le_gender.classes_)
print("Card Type classes:", le_card.classes_)

# ── 4. Define Features & Target ───────────────────────────────────────────────
X = df.drop(columns=['Exited'])
y = df['Exited']

feature_names = X.columns.tolist()
print("\nFeatures used:", feature_names)

# ── 5. Train/Test Split ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 6. Scale Features ─────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ── 7. Train Models ───────────────────────────────────────────────────────────

# Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train_scaled, y_train)
lr_pred = lr.predict(X_test_scaled)
lr_acc = accuracy_score(y_test, lr_pred)
print(f"\nLogistic Regression Accuracy: {lr_acc:.4f}")

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)
rf_pred = rf.predict(X_test_scaled)
rf_acc = accuracy_score(y_test, rf_pred)
print(f"Random Forest Accuracy:       {rf_acc:.4f}")

# ── 8. Best Model Report ──────────────────────────────────────────────────────
best_model = rf if rf_acc >= lr_acc else lr
best_name = "Random Forest" if rf_acc >= lr_acc else "Logistic Regression"
best_pred = rf_pred if rf_acc >= lr_acc else lr_pred

print(f"\nBest Model: {best_name}")
print("\nClassification Report:")
print(classification_report(y_test, best_pred, target_names=["Not Churned", "Churned"]))

# ── 9. Feature Importance (Random Forest) ────────────────────────────────────
importances = rf.feature_importances_
feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
print("\nTop 5 Important Features:")
for feat, imp in feat_imp[:5]:
    print(f"  {feat}: {imp:.4f}")

# ── 10. Save Model & Scaler ───────────────────────────────────────────────────
joblib.dump(best_model, "churn_model.pkl")
joblib.dump(scaler, "scaler.pkl")

# Save feature names for API validation
with open("feature_names.json", "w") as f:
    json.dump(feature_names, f)

print("\nFiles saved:")
print("  churn_model.pkl")
print("  scaler.pkl")
print("  encoder_info.json")
print("  feature_names.json")
print("\nDone!")
