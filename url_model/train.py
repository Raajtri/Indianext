import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

from lightgbm import LGBMClassifier


print("Loading datasets...")

# ==========================
# DATASET 1
# malicious_phish.csv
# ==========================

data1 = pd.read_csv("../../datasets/malicious_phish.csv")

data1["label"] = data1["type"].apply(lambda x: 0 if x == "benign" else 1)

data1 = data1[["url", "label"]]


# ==========================
# DATASET 2
# data.csv
# ==========================

data2 = pd.read_csv("../../datasets/data.csv")

data2["label"] = data2["label"].apply(lambda x: 0 if x == "good" else 1)

data2 = data2[["url", "label"]]


# ==========================
# MERGE DATASETS
# ==========================

print("Merging datasets...")

data = pd.concat([data1, data2], ignore_index=True)

print("Total dataset size:", len(data))


# ==========================
# SHUFFLE DATA
# ==========================

data = data.sample(frac=1, random_state=42).reset_index(drop=True)

X = data["url"].astype(str)
y = data["label"]


# ==========================
# TRAIN TEST SPLIT
# ==========================

print("Splitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==========================
# TF-IDF FEATURE EXTRACTION
# ==========================

print("Vectorizing URLs...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3,5),
    max_features=30000,
    min_df=3
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("Feature matrix shape:", X_train_vec.shape)


# ==========================
# TRAIN LIGHTGBM MODEL
# ==========================

print("Training LightGBM model...")

model = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.1,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1
)

model.fit(X_train_vec, y_train)


# ==========================
# MODEL EVALUATION
# ==========================

print("\nEvaluating model...")

pred = model.predict(X_test_vec)

print("\nModel Performance:\n")
print(classification_report(y_test, pred))


# ==========================
# SAVE MODEL
# ==========================

print("\nSaving model...")

joblib.dump(model, "url_model.pkl")
joblib.dump(vectorizer, "url_vectorizer.pkl")

print("\nModel saved successfully!")
