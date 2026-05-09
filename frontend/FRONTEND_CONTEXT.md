# Contexto Frontend

Este documento resume el estado actual del frontend y el contexto de producto/arquitectura que hay que respetar al seguir construyendo la app.

## Resumen

- El frontend vive en `frontend/`.
- Es una app Next.js con App Router, TypeScript, React 19 y Tailwind CSS 4.
- El producto pertenece al track `Agentic Money` de Platanus Hack 26.
- La idea de producto, segun los artifacts, es una app financiera donde el chat con un agente es la superficie principal para consultar, planificar y aprobar acciones sobre dinero.
- La implementacion actual muestra el chat real integrado con backend directamente en `/`.
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

## Variables De Entorno Frontend

No guardar valores secretos en el repo. Para conectar contra el backend local:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
# opcional; si no se define se deriva desde NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

La integracion actual no manda token porque el backend MVP usa un usuario dev hardcodeado.

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

- Es la pantalla principal del producto en `/`.
- Renderiza el chat integrado con backend REST + WebSocket.
- Reemplazó al boilerplate default de create-next-app y a la ruta `/chat`.

### `app/globals.css`

- Importa Tailwind con `@import "tailwindcss"`.
- Define variables `--background` y `--foreground`.
- Declara tokens Tailwind inline para colores y fuentes.
- Tiene soporte basico de dark mode via `prefers-color-scheme`.
- El `body` todavia fuerza `font-family: Arial, Helvetica, sans-serif`, lo que compite con las variables Geist configuradas.

### `app/chat/page.tsx`

- Es un Client Component (`"use client"`).
- Mantiene estado local de mensajes, sesion activa, estado WS y plan ocupado.
- Al montar lista sesiones reales (`GET /api/v1/chat/sessions`) y crea una si no existe.
- Hidrata historial desde `GET /api/v1/chat/sessions/{id}/messages`.
- Si encuentra mensajes `plan_proposal`, consulta `GET /api/v1/plans/{id}` para renderizar el plan.
- Abre WebSocket a `/api/v1/ws?session_id=<id>` antes de mandar mensajes.
- `handleSend` agrega mensaje optimista y llama `POST /api/v1/chat/sessions/{id}/messages`.
- Procesa frames `chat_token`, `chat_message`, `plan_proposed`, `plan_update`, `turn_complete`, `error`, `ping/pong`.
- Aprueba/rechaza planes con `POST /api/v1/plans/{id}/approve` y `/reject`.
- Renderiza header con backend configurado y estado de conexion.

### `app/lib/backend/client.ts`

- Cliente REST tipado contra el backend FastAPI MVP real.
- Usa `NEXT_PUBLIC_API_BASE_URL` o default `http://localhost:8000`.
- Manda `Accept-Language: es-AR`.
- Parsea el envelope de errores del backend y levanta `BackendApiError`.
- Expone helpers para health, chat sessions/messages, plans, Wallbit connections, balances y transactions.

### `app/lib/backend/ws.ts`

- Cliente WebSocket simple para el protocolo MVP real.
- Usa `NEXT_PUBLIC_WS_BASE_URL` o deriva `ws://`/`wss://` desde el API base.
- Se conecta a `/api/v1/ws?session_id=<uuid>`.
- Entrega frames parseados a la UI y emite error local si llega JSON invalido.

### `app/chat/types.ts`

- Define el modelo UI `Message` con roles `user`, `assistant` y `system`.
- Puede incluir `planId` y `plan` para renderizar propuestas reales del backend.
- El contrato DTO/backend vive en `app/lib/backend/types.ts`.

### Componentes De Chat

- `ChatInput.tsx`: input controlado, trim de mensaje, boton disabled cuando `disabled` es true.
- `ChatThread.tsx`: lista mensajes, autoscroll con `useEffect` y render de typing indicator.
- `ChatMessage.tsx`: burbujas diferenciadas para usuario/asistente/sistema y render especial si el mensaje trae `plan`.
- `PlanConfirmation.tsx`: tarjeta de aprobacion/rechazo para `TradePlan` real.
- `PlanSummary.tsx`: resumen de plan y steps con estados.

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
- `/chat` ya no tiene `page.tsx`; la experiencia principal vive en `/`.
- Metadata y `lang` siguen genericos.

## Recomendaciones Para Siguientes Cambios

1. Cambiar metadata y `lang` a la identidad real del proyecto y `es-AR`.
2. Seguir puliendo copy Spanish-first.
3. Evaluar si `/chat` debe mantenerse como redirect a `/` o permanecer inexistente.
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
