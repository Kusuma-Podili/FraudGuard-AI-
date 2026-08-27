# FraudGuard AI: REST & WebSocket API Reference

The FraudGuard AI API is versioned under `/api/v1` and adheres to RFC 7807 problem details error standards.

---

## Base URLs
- **REST Endpoints**: `http://localhost:8000/api/v1`
- **WebSocket Streaming**: `ws://localhost:8000/api/v1/simulation/ws`
- **OpenAPI Interactive Docs**: `http://localhost:8000/api/v1/docs`

---

## Authentication & RBAC

All protected endpoints require an `Authorization: Bearer <JWT_TOKEN>` header.

### 1. User Login
- **Method**: `POST`
- **Path**: `/auth/login/json`
- **Request Body**:
```json
{
  "email": "analyst@fraudguard.ai",
  "password": "Analyst@FraudGuard2026"
}
```
- **Response** `200 OK`:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "USR_ANALYST_01",
    "role": "FRAUD_ANALYST",
    "full_name": "Jane Doe"
  }
}
```

---

## Real-Time Transaction Scoring Gateway (<20ms SLA)

### 2. Score Single Transaction
- **Method**: `POST`
- **Path**: `/transactions/score`
- **Request Body**:
```json
{
  "card_id": "CARD_4829_1092",
  "amount": 1850.00,
  "currency": "USD",
  "merchant_id": "M_APPLE_NYC_01",
  "merchant_name": "Apple Fifth Avenue",
  "merchant_category": "ELECTRONICS",
  "entry_mode": "CNP",
  "card_type": "CREDIT",
  "card_network": "VISA",
  "latitude": 40.7638,
  "longitude": -73.9729,
  "country_code": "US",
  "device_fingerprint": "DEV_SAFARI_M3_09",
  "ip_address": "72.229.28.185",
  "failed_pin_attempts_24h": 0
}
```
- **Response** `200 OK`:
```json
{
  "success": true,
  "data": {
    "transaction_id": "TX_9281983012",
    "decision_action": "ALLOW",
    "risk_score": 0.042,
    "risk_tier": "LOW",
    "confidence_level": "HIGH",
    "triggered_rules": [],
    "model_breakdown": {
      "xgboost": 0.041,
      "lightgbm": 0.038,
      "catboost": 0.045,
      "random_forest": 0.040,
      "autoencoder": 0.050,
      "isolation_forest": 0.050,
      "graph_syndicate": 0.020
    },
    "is_anomaly": false,
    "is_impossible_travel": false,
    "requires_step_up_auth": false,
    "latency_ms": 1.42,
    "evaluated_at": "2026-08-27T10:14:02Z"
  }
}
```

---

## Explainable AI (XAI) & SHAP Attributions

### 3. Explain Transaction Decision
- **Method**: `POST`
- **Path**: `/explain`
- **Request Body**:
```json
{
  "transaction_id": "TX_9281983012",
  "transaction_payload": {
    "amount": 3400.00,
    "merchant_category": "ELECTRONICS",
    "failed_pin_attempts_24h": 2
  }
}
```
- **Response** `200 OK`:
```json
{
  "success": true,
  "data": {
    "transaction_id": "TX_9281983012",
    "risk_score": 0.892,
    "base_value": 0.050,
    "decision_action": "DECLINE",
    "top_risk_factors": ["failed_pin_attempts_24h", "amount", "velocity_1h"],
    "top_protective_factors": ["entry_mode_CHIP"],
    "waterfall": [
      {
        "feature": "failed_pin_attempts_24h",
        "value": 2,
        "shap_value": 0.421,
        "direction": "INCREASES_RISK",
        "impact_pct": 42.1
      }
    ],
    "counterfactuals": [
      {
        "feature_name": "failed_pin_attempts_24h",
        "original_value": 2,
        "recommended_value": 0,
        "change_description": "Complete 3DS biometric challenge to clear authentication lock.",
        "is_actionable": true
      }
    ]
  }
}
```
