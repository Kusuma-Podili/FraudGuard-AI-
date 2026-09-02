export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/api/v1/simulation/ws";

export const DEFAULT_THRESHOLDS = {
  REVIEW: 0.30,
  CHALLENGE: 0.65,
  DECLINE: 0.85,
};

export const MERCHANT_CATEGORIES = [
  "GROCERY",
  "ELECTRONICS",
  "LUXURY_JEWELRY",
  "GAMBLING",
  "CRYPTO_EXCHANGE",
  "GAS_STATION",
  "TRAVEL_AIRLINE",
  "RESTAURANT",
  "DIGITAL_GOODS",
  "GENERAL_RETAIL",
];

export const ATTACK_SCENARIOS = [
  {
    id: "CARD_TESTING",
    name: "Card Testing Probe Attack",
    description: "Rapid micro-authorizations (₹0.25 - ₹2.50) from rotating IPs to test card numbers",
    severity: "HIGH",
    color: "amber",
  },
  {
    id: "IMPOSSIBLE_TRAVEL",
    name: "Impossible Velocity Teleportation",
    description: "Physical POS authorization 5,000+ km away from cardholder home within 15 minutes",
    severity: "CRITICAL",
    color: "red",
  },
  {
    id: "ACCOUNT_TAKEOVER",
    name: "Account Takeover (ATO) Electronics Burst",
    description: "Sudden ₹3,500+ electronics purchase with new device fingerprint and address change",
    severity: "CRITICAL",
    color: "red",
  },
  {
    id: "CRYPTO_VELOCITY",
    name: "Offshore Crypto Cash-Out",
    description: "High-value ₹1,500+ withdrawal surge at offshore cryptocurrency exchange gateways",
    severity: "HIGH",
    color: "purple",
  },
  {
    id: "CREDENTIAL_STUFFING",
    name: "PIN / CVV Brute Force",
    description: "Successive authentication failures triggering instant security locks",
    severity: "HIGH",
    color: "blue",
  },
];
