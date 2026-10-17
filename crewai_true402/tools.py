"""true402 tools for CrewAI — pay-per-call on-chain safety AND search/SEO data for agents over x402.

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


class _HistoryInput(BaseModel):
    token: str = Field(..., description="A Base ERC-20 token contract address (0x…)")
    limit: Optional[int] = Field(None, description="Max removal events to return (1–200, default 50)")


class _BacklinksInput(BaseModel):
    target: str = Field(..., description="A domain, or any URL on it")


class _KeywordVolumeInput(BaseModel):
    keywords: list[str] = Field(..., description="Up to 200 keywords — batch them, see the tool description")
    location: Optional[int] = Field(None, description="Location code (default 2840 = United States)")
    language: Optional[str] = Field(None, description="Language code (default 'en')")


class _RankedKeywordsInput(BaseModel):
    target: str = Field(..., description="A domain to pull organic rankings for")
    limit: Optional[int] = Field(None, description="Max keywords to return (1–200, default 50)")
    location: Optional[int] = Field(None, description="Location code (default 2840 = United States)")
    language: Optional[str] = Field(None, description="Language code (default 'en')")


class _KeywordIdeasInput(BaseModel):
    seed: str = Field(..., description="A seed keyword or short phrase (max 80 chars)")
    limit: Optional[int] = Field(None, description="Max ideas to return (1–200, default 50)")
    location: Optional[int] = Field(None, description="Location code (default 2840 = United States)")
    language: Optional[str] = Field(None, description="Language code (default 'en')")


class _PreflightInput(BaseModel):
    """An UNSIGNED transaction. No private key and no signature are ever sent — see the tool description."""

    from_: str = Field(..., alias="from", description="Sender address (0x…). Asserted, never proven.")
    to: str = Field(..., description="Destination contract or address (0x…)")
    data: Optional[str] = Field(None, description="Calldata hex (0x…). Omit for a plain native transfer.")
    value: Optional[str] = Field(None, description="Native value in wei, decimal string. Default 0.")

    model_config = {"populate_by_name": True}


class _StallTool(BaseTool):
    """Base for a true402 stall exposed as a CrewAI tool."""

    path: str
    input_key: str
    # Holds the payer's PRIVATE KEY. Pydantic would otherwise print it in repr() and emit it from
    # model_dump()/model_dump_json() — which agent frameworks call when they log, trace or cache a tool.
    opts: PayOpts = Field(exclude=True, repr=False)

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


class LiquidityHistoryTool(_StallTool):
    name: str = "true402_liquidity_history"
    description: str = (
        "What has ALREADY happened to a Base token's liquidity, from true402's own DEX archive: every "
        "removal event with the amount, block and transaction hash, plus the other tokens drained in "
        "the SAME transaction (one actor, several pools). A live honeypot simulation cannot see this — "
        "a pool drained last month simulates fine today if it was re-seeded. Every answer carries the "
        "block range the index covers, so \"none observed\" is not a claim of safety. ~$0.005 USDC over x402."
    )
    args_schema: Type[BaseModel] = _HistoryInput
    path: str = "/v1/base/liquidity-history"
    input_key: str = "token"

    def _run(self, **kwargs) -> str:
        body = {"token": kwargs.get("token")}
        if kwargs.get("limit") is not None:
            body["limit"] = kwargs["limit"]
        return json.dumps(pay_stall(self.path, body, self.opts))


class TxPreflightTool(_StallTool):
    name: str = "true402_tx_preflight"
    description: str = (
        "Check a Base transaction BEFORE signing it. Send the UNSIGNED transaction (from, to, data, "
        "value) and get three lenses: a simulation against current state (does it revert?), the decoded "
        "intent (is this an unlimited approval that outlives the trade?), and the counterparty's "
        "liquidity-removal history. Takes NO private key and NO signature, so it cannot broadcast or "
        "front-run the transaction it inspects. Never returns \"safe\" — a clean result means these "
        "checks found nothing, and every response states its limits. Call this LAST, immediately before "
        "signing. ~$0.008 USDC over x402."
    )
    args_schema: Type[BaseModel] = _PreflightInput
    path: str = "/v1/base/tx-preflight"
    input_key: str = "from"

    def _run(self, **kwargs) -> str:
        # The field is `from_` in Python (a reserved word) and `from` on the wire.
        body = {"from": kwargs.get("from") or kwargs.get("from_"), "to": kwargs.get("to")}
        for k in ("data", "value"):
            if kwargs.get(k) is not None:
                body[k] = kwargs[k]
        return json.dumps(pay_stall(self.path, body, self.opts))


class BacklinksTool(_StallTool):
    name: str = "true402_backlinks"
    description: str = (
        "A domain's backlink profile: referring domains and pages, the dofollow split that actually "
        "carries authority, authority rank and spam score. The one SEO signal an agent cannot compute "
        "from a page fetch — it needs a crawled link graph. ~$0.10 USDC over x402."
    )
    args_schema: Type[BaseModel] = _BacklinksInput
    path: str = "/v1/backlinks"
    input_key: str = "target"


class KeywordVolumeTool(_StallTool):
    name: str = "true402_keyword_volume"
    description: str = (
        "Search volume, CPC, competition and 12-month trend for keywords. Priced PER CALL, not per "
        "keyword: send up to 200 keywords in ONE call for the same price as one keyword — looping one "
        "keyword per call buys identical data for up to 200x the money, so batch the whole list. "
        "~$0.15 USDC over x402."
    )
    args_schema: Type[BaseModel] = _KeywordVolumeInput
    path: str = "/v1/keyword-volume"
    input_key: str = "keywords"

    def _run(self, **kwargs) -> str:
        body: dict = {"keywords": kwargs.get("keywords")}
        for k in ("location", "language"):
            if kwargs.get(k) is not None:
                body[k] = kwargs[k]
        return json.dumps(pay_stall(self.path, body, self.opts))


class RankedKeywordsTool(_StallTool):
    name: str = "true402_ranked_keywords"
    description: str = (
        "Which keywords a domain already ranks for in organic search, with position and the exact URL "
        "that ranks. Works on any domain, so it is competitor research as much as self-audit. "
        "~$0.05 USDC over x402."
    )
    args_schema: Type[BaseModel] = _RankedKeywordsInput
    path: str = "/v1/ranked-keywords"
    input_key: str = "target"

    def _run(self, **kwargs) -> str:
        body: dict = {"target": kwargs.get("target")}
        for k in ("limit", "location", "language"):
            if kwargs.get(k) is not None:
                body[k] = kwargs[k]
        return json.dumps(pay_stall(self.path, body, self.opts))


class KeywordIdeasTool(_StallTool):
    name: str = "true402_keyword_ideas"
    description: str = (
        "Related and long-tail keyword ideas for a seed term, each with search volume and search "
        "intent — measured candidates rather than ones a language model invented. "
        "~$0.05 USDC over x402."
    )
    args_schema: Type[BaseModel] = _KeywordIdeasInput
    path: str = "/v1/keyword-ideas"
    input_key: str = "seed"

    def _run(self, **kwargs) -> str:
        body: dict = {"seed": kwargs.get("seed")}
        for k in ("limit", "location", "language"):
            if kwargs.get(k) is not None:
                body[k] = kwargs[k]
        return json.dumps(pay_stall(self.path, body, self.opts))


def true402_tools(opts: Optional[PayOpts] = None) -> list[BaseTool]:
    """The true402 on-chain safety AND search/SEO tools, ready to hand to a CrewAI Agent.

    Pass a PayOpts, or leave None to read PAYER_PRIVATE_KEY / TRUE402_BASE_URL / BASE_RPC_URL from the
    environment. Stalls with a free daily trial (token safety/report, address safety) work even with no
    wallet configured — they return a real result until the trial is exhausted, then require payment.
    The search/SEO tools (backlinks, keyword volume/ranked/ideas) have no free trial — they are paid
    from the first call.
    """
    o = opts or PayOpts.from_env()
    return [
        TokenReportTool(opts=o),
        TokenSafetyTool(opts=o),
        AddressSafetyTool(opts=o),
        DeployerCheckTool(opts=o),
        LiquidityHistoryTool(opts=o),
        TxPreflightTool(opts=o),
        BacklinksTool(opts=o),
        KeywordVolumeTool(opts=o),
        RankedKeywordsTool(opts=o),
        KeywordIdeasTool(opts=o),
    ]
