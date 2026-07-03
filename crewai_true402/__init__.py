"""true402 tools for CrewAI — pay-per-call on-chain rug/honeypot & address safety for Base AI agents
over x402 (USDC on Base, no account, no API key; the wallet is the identity).

    from crewai_true402 import true402_tools
    tools = true402_tools()
"""
from .tools import (
    AddressSafetyTool,
    DeployerCheckTool,
    TokenReportTool,
    TokenSafetyTool,
    true402_tools,
)
from .x402 import PayOpts, pay_stall, sign_payment

__version__ = "0.1.0"
__all__ = [
    "true402_tools",
    "TokenReportTool",
    "TokenSafetyTool",
    "AddressSafetyTool",
    "DeployerCheckTool",
    "PayOpts",
    "pay_stall",
    "sign_payment",
]
