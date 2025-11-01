import joblib
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define where the trained model artifacts are located
# This path is relative to the 'server' directory
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "ml_models"
MODEL_PATH = ARTIFACTS_DIR / "preference_model.joblib"
VECTORIZER_PATH = ARTIFACTS_DIR / "tfidf_vectorizer.joblib"

# A dictionary to hold our loaded models in memory
ml_artifacts = {
    "model": None,
    "vectorizer": None
}

def load_ml_models():
    """
    Loads the ML model and vectorizer from disk into memory.
    This function is called once at server startup.
    """
    logging.info("Attempting to load ML preference model...")
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        logging.warning("ML model or vectorizer file not found. The quality filter will be disabled. Run the training script to generate these files.")
        return

    try:
        ml_artifacts["model"] = joblib.load(MODEL_PATH)
        ml_artifacts["vectorizer"] = joblib.load(VECTORIZER_PATH)
        logging.info("Successfully loaded ML preference model and vectorizer.")
    except Exception as e:
        logging.error(f"Failed to load ML artifacts: {e}")
        # Ensure they are reset on failure
        ml_artifacts["model"] = None
        ml_artifacts["vectorizer"] = None

def predict_acceptance_probability(original_prompt: str, enhanced_prompt: str) -> float:
    """
    Predicts the probability that a user will 'accept' an enhancement.
    Returns a probability between 0.0 and 1.0.
    """
    model = ml_artifacts.get("model")
    vectorizer = ml_artifacts.get("vectorizer")

    # If the model isn't loaded, default to a high probability (graceful degradation)
    if model is None or vectorizer is None:
        return 1.0

    try:
        # Combine prompts to create the feature
        text_feature = original_prompt + " " + enhanced_prompt
        
        # Transform the feature using the loaded vectorizer
        vectorized_text = vectorizer.transform([text_feature])
        
        # Predict the probability. predict_proba returns [[P(reject), P(accept)]]
        probability_of_acceptance = model.predict_proba(vectorized_text)[0][1]
        
        logging.info(f"Predicted acceptance probability: {probability_of_acceptance:.4f}")
        return probability_of_acceptance
    except Exception as e:
        logging.error(f"Error during ML model prediction: {e}")
        # Default to a safe, high probability on failure
        return 1.0