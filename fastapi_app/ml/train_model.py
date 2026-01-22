"""
Script to train fraud detection model.
Run this separately to generate model files.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_data(n_samples=10000):
    """Generate synthetic fraud detection data for training."""
    np.random.seed(42)
    
    # Generate features
    data = {
        'amount': np.random.exponential(scale=100, size=n_samples),
        'hour': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'is_weekend': np.random.randint(0, 2, n_samples),
        'is_night': np.random.randint(0, 2, n_samples),
        'day_of_month': np.random.randint(1, 32, n_samples),
        'txn_count_1h': np.random.poisson(lam=2, size=n_samples),
        'txn_count_24h': np.random.poisson(lam=10, size=n_samples),
        'merchant_category_encoded': np.random.randint(0, 10, n_samples),
        'merchant_risk_score': np.random.uniform(0, 1, n_samples),
        'country_encoded': np.random.randint(0, 4, n_samples),
        'is_foreign_transaction': np.random.randint(0, 2, n_samples),
        'device_risk_score': np.random.uniform(0, 1, n_samples),
        'transaction_type_encoded': np.random.randint(0, 6, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Add derived features
    df['log_amount'] = np.log1p(df['amount'])
    df['amount_bin'] = pd.cut(df['amount'], bins=[0, 10, 100, 1000, 10000, np.inf], labels=[0,1,2,3,4])
    df['txn_amount_24h'] = df['amount'] * df['txn_count_24h']
    df['avg_txn_amount_24h'] = df['txn_amount_24h'] / (df['txn_count_24h'] + 1)
    
    # Generate target (fraud label) based on features
    fraud_prob = (
        (df['amount'] > 500).astype(int) * 0.3 +
        (df['txn_count_1h'] > 5).astype(int) * 0.2 +
        (df['is_night'] == 1).astype(int) * 0.1 +
        (df['is_foreign_transaction'] == 1).astype(int) * 0.2 +
        df['merchant_risk_score'] * 0.2
    )
    
    df['is_fraud'] = (fraud_prob > np.random.uniform(0, 1, n_samples)).astype(int)
    
    logger.info(f"Generated {n_samples} samples with {df['is_fraud'].sum()} fraud cases ({df['is_fraud'].mean()*100:.2f}%)")
    
    return df

def train_model():
    """Train and save fraud detection model."""
    
    logger.info("Generating training data...")
    df = generate_synthetic_data(n_samples=10000)
    
    # Define features
    feature_cols = [
        'amount', 'log_amount', 'amount_bin',
        'hour', 'day_of_week', 'is_weekend', 'is_night', 'day_of_month',
        'txn_count_1h', 'txn_count_24h', 'txn_amount_24h', 'avg_txn_amount_24h',
        'merchant_category_encoded', 'merchant_risk_score',
        'country_encoded', 'is_foreign_transaction',
        'device_risk_score', 'transaction_type_encoded'
    ]
    
    X = df[feature_cols]
    y = df['is_fraud']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    logger.info("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Important Features:")
    print(feature_importance.head(10))
    
    # Save model and scaler
    models_dir = Path("ml/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "fraud_model.pkl"
    scaler_path = models_dir / "scaler.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    logger.info(f"Model saved to {model_path}")
    logger.info(f"Scaler saved to {scaler_path}")
    
    return model, scaler

if __name__ == "__main__":
    train_model()
