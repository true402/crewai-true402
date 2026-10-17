# crewai-true402

[![PyPI version](https://img.shields.io/pypi/v/crewai-true402)](https://pypi.org/project/crewai-true402/) &nbsp; **Stable · production-ready** — semver-stable public API (v1.0).

**[true402](https://true402.dev) tools for [CrewAI](https://www.crewai.com)** — give an agent a pre-trade **rug/honeypot check** for Base tokens AND **search/SEO data** (backlinks, keyword volume, rankings, keyword ideas), each paid for per call over [x402](https://x402.org) (USDC on Base). No accounts, no API keys — the wallet is the identity. Most of the on-chain safety checks have a **free daily trial**, so those tools work out of the box with no wallet configured; `true402_deployer_check` and the search/SEO tools are paid from the first call.

## Install

```bash
pip install crewai-true402
```

## Use

```python
from crewai import Agent
from crewai_true402 import true402_tools

# Reads PAYER_PRIVATE_KEY from the env (a Base wallet holding a little USDC).
# Omit the key to rely on the free daily trial for most safety stalls (not true402_deployer_check).
tools = true402_tools()

trader = Agent(
    role="Base memecoin trader",
    goal="Only buy tokens that pass an on-chain safety check",
    tools=tools,
    backstory="You never ape into a token before rug-checking it.",
)
```

The agent gets ten tools:

| Tool | What | Price |
|------|------|-------|
| `true402_token_report` | Composite **avoid/caution/ok** verdict — honeypot buy/sell simulation + liquidity + ownership + recent rug activity. Call **before buying**. | ~$0.01 |
| `true402_token_safety` | Structural safety score 0–100 + flags (honeypot sim, liquidity, mint/ownership). | ~$0.005 |
| `true402_address_safety` | Profile + risk for any address before you send/approve/call it (EOA vs contract, balances, proxy detection). | ~$0.005 |
| `true402_tx_preflight` | Check an **unsigned** transaction before signing: does it revert, does it grant an unlimited approval, has the counterparty been draining liquidity. Takes no key and no signature. | ~$0.008 |
| `true402_liquidity_history` | What already happened to a token's liquidity — every removal with amount/block/tx, plus the tokens drained in the same transaction. | ~$0.005 |
| `true402_deployer_check` | Deployer wallet reputation — age, contracts shipped, fresh-throwaway flag — to catch serial ruggers. **No free trial — paid from the first call.** | ~$0.008 |
| `true402_backlinks` | A domain's backlink profile — referring domains/pages, dofollow split, authority rank, spam score. | ~$0.10 |
| `true402_keyword_volume` | Search volume, CPC, competition and trend for **up to 200 keywords in one call** — priced per call, not per keyword, so batch the list. | ~$0.15 |
| `true402_ranked_keywords` | Which keywords a domain already ranks for, with position and the ranking URL. Works on any domain — competitor research as much as self-audit. | ~$0.05 |
| `true402_keyword_ideas` | Related and long-tail keyword ideas for a seed term, with search volume and intent. | ~$0.05 |

## Configuration

`true402_tools()` reads the environment, or pass a `PayOpts`:

```python
from crewai_true402 import true402_tools, PayOpts

tools = true402_tools(PayOpts(
    payer_private_key="0x…",   # a Base wallet with a little USDC (gas is sponsored; USDC only)
    max_amount_usd=0.25,        # hard per-call ceiling — refuses to sign a 402 demanding more
))
```

| Env var | Default | Meaning |
|---------|---------|---------|
| `PAYER_PRIVATE_KEY` | — | Base wallet key that signs x402 payments (needs USDC, not ETH). Unset → free trial only. |
| `TRUE402_BASE_URL` | `https://true402.dev/api` | Override to point at a self-hosted instance. |
| `BASE_RPC_URL` | `https://mainnet.base.org` | Base RPC for the balance pre-check. |

## Safety

The client **refuses to sign** anything that isn't USDC-on-Base within `max_amount_usd` (default $0.25, above the server's own $0.20 per-request ceiling so a legitimately-priced stall is never blocked) — so a rogue or compromised endpoint can't make your agent authorize an unexpected asset, network, or amount. The private key is used only to sign locally; it never leaves the process.

## Links

- Live check in your browser: <https://true402.dev/check>
- API reference: <https://true402.dev/docs/api> · OpenAPI: <https://true402.dev/openapi.json>
- Also available: [LangChain](https://www.npmjs.com/package/@true402.dev/langchain) · [MCP server](https://www.npmjs.com/package/@true402.dev/mcp-server) · [CLI](https://www.npmjs.com/package/@true402.dev/rugcheck)

**Checking tokens by hand?** Send any Base token address to [@True402bot](https://t.me/True402bot) on Telegram — same on-chain checks, free, no wallet.

## Guides

- [Add a rug check to a CrewAI agent](https://true402.dev/guides/rug-check-crewai-agent)
- [Token price and rug risk in one call](https://true402.dev/guides/token-price-and-rug-check-api)
- [The x402 protocol, explained](https://true402.dev/guides/what-is-x402)

## Also available for

MCP (Claude Code / Desktop, Cursor, **Hermes**) · **Hermes Agent** · **OpenClaw** · **ElizaOS** ·
**LangChain** · **CrewAI** · **Vercel AI SDK** · **Coinbase AgentKit** · **Virtuals GAME** · CLI —
same on-chain checks, one install command each:
**[true402.dev/integrations](https://true402.dev/integrations)**

## Paying, exactly

The rules below are the service's, not this package's — they bite whatever client you use, and they
are the ones that surprise people writing their own payer.

- **Pay the EXACT amount quoted in the 402.** Underpaying is rejected. **Overpaying is refused with
  402 and never credited** — settlement submits the signed value and there is no refund path, so a
  surplus would simply be swept. Equality is also what binds an authorization to the resource it was
  quoted for.
- **One authorization buys exactly one response.** A replay is refused, not double-charged.
- **You are charged on success only.** Settlement is submitted only when the endpoint returns 2xx; if
  it errors or times out, your signed authorization is never submitted, so there is nothing to refund.
- Some endpoints serve a few free calls per day per client IP, with no wallet. The per-operation
  description in the [OpenAPI spec](https://true402.dev/api/openapi.json) says which.

Full rules: **[true402.dev/terms](https://true402.dev/terms)** · what is logged and kept:
**[true402.dev/privacy](https://true402.dev/privacy)**

## License

MIT
