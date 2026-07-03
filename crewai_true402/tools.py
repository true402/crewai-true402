"""true402 tools for CrewAI — pay-per-call on-chain safety for Base agents over x402.

    from crewai_true402 import true402_tools
    tools = true402_tools()  # reads PAYER_PRIVATE_KEY from the env

    agent = Agent(role="Trader", tools=tools, ...)
"""
from __future__ import annotations

import json
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .x402 import PayOpts, pay_stall


class _TokenInput(BaseModel):
    token: str = Field(..., description="A Base ERC-20 token contract address (0x…)")


class _AddressInput(BaseModel):
    address: str = Field(..., description="Any Base address (0x…) — an EOA or a contract")


class _StallTool(BaseTool):
    """Base for a true402 stall exposed as a CrewAI tool."""

    path: str
    input_key: str
    opts: PayOpts

    def _run(self, **kwargs) -> str:
        value = kwargs.get(self.input_key)
        result = pay_stall(self.path, {self.input_key: value}, self.opts)
        return json.dumps(result)


class TokenReportTool(_StallTool):
    name: str = "true402_token_report"
    description: str = (
        "Pre-trade rug/honeypot check for a Base ERC-20: a composite avoid/caution/ok verdict from an "
        "on-chain buy/sell honeypot simulation, liquidity depth, ownership/mint inspection, and recent "
        "rug activity. Call BEFORE buying a token. ~$0.01 USDC over x402."
    )
    args_schema: Type[BaseModel] = _TokenInput
    path: str = "/v1/base/token-report"
    input_key: str = "token"


class TokenSafetyTool(_StallTool):
    name: str = "true402_token_safety"
    description: str = (
        "Structural safety score (0–100) + flags for a Base ERC-20: honeypot simulation, liquidity, "
        "mint/ownership/blacklist. Lighter than token_report. ~$0.005 USDC over x402."
    )
    args_schema: Type[BaseModel] = _TokenInput
    path: str = "/v1/token-safety"
    input_key: str = "token"


class AddressSafetyTool(_StallTool):
    name: str = "true402_address_safety"
    description: str = (
        "Profile + risk for any Base address before you send to / approve / call it: EOA-vs-contract, "
        "ETH+USDC balance, activity, ownership, and upgradeable-proxy (EIP-1967) detection. "
        "~$0.005 USDC over x402."
    )
    args_schema: Type[BaseModel] = _AddressInput
    path: str = "/v1/base/address-safety"
    input_key: str = "address"


class DeployerCheckTool(_StallTool):
    name: str = "true402_deployer_check"
    description: str = (
        "Deployer reputation for a Base token: resolves who created it and that wallet's track record "
        "(age, contracts shipped, fresh-throwaway flag) to catch serial ruggers a structural check "
        "can't see. ~$0.008 USDC over x402."
    )
    args_schema: Type[BaseModel] = _TokenInput
    path: str = "/v1/base/deployer-check"
    input_key: str = "token"


def true402_tools(opts: Optional[PayOpts] = None) -> list[BaseTool]:
    """The four true402 safety tools, ready to hand to a CrewAI Agent.

    Pass a PayOpts, or leave None to read PAYER_PRIVATE_KEY / TRUE402_BASE_URL / BASE_RPC_URL from the
    environment. Stalls with a free daily trial (token safety/report, address safety) work even with no
    wallet configured — they return a real result until the trial is exhausted, then require payment.
    """
    o = opts or PayOpts.from_env()
    return [
        TokenReportTool(opts=o),
        TokenSafetyTool(opts=o),
        AddressSafetyTool(opts=o),
        DeployerCheckTool(opts=o),
    ]
