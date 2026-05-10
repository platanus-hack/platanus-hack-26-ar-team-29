# Atajo: Project Description

## The Vision
Managing multiple financial accounts, keeping track of balances, and executing trades across different platforms is traditionally fragmented and full of friction. **Atajo** (Spanish for "Shortcut") changes this paradigm by offering a unified, Spanish-first conversational AI agent that sits atop an account-agnostic personal finance backend.

Our goal is to let you manage your money, investments, and trades easily and without friction. Instead of navigating complex interfaces and multiple apps, **you can buy and sell assets with just one natural language message**. This is the core selling point of Atajo: simplifying complex financial interactions into an intuitive, chat-first experience.

## Key Selling Points
- **Frictionless Trading:** Execute multi-step trades and asset conversions just by asking. "Comprá 10 USD de Apple" (Buy 10 USD of Apple) is all it takes to initiate a secure trade plan.
- **Unified Financial Hub:** Atajo consolidates multiple financial platforms into one seamless interface. Starting with a robust Wallbit integration, you can view all your balances and transaction history in one single conversation.
- **Natural Language Interface:** Talk directly to your money. Whether you want to check your portfolio, move funds, or buy stocks, Atajo understands your intent and processes it in plain language.

## Implemented Features (MVP)
The current Minimum Viable Product successfully implements the following core features:

- **End-to-End Chat Interface:** A robust Next.js frontend that acts as the primary control plane, rendering conversations, typing indicators, and structured data cleanly.
- **Multi-step Plan Approvals:** Security is paramount. When you ask to move money or execute a trade, Atajo drafts a detailed execution plan. No financial action is ever taken until you explicitly review and click "Approve".
- **Real-time Streaming:** Both the agent's LLM generation (chat tokens) and every state change in a plan's execution are streamed directly to the frontend via WebSockets, providing immediate and transparent feedback.
- **Live Wallbit Integration:** Connects seamlessly to the Wallbit Dev API to fetch live balances and transaction feeds. 
- **Provider-Agnostic Architecture:** The backend uses a strictly layered hexagonal architecture. Adding a new provider (like an Ethereum wallet or another fintech platform) is simply a matter of dropping in a new adapter—the core chat and plan orchestration logic remains untouched.
