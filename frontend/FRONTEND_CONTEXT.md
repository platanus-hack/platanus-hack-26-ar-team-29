# Contexto Frontend

Este documento resume el estado actual del frontend y el contexto de producto/arquitectura que hay que respetar al seguir construyendo la app.

## Resumen

- El frontend vive en `frontend/`.
- Es una app Next.js con App Router, TypeScript, React 19 y Tailwind CSS 4.
- El producto pertenece al track `Agentic Money` de Platanus Hack 26.
- La idea de producto, segun los artifacts, es una app financiera donde el chat con un agente es la superficie principal para consultar, planificar y aprobar acciones sobre dinero.
- La implementacion actual es una base inicial: homepage default de Next y una ruta `/chat` con chat mockeado y confirmacion de trade mockeada.
- El diseño objetivo esta documentado principalmente en `.opencode/artifacts/02-2_frontend_design.md` y el contrato REST/WebSocket en `.opencode/artifacts/02-3_api_surface.md`.

## Stack

- Framework: `next@16.3.0-canary.17`.
- Runtime UI: `react@19.2.6`, `react-dom@19.2.6`.
- Lenguaje: TypeScript 5 con `strict: true`.
- Estilos: Tailwind CSS 4 via `@tailwindcss/postcss`.
- Lint: ESLint 9 con `eslint-config-next/core-web-vitals` y `eslint-config-next/typescript`.
- Package manager observado: existe `bun.lock`, aunque `package.json` expone scripts genericos.

## Comandos

Ejecutar desde `frontend/`:

```bash
bun dev
bun run build
bun run lint
```

Tambien deberian funcionar los equivalentes npm porque los scripts estan en `package.json`:

```bash
npm run dev
npm run build
npm run lint
```

## Regla Importante De Next.js

`frontend/AGENTS.md` advierte que esta version de Next.js tiene cambios breaking y no debe asumirse compatibilidad con conocimiento anterior. Antes de escribir codigo que dependa de APIs/convenios especificos de Next, revisar la guia relevante en `node_modules/next/dist/docs/`.

## Estructura Actual

```text
frontend/
  app/
    globals.css
    layout.tsx
    page.tsx
    chat/
      api.ts
      page.tsx
      types.ts
      _components/
        ChatInput.tsx
        ChatMessage.tsx
        ChatThread.tsx
        TradeConfirmation.tsx
        TradeSummary.tsx
  public/
    file.svg
    globe.svg
    next.svg
    vercel.svg
    window.svg
  AGENTS.md
  CLAUDE.md
  README.md
  eslint.config.mjs
  next.config.ts
  package.json
  postcss.config.mjs
  tsconfig.json
```

## Estado De Implementacion

### `app/layout.tsx`

- Define el layout raiz.
- Importa `Geist` y `Geist_Mono` desde `next/font/google`.
- Define metadata default de create-next-app: `Create Next App`.
- Usa `html lang="en"`, aunque el producto objetivo es Spanish-first (`es-AR`).
- Aplica clases globales de altura completa y antialiasing.

### `app/page.tsx`

- Todavia es la pantalla default de create-next-app.
- No refleja el producto final.
- Es candidata a reemplazarse por una landing, dashboard o redireccion a `/chat`, segun la decision de producto.

### `app/globals.css`

- Importa Tailwind con `@import "tailwindcss"`.
- Define variables `--background` y `--foreground`.
- Declara tokens Tailwind inline para colores y fuentes.
- Tiene soporte basico de dark mode via `prefers-color-scheme`.
- El `body` todavia fuerza `font-family: Arial, Helvetica, sans-serif`, lo que compite con las variables Geist configuradas.

### `app/chat/page.tsx`

- Es un Client Component (`"use client"`).
- Mantiene estado local de mensajes con `useState`.
- Seed inicial: bot mockeado con texto en ingles.
- `handleSend` agrega el mensaje de usuario, activa estado de typing y llama `sendChatMessage`.
- Si falla la llamada mock, agrega un mensaje de error generico.
- `setTradeStatus` actualiza un trade embebido en un mensaje a `confirmed` o `rejected`.
- Renderiza un contenedor responsive simple con header, thread y input.

### `app/chat/api.ts`

- No llama a backend real.
- Simula latencia con `setTimeout` de 800 ms.
- Devuelve respuestas aleatorias desde `CANNED_REPLIES`.
- Si el ultimo texto contiene `swap` o `trade`, devuelve un mensaje de bot con `trade` mockeado:
  - `fromTicker: USDC`
  - `fromAmount: 100`
  - `toTicker: ETH`
  - `toAmount: 0.025`
  - `valueUSD: 100`
