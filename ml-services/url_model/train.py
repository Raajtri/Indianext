import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

from lightgbm import LGBMClassifier


print("Loading datasets...")

data1 = pd.read_csv("../../datasets/malicious_phish.csv")
data2 = pd.read_csv("../../datasets/data.csv")


# Label encoding
data1["label"] = data1["type"].apply(lambda x: 0 if x == "benign" else 1)
data2["label"] = data2["label"].apply(lambda x: 0 if x == "good" else 1)


data1 = data1[["url", "label"]]
data2 = data2[["url", "label"]]


# Merge datasets
print("Merging datasets...")
data = pd.concat([data1, data2], ignore_index=True)


# Clean data
data["url"] = data["url"].astype(str).str.lower().str.strip()
data = data.drop_duplicates()


print("Dataset size:", len(data))
print("\nClass distribution:")
print(data["label"].value_counts())


# Shuffle
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

X = data["url"]
y = data["label"]


# Train test split
print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# TF-IDF
print("\nVectorizing URLs...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3,5),
    max_features=30000,
    min_df=3
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print("Feature matrix:", X_train_vec.shape)


# Train model
print("\nTraining LightGBM model...")

model = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.1,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1
)

model.fit(X_train_vec, y_train)


# Evaluation
print("\nEvaluating model...\n")

pred = model.predict(X_test_vec)

print(classification_report(y_test, pred))


# Save model
print("\nSaving model...")

joblib.dump(model, "url_model.pkl")
joblib.dump(vectorizer, "url_vectorizer.pkl")

print("Model saved successfully!")