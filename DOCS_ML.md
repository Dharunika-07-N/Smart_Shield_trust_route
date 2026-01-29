# 🧠 Smart Shield Trust Route - ML Documentation

## 🛰️ Model Architecture

### 1. Safety Classifier (Enhanced)
- **Algorithm**: Random Forest Classifier with Hyperparameter Tuning.
- **Purpose**: Classifies route segments into 5 safety levels (Very Unsafe to Very Safe).
- **Features**: crime rate, lighting, patrol frequency, traffic density, police/hospital proximity, plus engineered temporal and infrastructure features.
- **Health Monitoring**: Tracks prediction drift and accuracy degradation.

### 2. Delivery Time Predictor (Enhanced)
- **Algorithm**: XGBoost Regressor.
- **Purpose**: Precise ETA estimation with confidence intervals.
- **Features**: Route distance, traffic patterns, weather conditions (rain, snow, temperature), time of day, day of week.
- **Validation**: Uses Time-Series Cross-Validation to ensure reliability on temporal data.

### 3. SARSA RL Agent (Adaptive)
- **Algorithm**: Reinforcement Learning (SARSA).
- **Purpose**: Learns optimal route strategies from historical delivery outcomes.
- **Reward Function**: Weighted balance of time efficiency, safety score, delivery success, and distance.
- **Adaptation**: Uses experience replay and epsilon-decay to continuously optimize recommendations.

---

## 🛠️ Operational Workflows

### 🔄 Model Retraining
Models can be retrained via the API or Admin Dashboard:
- **Endpoint**: `POST /api/v1/training/retrain`
- **Background Task**: Training runs in the background to avoid blocking API requests.
- **Minimum Samples**: By default, requires 100 samples to initiate (configurable).

### 🧪 A/B Testing
Deploy new model versions safely using the experimentation framework:
1. Create experiment: `POST /api/v1/experiments/create`
2. Assign traffic: Hash-based splitting ensures a consistent user experience.
3. Compare performance: `GET /api/v1/experiments/compare/{name}`
4. Finalize: Stop experiment and set the winner as active.

---

## 📈 Monitoring & Governance

### Drift Detection
The system automatically monitors:
- **Feature Drift**: Changes in the distribution of input data (e.g., traffic patterns change over time).
- **Prediction Drift**: Significant shifts in model output distributions.
- **Performance Degradation**: Triggers alerts if MAE or Accuracy drops below thresholds (15% by default).

### Best Practices
1. **Data Freshness**: Retrain models at least once a month or after major local events.
2. **Version Control**: Every training run creates a new model version with associated metadata.
3. **Safety First**: Always compare new models (Group B) against the baseline (Group A) for at least 7 days before fully switching.

---

## 🚀 Deployment Guide

### Environment Setup
1. Ensure dependencies are installed: `pip install -r backend/requirements.txt`
2. Run database migrations: `python backend/update_schema.py`
3. Initialize base models: Trigger the `/training/retrain` endpoint or run initial training scripts.

### CI/CD Pipeline
- **Testing**: Automated tests run on every push to `main` or PR.
- **Linting**: Code quality checks ensure ML modules follow best practices.
- **Deployment**: Successful tests on `main` trigger production deployment.
