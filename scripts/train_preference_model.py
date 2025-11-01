import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib # For saving the model and vectorizer
import logging

# This allows the script to import from the 'app' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

from app.database.session import SessionLocal
from app.models.prompt import UsageAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define where to save the trained model artifacts
ARTIFACTS_DIR = os.path.join("server", "app", "ml_models")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "preference_model.joblib")
VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib")

def load_feedback_data(db: Session) -> pd.DataFrame:
    """
    Queries the database and loads all usage_analytics data with explicit feedback
    into a pandas DataFrame.
    """
    logging.info("Loading feedback data from the database...")
    query = db.query(UsageAnalytics).filter(UsageAnalytics.user_action.isnot(None))
    df = pd.read_sql(query.statement, query.session.bind)
    logging.info(f"Found {len(df)} records with user feedback.")
    return df

def train_model():
    """
    Main function to load data, train the preference model, and save the artifacts.
    """
    db = SessionLocal()
    df = load_feedback_data(db)
    db.close()

    # We need at least a few samples of both 'accepted' and 'rejected' to train
    required_samples = 5
    if df_joined.empty or df_joined['user_action'].nunique() < 2 or len(df_joined) < required_samples:
        logging.warning(f"Not enough diverse data. Need at least {required_samples} samples with both 'accepted' and 'rejected' actions.")
        return

    # --- Feature Engineering ---
    # We combine the original and enhanced prompts to create our feature set 'X'.
    # We assume 'accepted' is the positive class.
    df['text_features'] = df['prompt.original_prompt'] + " " + df['prompt.enhanced_prompt'] # This requires a join in the query, let's fix the query.
    
    # --- Corrected Data Loading with Join ---
    logging.info("Re-loading data with a join to get prompt text...")
    db = SessionLocal()
    # Correct query that joins UsageAnalytics with PromptCache
    query = db.query(
        UsageAnalytics.user_action, 
        models.PromptCache.original_prompt, 
        models.PromptCache.enhanced_prompt
    ).join(models.PromptCache, UsageAnalytics.prompt_id == models.PromptCache.id).filter(
        UsageAnalytics.user_action.isnot(None)
    )
    df_joined = pd.read_sql(query.statement, query.session.bind)
    db.close()
    
    if df_joined.empty or df_joined['user_action'].nunique() < 2 or len(df_joined) < 10:
        logging.warning("Not enough diverse data to train after join. Aborting.")
        return
        
    df_joined['text_features'] = df_joined['original_prompt'] + " " + df_joined['enhanced_prompt']

    # Our target variable 'y'
    y = df_joined['user_action'].apply(lambda x: 1 if x == 'accepted' else 0)
    X = df_joined['text_features']

    # --- Model Training ---
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Vectorize the text data using TF-IDF
    vectorizer = TfidfVectorizer(max_features=3000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train a simple Logistic Regression model
    model = LogisticRegression(random_state=42)
    model.fit(X_train_vec, y_train)

    # --- Evaluation ---
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Model training complete. Test accuracy: {accuracy:.4f}")

    # --- Saving Artifacts ---
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logging.info(f"Model saved to {MODEL_PATH}")
    logging.info(f"Vectorizer saved to {VECTORIZER_PATH}")


if __name__ == "__main__":
    from app.models import prompt as models # Add model import here for the corrected query
    train_model()