import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

from xgboost import XGBClassifier   # NEW MODEL

DATA_PATH = "../../datasets/SpamAssasin.csv"

print("Loading dataset...")

data = pd.read_csv(DATA_PATH)

print("Dataset columns:", data.columns)

# Fill missing values
data["subject"] = data["subject"].fillna("")
data["body"] = data["body"].fillna("")

# Combine email text
data["text"] = data["subject"] + " " + data["body"]

# Keep only required columns
data = data[["text", "label"]]

# Convert labels
data["label"] = data["label"].map({"ham":0,"spam":1}).fillna(data["label"])

print("Dataset size:", len(data))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    data["text"],
    data["label"],
    test_size=0.2,
    random_state=42
)

vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)

print("Vectorizing emails...")

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("Training XGBoost model...")

model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train_vec, y_train)

pred = model.predict(X_test_vec)

print("\nModel Performance:\n")
print(classification_report(y_test, pred))

# Save model
joblib.dump(model, "phishing_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("\nModel saved successfully!")