- Tiene un comentario con el reemplazo esperado por `fetch("/api/chat")`, pero el contrato real de artifacts apunta a `/api/v1/chat/...`.

### `app/chat/types.ts`

- Define `ChatRole = "user" | "bot"`.
- Define `Message` con `id`, `role`, `content`, `createdAt` y opcional `trade`.
- Define `Trade` y `TradeStatus = "pending" | "confirmed" | "rejected"`.
- Estos tipos son utiles para el prototipo, pero no coinciden todavia con el contrato API final, que usa sesiones, mensajes, planes, steps, IDs UUID y timestamps ISO 8601.

### Componentes De Chat

- `ChatInput.tsx`: input controlado, trim de mensaje, boton disabled cuando `disabled` es true.
- `ChatThread.tsx`: lista mensajes, autoscroll con `useEffect` y render de typing indicator.
- `ChatMessage.tsx`: burbujas diferenciadas para usuario/bot y render especial si el mensaje trae `trade`.
- `TradeConfirmation.tsx`: tarjeta de confirmacion con botones `Reject` y `Confirm` cuando esta pendiente; luego muestra estado final.
- `TradeSummary.tsx`: formatea montos y USD en `en-US`; usa simbolos Unicode para flecha y aproximacion.

## Arquitectura Objetivo Del Producto

El frontend objetivo no es solo un chat. Segun `.opencode/artifacts/02-2_frontend_design.md`, la app debe pensarse como una aplicacion de chat con lentes financieros conectados.

Principios locked:

- Chat es la superficie universal y el control plane.
- Las tabs son proyecciones de estado: leen directo, pero las escrituras sensibles pasan por el agente y la ceremonia de aprobacion.
- Los planes son entidades first-class, no modales efimeros.
- Debe haber tiempo real via WebSocket; no polling client-side.
- Producto Spanish-first con registro argentino (`es-AR`).
- La UI debe ser provider-aware, no hardcodear Wallbit/Ethereum en componentes generales.
- La ceremonia de auditoria debe ser visible y facil de encontrar.

## Superficies Objetivo

Las superficies objetivo documentadas son 11:

| Superficie | Proposito |
| --- | --- |
| Chat | Conversacion, aprobacion de planes, streaming, audit replay |
| Home dashboard | Resumen financiero y actividad reciente |
| Balances | Saldos cash/stablecoin por proveedor y moneda |
| Holdings | Posiciones por proveedor/asset, P&L y allocation |
| Activity | Feed unificado de transacciones |
| Documents | Ingestion de PDFs/CSVs/recibos y clasificacion |
| Investment profile | Objetivos, reglas, riesgo y metricas del perfil |
| Tradebots | Bots, safeguards, ticks y planes generados |
| Pending plans | Inbox de planes pendientes o parcialmente fallidos |
| Provider connections | Conexion y estado de proveedores financieros |
| Agent activity / audit | Log de tool calls, provider calls y transiciones |

## Modelo De Escrituras

- Lecturas: REST snapshot inicial por tab.
- Updates: WebSocket con deltas por topico.
- Escrituras sensibles: mediadas por chat/agente y aprobacion de plan.
- Escrituras directas permitidas: metadata o acciones idempotentes de bajo riesgo, por ejemplo renombrar sesion, pausar sync, corregir label, refresh now.
- Las acciones financieras no deberian ejecutarse directamente desde un boton que llame a un endpoint de trade.

## Contrato API Objetivo

El contrato esta en `.opencode/artifacts/02-3_api_surface.md`.

Convenciones principales:

- Base REST: `/api/v1`.
- JSON en `snake_case`.
- Fechas ISO 8601 UTC con sufijo `Z`.
- IDs UUIDv4.
- Header de locale: `Accept-Language: es-AR`.
- Errores con envelope:

```json
{
  "error": {
    "code": "PLAN_PRECONDITION_FAILED",
    "message_es": "El plan ya no se puede ejecutar.",
    "message_en": "Plan can no longer execute.",
    "params": {},
    "details": null,
    "trace_id": "..."
  }
}
```

Endpoints relevantes para chat:

- `GET /api/v1/chat/sessions`
- `POST /api/v1/chat/sessions`
- `GET /api/v1/chat/sessions/{id}`
- `PATCH /api/v1/chat/sessions/{id}`
- `DELETE /api/v1/chat/sessions/{id}`
- `GET /api/v1/chat/sessions/{id}/messages`
- `POST /api/v1/chat/sessions/{id}/messages`
- `POST /api/v1/chat/sessions/{id}/attachments`

