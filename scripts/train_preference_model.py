import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import logging

# This allows the script to import from the 'app' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

from app.database.session import SessionLocal
# Correctly import models to use them in the query
from app.models import prompt as models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define artifact paths
ARTIFACTS_DIR = os.path.join("server", "app", "ml_models")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "preference_model.joblib")
VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib")

def load_feedback_data(db: Session) -> pd.DataFrame:
    """
    Queries the database with a join and loads all analytics data with explicit feedback
    into a pandas DataFrame.
    """
    logging.info("Loading feedback data with join from the database...")
    
    query = db.query(
        models.UsageAnalytics.user_action,
        models.PromptCache.original_prompt,
        models.PromptCache.enhanced_prompt
    ).join(
        models.PromptCache, models.UsageAnalytics.prompt_id == models.PromptCache.id
    ).filter(
        models.UsageAnalytics.user_action.isnot(None)
    )
    
    df = pd.read_sql(query.statement, query.session.bind)
    logging.info(f"Found {len(df)} records with user feedback.")
    return df

def train_model():
    """
    Main function to load data, train the preference model, and save the artifacts.
    """
    db = SessionLocal()
    df = load_feedback_data(db) # Now correctly using a single DataFrame 'df'
    db.close()

    required_samples = 5
    if df.empty or df['user_action'].nunique() < 2 or len(df) < required_samples:
        logging.warning(f"Not enough diverse data to train. Need at least {required_samples} samples with both 'accepted' and 'rejected' actions.")
        return

    # --- Feature Engineering ---
    df['text_features'] = df['original_prompt'] + " " + df['enhanced_prompt']
    y = df['user_action'].apply(lambda x: 1 if x == 'accepted' else 0)
    X = df['text_features']

    # --- Model Training ---
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    except ValueError:
        logging.warning("Could not perform stratified split. This usually means one class has only one sample. Try adding more diverse feedback.")
        return
        
    vectorizer = TfidfVectorizer(max_features=3000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(random_state=42, class_weight='balanced')
    model.fit(X_train_vec, y_train)

    # --- Evaluation ---
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Model training complete. Test accuracy: {accuracy:.4f}")

    # --- Saving Artifacts ---
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logging.info(f"Model and vectorizer saved successfully to {ARTIFACTS_DIR}")

if __name__ == "__main__":
    train_model()
