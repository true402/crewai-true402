# crewai-true402

[![PyPI version](https://img.shields.io/pypi/v/crewai-true402)](https://pypi.org/project/crewai-true402/) &nbsp; **Stable · production-ready** — semver-stable public API (v1.0).

**[true402](https://true402.dev) tools for [CrewAI](https://www.crewai.com)** — give a Base trading agent a pre-trade **rug/honeypot check** it pays for per call over [x402](https://x402.org) (USDC on Base). No accounts, no API keys — the wallet is the identity. The safety checks have a **free daily trial**, so the tools work out of the box with no wallet configured.

## Install

```bash
pip install crewai-true402
```

## Use

```python
from crewai import Agent
from crewai_true402 import true402_tools

# Reads PAYER_PRIVATE_KEY from the env (a Base wallet holding a little USDC).
# Omit the key to rely on the free daily trial for the safety stalls.
tools = true402_tools()

trader = Agent(
    role="Base memecoin trader",
    goal="Only buy tokens that pass an on-chain safety check",
    tools=tools,
    backstory="You never ape into a token before rug-checking it.",
)
```

The agent gets four tools:

| Tool | What | Price |
|------|------|-------|
| `true402_token_report` | Composite **avoid/caution/ok** verdict — honeypot buy/sell simulation + liquidity + ownership + recent rug activity. Call **before buying**. | ~$0.01 |
| `true402_token_safety` | Structural safety score 0–100 + flags (honeypot sim, liquidity, mint/ownership). | ~$0.005 |
| `true402_address_safety` | Profile + risk for any address before you send/approve/call it (EOA vs contract, balances, proxy detection). | ~$0.005 |
| `true402_deployer_check` | Deployer wallet reputation — age, contracts shipped, fresh-throwaway flag — to catch serial ruggers. | ~$0.008 |

## Configuration

`true402_tools()` reads the environment, or pass a `PayOpts`:

```python
from crewai_true402 import true402_tools, PayOpts

tools = true402_tools(PayOpts(
    payer_private_key="0x…",   # a Base wallet with a little USDC (gas is sponsored; USDC only)
    max_amount_usd=0.10,        # hard per-call ceiling — refuses to sign a 402 demanding more
))
```

| Env var | Default | Meaning |
|---------|---------|---------|
| `PAYER_PRIVATE_KEY` | — | Base wallet key that signs x402 payments (needs USDC, not ETH). Unset → free trial only. |
| `TRUE402_BASE_URL` | `https://true402.dev/api` | Override to point at a self-hosted instance. |
| `BASE_RPC_URL` | `https://mainnet.base.org` | Base RPC for the balance pre-check. |

## Safety

The client **refuses to sign** anything that isn't USDC-on-Base within `max_amount_usd` (default $0.10) — so a rogue or compromised endpoint can't make your agent authorize an unexpected asset, network, or amount. The private key is used only to sign locally; it never leaves the process.

## Links

- Live check in your browser: <https://true402.dev/check>
- API reference: <https://true402.dev/docs/api> · OpenAPI: <https://true402.dev/openapi.json>
- Also available: [LangChain](https://www.npmjs.com/package/@true402.dev/langchain) · [MCP server](https://www.npmjs.com/package/@true402.dev/mcp-server) · [CLI](https://www.npmjs.com/package/@true402.dev/rugcheck)

**Checking tokens by hand?** Send any Base token address to [@True402bot](https://t.me/True402bot) on Telegram — same on-chain checks, free, no wallet.

## License

MIT
