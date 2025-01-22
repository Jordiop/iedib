import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import joblib
import numpy as np
import os

def load_and_preprocess_data():
    os.makedirs('models', exist_ok=True)
    df = sns.load_dataset("penguins")
    df = df.dropna()
    X = df.drop('species', axis=1)
    y = df['species']
    le = LabelEncoder()
    y = le.fit_transform(y)
    cat_features = ['island', 'sex']
    num_features = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
    X_dict = X[cat_features].to_dict('records')
    dv = DictVectorizer(sparse=False)
    X_cat = dv.fit_transform(X_dict)
    scaler = StandardScaler()
    X_num = scaler.fit_transform(X[num_features])
    X_combined = np.hstack((X_num, X_cat))
    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y, test_size=0.2, random_state=42
    )
    joblib.dump(dv, 'models/dict_vectorizer.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    joblib.dump(le, 'models/label_encoder.joblib')
    return X_train, X_test, y_train, y_test

def train_models():
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    models = {
        'logistic': LogisticRegression(random_state=42),
        'svm': SVC(random_state=42),
        'decision_tree': DecisionTreeClassifier(random_state=42),
        'knn': KNeighborsClassifier()
    }
    for name, model in models.items():
        model.fit(X_train, y_train)
        joblib.dump(model, f'models/{name}_model.joblib')
        score = model.score(X_test, y_test)
        print(f"{name} accuracy: {score:.4f}")

if __name__ == "__main__":
    train_models()
