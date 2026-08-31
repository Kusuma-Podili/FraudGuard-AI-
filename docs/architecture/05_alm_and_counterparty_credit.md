# Asset-Liability Management (ALM) & Counterparty Credit Risk Architecture

## Overview
Provides central treasury, capital markets, and chief risk officer desks with real-time liquidity stress testing, interest rate risk modeling, and bilateral derivative exposure calculations.

### Core Engines
1. **Liquidity Risk & ALM (`backend/app/domain/liquidity_risk/`)**:
   - Basel III HQLA Optimizer & 30-Day Liquidity Coverage Ratio.
   - Non-Maturity Deposit (NMD) behavioral runoff decay modeling.
   - Intraday Fedwire / CHIPS payment queue gridlock resolver.
2. **Counterparty Credit Risk & XVA (`backend/app/domain/counterparty_credit/`)**:
   - Potential Future Exposure (PFE) Monte Carlo diffusion models.
   - Comprehensive XVA Engine (Credit, Debit, Funding, Margin, and Capital Valuation Adjustments).
   - ISDA Standard Initial Margin Model (SIMM) Delta/Vega/Curvature calculations.