WebSocket objetivo:

- Endpoint: `wss://<host>/api/v1/ws`.
- Un socket por app, con multiplexing de topicos.
- Frames con `kind`, `topic`, `type`, `ts`, `seq`, `payload`.
- El cliente debe soportar `subscribe`, `unsubscribe`, `ack`, `error`, `ping`, `pong` y `resync`.

Topicos objetivo:

| Topico | Uso |
| --- | --- |
| `chat.<session_id>` | Tokens, mensajes, tool calls y propuestas de plan |
| `plan.<plan_id>` | Estado de plan y steps |
| `balance.<connection_id>` | Balances, posiciones, transacciones |
| `bot.<bot_id>` | Ticks y outcomes de tradebots |
| `ingest.<doc_id>` | Progreso de documentos |
| `connection.<connection_id>` | Estado/rate limit/credenciales |
| `notification.user` | Notificaciones proactivas |
| `plans.user` | Fan-in de planes del usuario |
| `bots.user` | Fan-in de bots del usuario |
| `connections.user` | Fan-in de conexiones del usuario |
| `ingests.user` | Fan-in de ingestas del usuario |

## Gap Entre Implementacion Actual Y Objetivo

- La UI esta mayormente en ingles; el objetivo es `es-AR`.
- No hay sistema i18n todavia.
- No hay routing para las 11 superficies objetivo.
- No hay layout de app con navegacion persistente.
- No hay sidebar de sesiones de chat.
- No hay backend real conectado.
- No hay WebSocket ni streaming.
- El trade actual es un objeto embebido en mensaje; el objetivo es `TradePlan` first-class con steps y estados.
- No hay persistencia de mensajes/sesiones.
- No hay manejo de auth/session.
- No hay estado global/cache para snapshots REST + deltas WS.
- No hay componentes compartidos de error/loading/empty states.
- No hay tests.
- `app/page.tsx` sigue siendo boilerplate.
- Metadata y `lang` siguen genericos.

## Recomendaciones Para Siguientes Cambios

1. Reemplazar `app/page.tsx` por una entrada real del producto o redireccion a `/chat`.
2. Cambiar metadata y `lang` a la identidad real del proyecto y `es-AR`.
3. Traducir el prototipo de chat a Spanish-first.
4. Separar tipos mock de tipos API objetivo para evitar acoplar el prototipo al contrato incompleto.
5. Introducir una capa `app/chat/api.ts` alineada a `/api/v1/chat/sessions` y `/messages` cuando exista backend.
6. Modelar `TradePlan` y `TradeStep` en vez de `trade` embebido cuando se implemente aprobacion real.
7. Definir layout persistente de app antes de crear tabs: navegacion, pending-plans badge, toast layer y chat control plane.
8. Crear una estrategia unica para REST snapshot + WebSocket deltas antes de implementar varias superficies.
9. Mantener componentes provider-aware: evitar condicionales hardcodeados por proveedor salvo en formularios especificos de conexion.
10. Evitar polling en tabs; usar WebSocket o refresh manual documentado.

## Archivos Analizados

- `frontend/package.json`
- `frontend/README.md`
- `frontend/AGENTS.md`
- `frontend/CLAUDE.md`
- `frontend/next.config.ts`
- `frontend/tsconfig.json`
- `frontend/eslint.config.mjs`
- `frontend/postcss.config.mjs`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`
- `frontend/app/globals.css`
- `frontend/app/chat/page.tsx`
- `frontend/app/chat/api.ts`
- `frontend/app/chat/types.ts`
- `frontend/app/chat/_components/ChatInput.tsx`
- `frontend/app/chat/_components/ChatMessage.tsx`
- `frontend/app/chat/_components/ChatThread.tsx`
- `frontend/app/chat/_components/TradeConfirmation.tsx`
- `frontend/app/chat/_components/TradeSummary.tsx`
- `.opencode/artifacts/02-2_frontend_design.md`
- `.opencode/artifacts/02-3_api_surface.md`
- `.opencode/artifacts/02_execution_plan.md`
- `.opencode/artifacts/03_build_log.md`
- `README.md`
- `platanus-hack-project.json`

## Nota Para Agentes/Desarrolladores

Antes de tocar frontend, leer este archivo, `frontend/AGENTS.md`, `.opencode/artifacts/02-2_frontend_design.md` y `.opencode/artifacts/02-3_api_surface.md`. Si hay conflicto entre el prototipo actual y los artifacts, tratar el prototipo como implementacion temporal y los artifacts como direccion de producto, salvo que el equipo decida lo contrario.
