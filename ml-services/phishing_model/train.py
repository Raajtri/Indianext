import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

from xgboost import XGBClassifier


print("Loading datasets...")

datasets = []


# =========================
# CEAS Dataset
# =========================
df = pd.read_csv("../../datasets/CEAS_08.csv")

df["sender"] = df["sender"].fillna("").astype(str)
df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)
df["urls"] = df["urls"].fillna("").astype(str)

df["text"] = df["sender"] + " " + df["subject"] + " " + df["body"] + " " + df["urls"]

datasets.append(df[["text","label"]])


# =========================
# Enron Dataset
# =========================
df = pd.read_csv("../../datasets/Enron.csv")

df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)

df["text"] = df["subject"] + " " + df["body"]

datasets.append(df[["text","label"]])


# =========================
# Ling Dataset
# =========================
df = pd.read_csv("../../datasets/Ling.csv")

df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)

df["text"] = df["subject"] + " " + df["body"]

datasets.append(df[["text","label"]])


# =========================
# Nazario Dataset
# =========================
df = pd.read_csv("../../datasets/Nazario.csv")

df["sender"] = df["sender"].fillna("").astype(str)
df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)
df["urls"] = df["urls"].fillna("").astype(str)

df["text"] = df["sender"] + " " + df["subject"] + " " + df["body"] + " " + df["urls"]

datasets.append(df[["text","label"]])


# =========================
# Nigerian Fraud Dataset
# =========================
df = pd.read_csv("../../datasets/Nigerian_Fraud.csv")

df["sender"] = df["sender"].fillna("").astype(str)
df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)
df["urls"] = df["urls"].fillna("").astype(str)

df["text"] = df["sender"] + " " + df["subject"] + " " + df["body"] + " " + df["urls"]

datasets.append(df[["text","label"]])


# =========================
# SpamAssassin Dataset
# =========================
df = pd.read_csv("../../datasets/SpamAssasin.csv")

df["sender"] = df["sender"].fillna("").astype(str)
df["subject"] = df["subject"].fillna("").astype(str)
df["body"] = df["body"].fillna("").astype(str)
df["urls"] = df["urls"].fillna("").astype(str)

df["text"] = df["sender"] + " " + df["subject"] + " " + df["body"] + " " + df["urls"]

datasets.append(df[["text","label"]])


# =========================
# Phishing Email Dataset
# =========================
df = pd.read_csv("../../datasets/phishing_email.csv")

df.rename(columns={"text_combined":"text"}, inplace=True)

df["text"] = df["text"].fillna("").astype(str)

datasets.append(df[["text","label"]])


# =========================
# Merge All Datasets
# =========================
data = pd.concat(datasets, ignore_index=True)

print("Total dataset size:", len(data))


# =========================
# Train/Test Split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    data["text"],
    data["label"],
    test_size=0.2,
    random_state=42
)


# =========================
# TF-IDF Vectorizer
# =========================
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=8000
)

print("Vectorizing emails...")

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)


# =========================
# XGBoost Model
# =========================
print("Training XGBoost model...")

model = XGBClassifier(
    n_estimators=400,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

model.fit(X_train_vec, y_train)


# =========================
# Model Evaluation
# =========================
pred = model.predict(X_test_vec)

print("\nModel Performance:\n")
print(classification_report(y_test, pred))


# =========================
# Save Model
# =========================
joblib.dump(model, "phishing_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("\nModel saved successfully!")