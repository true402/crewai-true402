"""true402 tools for CrewAI — pay-per-call on-chain rug/honeypot & address safety, PLUS search/SEO
data (backlinks, keyword volume, ranked keywords, keyword ideas), for Base AI agents over x402
(USDC on Base, no account, no API key; the wallet is the identity).

    from crewai_true402 import true402_tools
    tools = true402_tools()
"""
from .tools import (
    AddressSafetyTool,
    BacklinksTool,
    DeployerCheckTool,
    KeywordIdeasTool,
    KeywordVolumeTool,
    LiquidityHistoryTool,
    RankedKeywordsTool,
    TokenReportTool,
    TokenSafetyTool,
    TxPreflightTool,
    true402_tools,
)
from .x402 import PayOpts, pay_stall, sign_payment

from ._client import VERSION as __version__  # one source; it had drifted to 1.2.1 against a published 1.3.0
__all__ = [
    "true402_tools",
    "TokenReportTool",
    "TokenSafetyTool",
    "AddressSafetyTool",
    "DeployerCheckTool",
    "LiquidityHistoryTool",
    "TxPreflightTool",
    "BacklinksTool",
    "KeywordVolumeTool",
    "RankedKeywordsTool",
    "KeywordIdeasTool",
    "PayOpts",
    "pay_stall",
    "sign_payment",
]
