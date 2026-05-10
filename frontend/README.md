# Atajo Frontend

Este es el frontend de **Atajo**, un agente financiero conversacional construido para Platanus Hack 26 (Buenos Aires).

## Stack

- Framework: [Next.js 15](https://nextjs.org) (App Router).
- Runtime UI: React 19.
- Lenguaje: TypeScript.
- Estilos: Tailwind CSS v4.

## Desarrollo Local

Primero, instala las dependencias usando [Bun](https://bun.sh/):

```bash
bun install
```

Luego inicia el servidor de desarrollo:

```bash
bun dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador para ver la aplicación.

### Variables de Entorno

El frontend requiere que el backend (FastAPI) esté corriendo. Configura estas variables (por defecto apuntan a localhost si no las defines, pero es buena práctica tenerlas):

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

## Arquitectura y Contexto

Por favor lee el archivo `FRONTEND_CONTEXT.md` en este mismo directorio. Contiene todas las reglas arquitectónicas, los contratos de la API (REST y WebSockets) que usa el frontend y el estado de la implementación actual.

Para instrucciones sobre cómo los LLM deben trabajar con esta versión de Next.js, revisa `AGENTS.md`.