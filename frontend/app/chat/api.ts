import type {
    Message,
    SendMessageRequest,
    SendMessageResponse,
} from "./types";

const CANNED_REPLIES = [
    "Got it!",
    "Interesting — tell me more.",
    "Hmm, let me think about that.",
    "Thanks for sharing.",
    "Could you elaborate?",
    "Makes sense to me.",
    "Noted. What else?",
];

function makeId() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function pickReply() {
    return CANNED_REPLIES[Math.floor(Math.random() * CANNED_REPLIES.length)];
}

// Mocked. Swap the body for a real fetch when the backend is ready:
//
//   const res = await fetch("/api/chat", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(request),
//   });
//   if (!res.ok) throw new Error(`Chat API failed: ${res.status}`);
//   return (await res.json()) as SendMessageResponse;
export async function sendChatMessage(
    request: SendMessageRequest,
): Promise<SendMessageResponse> {
    await new Promise((resolve) => setTimeout(resolve, 800));

    const last = request.messages[request.messages.length - 1];
    const text = last?.content.toLowerCase() ?? "";

    if (text.includes("swap") || text.includes("trade")) {
        const reply: Message = {
            id: makeId(),
            role: "bot",
            content: "Here's the trade I prepared. Please confirm:",
            createdAt: Date.now(),
            trade: {
                data: {
                    id: makeId(),
                    fromTicker: "USDC",
                    fromAmount: 100,
                    toTicker: "ETH",
                    toAmount: 0.025,
                    valueUSD: 100,
                },
                status: "pending",
            },
        };
        return { reply };
    }

    const reply: Message = {
        id: makeId(),
        role: "bot",
        content: pickReply(),
        createdAt: Date.now(),
    };
    return { reply };
}
