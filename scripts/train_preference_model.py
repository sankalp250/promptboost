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
    Requires at least 50 accepted and 50 rejected samples.
    """
    db = SessionLocal()
    df = load_feedback_data(db)
    db.close()

    # Check for minimum requirements: at least 50 accepted and 50 rejected
    if df.empty:
        logging.warning("No feedback data found. Please generate some feedback data first.")
        return
    
    # Count samples by action
    action_counts = df['user_action'].value_counts()
    accepted_count = action_counts.get('accepted', 0)
    rejected_count = action_counts.get('rejected', 0)
    
    logging.info(f"Found {accepted_count} accepted and {rejected_count} rejected samples.")
    
    min_samples_per_class = 50
    if accepted_count < min_samples_per_class or rejected_count < min_samples_per_class:
        logging.warning(
            f"Not enough data to train. Need at least {min_samples_per_class} accepted and "
            f"{min_samples_per_class} rejected samples. Current: {accepted_count} accepted, "
            f"{rejected_count} rejected."
        )
        return

    # --- Feature Engineering ---
    df['text_features'] = df['original_prompt'] + " " + df['enhanced_prompt']
    y = df['user_action'].apply(lambda x: 1 if x == 'accepted' else 0)
    X = df['text_features']

    # --- Model Training ---
    # For small datasets (e.g., <= 20 samples), train on all data without splitting.
    # This gives the model maximum data to learn from.
    use_train_test_split = len(df) > 20
    
    if use_train_test_split:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            logging.info(f"Using train/test split: {len(X_train)} train, {len(X_test)} test")
        except ValueError:
            logging.warning("Could not perform stratified split. Training on all data instead.")
            use_train_test_split = False
    
    if not use_train_test_split:
        # Small dataset: train on all data
        X_train = X
        y_train = y
        X_test = X  # Use same data for "validation"
        y_test = y
        logging.info(f"Small dataset detected ({len(df)} samples). Training on all data.")
    
    # Adjust TF-IDF parameters for small datasets
    max_features = min(500, len(X_train))  # Reduce features for small datasets
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words='english',
        min_df=1,  # Lower threshold for small datasets
        max_df=0.95
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Use LogisticRegression with balanced class weights
    model = LogisticRegression(
        random_state=42,
        class_weight='balanced',
        max_iter=1000,
        C=1.0  # Regularization strength
    )
    model.fit(X_train_vec, y_train)

    # --- Evaluation ---
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Also show per-class accuracy
    accepted_mask = y_test == 1
    rejected_mask = y_test == 0
    accepted_acc = accuracy_score(y_test[accepted_mask], y_pred[accepted_mask]) if accepted_mask.sum() > 0 else 0
    rejected_acc = accuracy_score(y_test[rejected_mask], y_pred[rejected_mask]) if rejected_mask.sum() > 0 else 0
    
    logging.info(f"Model training complete.")
    logging.info(f"Overall accuracy: {accuracy:.4f}")
    logging.info(f"Accepted class accuracy: {accepted_acc:.4f}")
    logging.info(f"Rejected class accuracy: {rejected_acc:.4f}")

    # --- Saving Artifacts ---
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logging.info(f"Model and vectorizer saved successfully to {ARTIFACTS_DIR}")
    logging.info("✅ Training complete! The quality filter will now use this model.")

if __name__ == "__main__":
    train_model()
