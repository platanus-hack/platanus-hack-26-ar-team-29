import { getWsBaseUrl } from "./client";
import type { BackendWsFrame } from "./types";

export interface BackendWsSubscription {
  close: () => void;
  sendPing: () => void;
}

export function openSessionWebSocket({
  sessionId,
  onFrame,
  onOpen,
  onClose,
  onError,
}: {
  sessionId: string;
  onFrame: (frame: BackendWsFrame) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
}): BackendWsSubscription {
  const url = `${getWsBaseUrl()}/api/v1/ws?session_id=${encodeURIComponent(sessionId)}`;
  const ws = new WebSocket(url);

  ws.addEventListener("open", () => {
    onOpen?.();
  });

  ws.addEventListener("message", (event) => {
    try {
      onFrame(JSON.parse(event.data) as BackendWsFrame);
    } catch {
      onFrame({
        type: "error",
        code: "INVALID_WS_FRAME",
        message_es: "El servidor envió un evento inválido.",
      });
    }
  });

  ws.addEventListener("error", (event) => {
    onError?.(event);
  });

  ws.addEventListener("close", () => {
    onClose?.();
  });

  return {
    close() {
      ws.close();
    },
    sendPing() {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "ping" }));
    },
  };
}
