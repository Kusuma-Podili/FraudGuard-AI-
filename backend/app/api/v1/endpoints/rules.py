"""Dynamic Fraud Rules, AST Condition Builder, and Backtesting Endpoints."""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user, get_current_risk_officer
from backend.app.models.user import User
from backend.app.models.rule import FraudRule, RuleAction
from backend.app.models.transaction import TransactionRecord
from backend.app.schemas.rule import (
    RuleCreate, RuleUpdate, RuleResponse,
    RuleDryRunRequest, RuleDryRunResponse,
    RuleBacktestRequest, RuleBacktestResponse
)
from backend.app.schemas.common import APIResponse
from backend.app.services.rule_evaluator import SafeRuleEvaluator
from backend.app.services.decision_engine import get_decision_engine
from backend.app.core.exceptions import EntityNotFoundException

router = APIRouter()


@router.get("", response_model=APIResponse[List[RuleResponse]], summary="List Business Rules")
async def list_rules(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all configured fraud rules ordered by priority."""
    query = select(FraudRule).order_by(FraudRule.priority.asc())
    if category:
        query = query.where(FraudRule.category == category)
    if is_active is not None:
        query = query.where(FraudRule.is_active == is_active)

    result = await db.execute(query)
    rules = result.scalars().all()
    return APIResponse(data=rules)


@router.post("", response_model=APIResponse[RuleResponse], status_code=status.HTTP_201_CREATED, summary="Create Rule")
async def create_rule(
    rule_in: RuleCreate,
    db: AsyncSession = Depends(get_db),
    risk_officer: User = Depends(get_current_risk_officer)
):
    """Create and validate a new fraud rule."""
    # Validate condition expression with mock context
    mock_ctx = {
        "amount": 100.0, "velocity_1h": 1, "velocity_24h": 2, "is_foreign": False,
        "failed_pin_attempts_24h": 0, "merchant_category": "GROCERY",
        "distance_from_home_km": 10.0, "travel_velocity_kmh": 0.0,
        "is_impossible_travel": False, "amount_ratio_to_mean_30d": 1.0
    }
    try:
        SafeRuleEvaluator.evaluate_expression(rule_in.condition_expression, mock_ctx)
    except Exception as err:
        return APIResponse(success=False, message=f"Invalid rule syntax: {str(err)}", data=None)

    new_rule = FraudRule(
        rule_code=rule_in.rule_code,
        name=rule_in.name,
        description=rule_in.description,
        category=rule_in.category,
        condition_expression=rule_in.condition_expression,
        action=RuleAction(rule_in.action),
        priority=rule_in.priority,
        is_active=rule_in.is_active,
        created_by_user_id=risk_officer.id
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)

    # Hot-reload decision engine in-memory cache
    all_rules_res = await db.execute(select(FraudRule).where(FraudRule.is_active == True))
    active_rules = [
        {"rule_code": r.rule_code, "name": r.name, "condition": r.condition_expression, "action": r.action.value, "priority": r.priority}
        for r in all_rules_res.scalars().all()
    ]
    get_decision_engine().update_rules_cache(active_rules)

    return APIResponse(data=new_rule, message="Rule created and deployed successfully")


@router.post("/dry-run", response_model=APIResponse[RuleDryRunResponse], summary="Dry-Run Test Rule Expression")
async def dry_run_rule(
    payload: RuleDryRunRequest,
    user: User = Depends(get_current_user)
):
    """Test AST rule condition against sample transaction payload."""
    start_t = time.perf_counter()
    try:
        is_match, matched_vars = SafeRuleEvaluator.evaluate_expression(payload.condition_expression, payload.sample_transaction)
        elapsed_us = (time.perf_counter() - start_t) * 1_000_000.0

        resp = RuleDryRunResponse(
            is_triggered=is_match,
            evaluation_result=is_match,
            latency_microseconds=round(elapsed_us, 2),
            matched_variables=matched_vars,
            error_message=None
        )
        return APIResponse(data=resp)
    except Exception as e:
        resp = RuleDryRunResponse(
            is_triggered=False,
            evaluation_result=False,
            latency_microseconds=0.0,
            matched_variables={},
            error_message=str(e)
        )
        return APIResponse(data=resp, success=False, message="Rule evaluation failed")


@router.post("/backtest", response_model=APIResponse[RuleBacktestResponse], summary="Backtest Rule on Historical Data")
async def backtest_rule(
    payload: RuleBacktestRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Run historical simulation of proposed rule to calculate catch rate and false positive impact."""
    stmt = select(TransactionRecord).order_by(TransactionRecord.created_at.desc()).limit(payload.historical_samples_count)
    result = await db.execute(stmt)
    records = result.scalars().all()

    total_eval = len(records)
    triggered = 0
    fraud_caught = 0
    fp_count = 0

    for rec in records:
        ctx = {
            "amount": rec.amount,
            "velocity_1h": 2,
            "failed_pin_attempts_24h": 0,
            "merchant_category": rec.merchant_category,
            "country_code": rec.country_code,
            "is_impossible_travel": False,
            "travel_velocity_kmh": 0.0,
            "amount_ratio_to_mean_30d": 1.2
        }
        try:
            is_match, _ = SafeRuleEvaluator.evaluate_expression(payload.condition_expression, ctx)
            if is_match:
                triggered += 1
                if rec.is_fraud == 1:
                    fraud_caught += 1
                else:
                    fp_count += 1
        except Exception:
            continue

    trigger_pct = (triggered / max(total_eval, 1)) * 100.0
    catch_rate = (fraud_caught / max(triggered, 1)) * 100.0
    fpr = (fp_count / max(total_eval, 1)) * 100.0

    resp = RuleBacktestResponse(
        total_evaluated=total_eval,
        total_triggered=triggered,
        trigger_percentage=round(trigger_pct, 2),
        fraud_catch_rate=round(catch_rate, 2),
        false_positive_rate=round(fpr, 2),
        estimated_monthly_decline_volume=triggered * 30
    )
    return APIResponse(data=resp, message="Backtest completed")
