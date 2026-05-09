# Research brief: Claude agent workflows — streaming and tool confirmations

## Overview

Claude exposes "thinking" and tool execution as a structured SSE stream from the Anthropic Messages API. UIs render the spinner, the live thinking text, and the tool-call boxes by consuming a small set of typed events (`message_start`, `content_block_start/delta/stop`, `message_delta`, `message_stop`) plus three delta sub-types: `text_delta`, `thinking_delta`/`signature_delta`, and `input_json_delta`. Tool execution is gated by a layered permission system that combines (in this order) hooks → deny rules → permission mode → allow rules → a `canUseTool` callback. In Claude Code, that callback surfaces as the interactive "Allow / Allow always / Deny" prompt and the persisted choices are written to `.claude/settings.local.json` (or higher scopes). The Agent SDK exposes the same machinery programmatically via `canUseTool`, `permissionMode`, settings sources, and `PreToolUse` hooks.

---

## Section 1: Streaming the thought process

### 1.1 SSE event types from the Messages API

Set `"stream": true` on a `POST /v1/messages` request and the API returns server-sent events. The high-level flow is fixed:

1. `message_start` — emits a `Message` object with empty `content`, model, role, id, and initial `usage`.
2. For each output content block: `content_block_start` (with `index` and a partial `content_block`), then 1+ `content_block_delta` events, then `content_block_stop`.
3. `message_delta` — top-level changes (final `stop_reason`, `stop_sequence`, cumulative `usage`).
4. `message_stop`.
5. `ping` events may appear anywhere; `error` events (e.g., `overloaded_error`) can interrupt at any point.

The streaming docs describe new event types may be added per the API versioning policy; clients must handle unknown types gracefully.

### 1.2 Delta sub-types inside `content_block_delta`

| `delta.type`       | Meaning                                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| `text_delta`       | `delta.text` — append to text block at given `index`.                                                      |
| `thinking_delta`   | `delta.thinking` — chunk of extended-thinking content; only emitted when `display: "summarized"`.          |
| `signature_delta`  | `delta.signature` — encrypted signature of the full thinking, emitted just before the thinking block stops; required for multi-turn continuity. |
| `input_json_delta` | `delta.partial_json` — a partial JSON string for a `tool_use` block's `input` field.                       |

`message_delta.usage` token counts are **cumulative**, not deltas.

### 1.3 Extended thinking in the stream

A thinking block streams as:

```
event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"thinking","thinking":"","signature":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"thinking_delta","thinking":"I need to find the GCD..."}}

... more thinking_delta ...

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"signature_delta","signature":"EqQB..."}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}
```

Key client rules:

- `thinking={"type":"enabled"|"adaptive","budget_tokens":N,"display":"summarized"|"omitted"}` controls behavior.
- With `display:"omitted"` (default for Opus 4.7), no `thinking_delta` events arrive — the block opens, gets a single `signature_delta`, and closes. Text starts streaming sooner.
- Thinking blocks (and `redacted_thinking` blocks, when content is filtered) **must be passed back unchanged** in subsequent turns when paired with tool use, including the `signature`. The server decrypts the signature to reconstruct the original thinking; any text the client puts in the `thinking` field of an omitted block is ignored.
- Client UIs typically render `thinking_delta` text in a dimmed, collapsible "thinking…" panel and animate a spinner. Once `content_block_stop` fires for the thinking block, the spinner switches to "responding" / "using tool".

### 1.4 Tool-use streaming and the "Claude is using X" affordance

The trick that lets a UI show "Claude is using `Bash`…" before arguments are complete is in `content_block_start`:

```
event: content_block_start
data: {"type":"content_block_start","index":1,
       "content_block":{"type":"tool_use","id":"toolu_01...","name":"get_weather","input":{}}}
```

The `name` and `id` are present immediately on the `start` event, with `input: {}`. Subsequent events stream the JSON arguments piece by piece:

```
event: content_block_delta
data: {"type":"content_block_delta","index":1,
       "delta":{"type":"input_json_delta","partial_json":"{\"location\":"}}

event: content_block_delta
data: {"type":"content_block_delta","index":1,
       "delta":{"type":"input_json_delta","partial_json":" \"San Fra"}}
```

Implementation notes from the docs:

- `partial_json` deltas are **string fragments**, not JSON objects. Concatenate them and parse on `content_block_stop`, or use partial-JSON parsing (Pydantic helper, SDK `inputJsonStream`, etc.) to render arguments live.
- Current models emit one complete key/value pair at a time, so there can be visible delays between deltas while the model reasons. Use an "indeterminate" spinner or progress dot, not a per-character animation.
- Server tools (`web_search`, `code_execution`, `web_fetch`) appear with `content_block.type` = `server_tool_use` and the same `input_json_delta` pattern; their results stream back as a separate content block (e.g., `web_search_tool_result`) before Claude continues.
- `stop_reason: "tool_use"` arrives in the `message_delta` event, which is the signal for client-tool callers to suspend the loop and execute the tool.
- `eager_input_streaming: true` per-tool enables fine-grained streaming for parameter values.

### 1.5 Anthropic SDK streaming helpers

The SDKs accumulate events into a final `Message` so callers don't reimplement state machines.

```python
import anthropic
client = anthropic.Anthropic()
with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=20000,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[{"role": "user", "content": "..."}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
    final = stream.get_final_message()
```

TypeScript exposes `.on("text", …)`, `for await` event iteration, and `stream.finalMessage()`. Go has `message.Accumulate(event)`, Java `MessageAccumulator`, Ruby `.accumulated_message`. Use these whenever you can — the docs explicitly recommend SDKs over hand-rolled SSE parsing.

### 1.6 Agent SDK message stream

The Claude Agent SDK wraps the API and emits higher-level `SDKMessage` objects: `system` init, `assistant` (model output), `user` (tool_result), and a terminal `result` message with `subtype: "success" | "error"`. In TypeScript:

```typescript
for await (const message of query({ prompt, options })) {
  if (message.type === "assistant") { /* show streamed assistant output */ }
  if (message.type === "result")    { /* final summary */ }
}
```

Hooks (`PreToolUse`, `PostToolUse`, `Notification`, `SubagentStop`, …) are how SDK callers observe and intercept tool activity in flight — they are the equivalent of the API-level `tool_use` block events plus a decision return.

### 1.7 What Claude Code (CLI/IDE) renders in practice

- A status bar shows the current permission mode (e.g., `⏵⏵ accept edits on`, `plan mode`).
- A spinner with elapsed time runs while the SDK is iterating events.
- Thinking text is rendered inline in a dimmed style (Sonnet/Opus default `display:"summarized"` produces this); when `display:"omitted"` is in force, you only see a "Thinking…" pulse.
- Each `tool_use` block becomes a labeled box: tool name (`Bash`, `Edit`, `Write`, `WebFetch`, `mcp__<server>__<action>`), the partially-streamed input rendered as it arrives (file path appears before `content`, command appears before `description`), and the result block below once the tool returns.
- For server tools like `web_search`, the search results render as a citation list returned in a `web_search_tool_result` content block.
- The `Notification` hook event (`permission_prompt`, `idle_prompt`) is what drives system-tray pings and Slack/PagerDuty integrations.

---

## Section 2: Asking for confirmation before tool runs

The four mechanisms below are layered; understanding the **evaluation order** is the most important thing.

### 2.0 Evaluation order (single source of truth)

When the SDK or CLI receives a `tool_use` block from the model, it resolves whether the tool actually runs in this fixed sequence (first match wins for terminal decisions):

1. **Hooks** (`PreToolUse`). They can deny outright (terminal). An `allow` from a hook does **not** skip the deny/ask checks below — those still apply.
2. **Deny rules** (from `disallowedTools` / `permissions.deny` in settings). Block. Effective even in `bypassPermissions`.
3. **Permission mode**. `bypassPermissions` approves, `acceptEdits` approves filesystem edits, `dontAsk` denies anything not already pre-approved, `plan` allows only read-only tools, `auto` defers to a classifier model.
4. **Allow rules** (from `allowedTools` / `permissions.allow`). Approve.
5. **`canUseTool` callback** (or interactive `/permissions` prompt). Final fallback. In `dontAsk` mode this step is skipped and the call is denied.

Multiple hooks of the same type run in parallel; the strictest result wins (`deny` > `defer` > `ask` > `allow`).

### 2.1 Mechanism A — Permission modes

| Mode                | Behavior                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `default`           | Reads run; everything else prompts on first use of each tool.                                                                   |
| `acceptEdits`       | Reads + file edits + a fixed list of filesystem Bash commands (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) auto-approved on in-scope paths. Other Bash still prompts. |
| `plan`              | Reads only; Claude proposes a plan instead of editing source.                                                                   |
| `auto`              | A classifier model approves/denies each call; pauses to default mode after 3 consecutive or 20 total denials. Research preview. |
| `dontAsk`           | Auto-deny anything not pre-approved by allow rules; `canUseTool` is never called. Use for non-interactive CI.                   |
| `bypassPermissions` | All checks skipped except deny rules and root-/home-level `rm -rf` circuit breakers. Hooks still run.                           |

How you set it:

- CLI: `claude --permission-mode plan`, or `Shift+Tab` to cycle `default → acceptEdits → plan`.
- Settings: `{"permissions":{"defaultMode":"acceptEdits"}}` in `.claude/settings.json`.
- SDK at start: `query({ options: { permissionMode: "default" } })`.
- SDK mid-session: `q.setPermissionMode("acceptEdits")` (TS) or `await client.set_permission_mode("acceptEdits")` (Python).

Important caveat from the docs: when a parent agent uses `bypassPermissions`, `acceptEdits`, or `auto`, **all subagents inherit it and cannot override per-agent**. Plan accordingly.

### 2.2 Mechanism B — `canUseTool` callback (Agent SDK)

Signature is identical in shape across Python and TypeScript: it receives the tool name, the tool input, and a context object; returns an allow- or deny-shaped object.

TypeScript:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

await query({
  prompt: "...",
  options: {
    canUseTool: async (toolName, input, { signal, suggestions }) => {
      if (toolName === "Bash" && /rm -rf/.test(input.command)) {
        return { behavior: "deny", message: "rm -rf is blocked", interrupt: true };
      }
      if (toolName === "Write") {
        return { behavior: "allow", updatedInput: { ...input, file_path: `/sandbox${input.file_path}` } };
      }
      return { behavior: "allow", updatedInput: input };
    },
  },
});
```

Python (`PermissionResultAllow` / `PermissionResultDeny`):

```python
async def can_use_tool(tool_name, input_data, context):
    if tool_name == "Bash" and "rm -rf" in input_data.get("command", ""):
        return PermissionResultDeny(message="rm -rf is blocked")
    return PermissionResultAllow(updated_input=input_data)

options = ClaudeAgentOptions(can_use_tool=can_use_tool)
```

Return shapes:

| Decision | TypeScript | Python |
| -------- | ---------- | ------ |
| Allow as-is | `{ behavior: "allow", updatedInput: input }` | `PermissionResultAllow(updated_input=input_data)` |
| Allow with rewrite | `{ behavior: "allow", updatedInput: { ...input, /* changes */ } }` | `PermissionResultAllow(updated_input={...})` |
| Deny + feedback | `{ behavior: "deny", message: "User declined" }` | `PermissionResultDeny(message="User declined")` |
| Deny + abort turn | `{ behavior: "deny", message: "...", interrupt: true }` (TS) | n/a |

The `message` you return on deny is fed back to the model as the tool result, so use it to redirect Claude (e.g., "User doesn't want to delete files. They asked if you could compress them into an archive instead."). The callback can stay pending indefinitely; the SDK only times out when the surrounding query is cancelled. Python `canUseTool` requires streaming mode and a dummy `PreToolUse` hook returning `{"continue_": True}` to keep the stream open — this is a documented workaround.

The same callback is reused for Claude's `AskUserQuestion` clarifying-question flow: when `toolName === "AskUserQuestion"`, the input contains a `questions` array (each with `header`, `question`, `options[]`, `multiSelect`); your handler returns `{ behavior: "allow", updatedInput: { questions, answers: { [q.question]: option.label } } }`.

### 2.3 Mechanism C — `PreToolUse` hooks

Hooks run **before** the permission-rule checks. Exit code 2 (shell hooks) or `permissionDecision: "deny"` (SDK hooks) terminates the call before any allow rule could let it through. The JSON output schema:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow" | "deny" | "ask" | "defer",
    "permissionDecisionReason": "...",
    "updatedInput": { /* rewritten tool input; must pair with permissionDecision: 'allow' */ },
    "additionalContext": "appended to model context"
  },
  "systemMessage": "shown in conversation",
  "continue": true
}
```

- `allow` skips the user prompt.
- `deny` blocks. The reason is shown to the user and fed back to the model.
- `ask` forces the prompt even if an allow rule would normally pre-approve.
- `defer` (TypeScript SDK / CLI `-p` only) ends the query and persists state for resumption — used when an out-of-band approval system (Slack, ticketing) will respond later.

SDK hook example (TypeScript):

```typescript
import { HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

const protectEnv: HookCallback = async (input) => {
  const i = input as PreToolUseHookInput;
  const path = (i.tool_input as any)?.file_path ?? "";
  if (path.endsWith(".env")) {
    return {
      hookSpecificOutput: {
        hookEventName: i.hook_event_name,
        permissionDecision: "deny",
        permissionDecisionReason: "Cannot modify .env files",
      },
    };
  }
  return {};
};

await query({ prompt, options: { hooks: { PreToolUse: [{ matcher: "Write|Edit", hooks: [protectEnv] }] } } });
```

Shell hook (settings.json):

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-rm.sh", "timeout": 30 }] }
    ]
  }
}
```

The shell hook receives JSON over stdin (`session_id`, `tool_name`, `tool_input`, `tool_use_id`, `permission_mode`, …) and writes the decision JSON to stdout. Exit 0 + JSON for structured control; exit 2 to block; other non-zero is treated as a non-blocking error.

There are 11 SDK hook events; the most useful for permission flows are `PreToolUse`, `PostToolUse`, `PermissionRequest` (fires when the SDK is about to surface a `canUseTool` prompt — useful for routing to Slack/email), and `Notification` (`permission_prompt` / `idle_prompt`).

### 2.4 Mechanism D — Settings-level allow/ask/deny lists

Located in (low → high precedence): `~/.claude/settings.json`, `.claude/settings.json` (checked in), `.claude/settings.local.json` (gitignored), managed settings (org policy, cannot be overridden).

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Read(./src/**)",
      "Edit(./src/**)",
      "WebFetch(domain:github.com)",
      "mcp__puppeteer__*"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env*)",
      "Read(./secrets/**)",
      "WebFetch"
    ],
    "ask": [
      "Bash(git push *)"
    ],
    "defaultMode": "acceptEdits",
    "additionalDirectories": ["../docs/"],
    "disableBypassPermissionsMode": "disable"
  }
}
```

Pattern syntax highlights:

- `Tool` matches any use; `Tool(specifier)` is exact or prefix-with-`*`.
- Bash uses `*` (single wildcard, can span spaces/args). `Bash(ls *)` enforces a word boundary; `Bash(ls*)` doesn't. `Bash(cmd:*)` is equivalent to `Bash(cmd *)`. Rules **must match each subcommand** of a compound (`&&`, `||`, `;`, `|`, `&`, newline). A built-in wrapper list (`timeout`, `nice`, `nohup`, `stdbuf`, bare `xargs`) is stripped before matching; runners like `npx`, `docker exec`, `devbox run` are not. A built-in read-only set (`ls`, `cat`, `grep`, `head`, `tail`, `find`, `wc`, `diff`, …) never prompts.
- `Read`/`Edit` follow gitignore semantics: `//abs`, `~/home`, `/repo-root`, `path` or `./path` (relative to cwd). `Read(.env)` ≡ `Read(**/.env)`. Edit/Read deny rules apply to Claude's **tools**, not Bash subprocesses; combine with sandboxing for OS-level enforcement.
- WebFetch supports `WebFetch(domain:example.com)`.
- MCP: `mcp__<server>` for any tool, `mcp__<server>__<action>` for one tool, `mcp__<server>__*` wildcard.
- `Agent(<name>)` controls subagent invocations.

Programmatic equivalents: `allowedTools` / `disallowedTools` arrays in `query()` options. `bypassPermissions` does **not** honor `allowedTools` (it approves everything except deny rules); use `disallowedTools` if you need a deny list with bypass.

To make project settings actually load in the SDK, set `settingSources: ["project"]` (TS) or `setting_sources=["project"]` (Python) — by default `query()` loads project settings, but a custom `settingSources` overrides that, so include `"project"` explicitly when you set it.

### 2.5 The user-facing UX in Claude Code

When a tool needs approval and no rule matched, the CLI prints a permission card showing the tool name, the input (a colorized diff for `Edit`/`Write`, the command for `Bash`, etc.), and three options. The exact wording is "Yes (don't ask again)" for the persistent variant; the docs describe the tiered behavior:

| Tool category | Approval required | What "Yes, don't ask again" persists |
| ------------- | ----------------- | ------------------------------------ |
| Read-only (Read, Grep) | None | n/a |
| Bash | Yes | Persisted **per project directory and command prefix** in `.claude/settings.local.json` |
| File modification (Edit, Write) | Yes | Persisted **until session end** (not written to disk) |

Selecting "Yes, don't ask again" appends to the `permissions.allow` array in the highest-precedence non-managed settings file. For compound Bash commands, up to 5 separate prefix rules are saved (one per subcommand). When the user selects "No", the denial reason is fed back to the model as the tool result, so Claude can adjust. View and edit live rules via `/permissions`.

`/sandbox` enables OS-level filesystem/network isolation for Bash; with `autoAllowBashIfSandboxed: true` (default), sandboxed Bash skips even the "ask" rules (the sandbox boundary substitutes for the prompt), but explicit deny rules and the `rm -rf /` circuit breaker still apply.

---

## Practical guidance: wiring an agent loop with streaming + human approval

For someone building or extending an agent, the recommended composition:

1. **Use the SDK, not raw SSE.** Anthropic explicitly recommends the SDKs over hand-parsing the stream. For pure Messages API use, lean on `messages.stream(...)` accumulators (Python `get_final_message`, TS `finalMessage`, Go `Accumulate`, Java `MessageAccumulator`). For agent loops, use the Agent SDK's `query()` / `ClaudeSDKClient`.

2. **Stream rendering checklist.** On each event:
   - `message_start` → render an empty assistant turn, start a spinner.
   - `content_block_start` with `type: "thinking"` → open a "Thinking…" panel; with `type: "tool_use"` → open a tool card showing `name` and `id` immediately.
   - `content_block_delta`:
     - `text_delta` → append to the visible response.
     - `thinking_delta` → append to the thinking panel.
     - `input_json_delta` → buffer `partial_json`; render keys live with a partial-JSON parser.
     - `signature_delta` → store, do not render; the value is opaque.
   - `content_block_stop` → finalize the block; for tool_use, parse the buffered JSON and run permission checks before executing.
   - `message_delta` with `stop_reason: "tool_use"` → suspend the loop, let the permission flow run, then send the `tool_result` back.
   - `message_stop` → stop the spinner.
   - Always handle unknown event types as no-ops.

3. **Permission architecture.** Layer in this order, top to bottom:
   - **Static deny rules** in `.claude/settings.json` for things you never want (e.g., `Bash(curl *)`, `Read(./.env)`, `WebFetch`). These hold even in `bypassPermissions`.
   - **Static allow rules** for things you always trust (`Read(./src/**)`, `Bash(npm test)`).
   - **`PreToolUse` hooks** for dynamic policy: rewriting paths into a sandbox, blocking commands that match a runtime regex, paging Slack via `PermissionRequest`, redacting secrets from `tool_input`.
   - **`canUseTool` callback** as the user-facing fallback. Render a UI prompt (terminal y/n, web modal, mobile sheet), and on "always allow" persist the rule into `permissions.allow` so the next call short-circuits at step 4 of the evaluation order.
   - **Permission mode** as the global posture: `plan` for exploratory work, `default` for human-in-the-loop, `acceptEdits` for trusted prototyping, `dontAsk` for headless CI.

4. **Always feed deny back to the model.** Use the `message` field on `PermissionResultDeny` (or `permissionDecisionReason` in a hook) to give Claude the *reason* and a hint at what to do instead. The docs' canonical example: "User doesn't want to delete files. They asked if you could compress them into an archive instead." This makes denial productive instead of dead-ending the turn.

5. **Use `PermissionRequest` (and `Notification`) hooks for out-of-band approval.** When the human isn't in front of the terminal, route the prompt to Slack/PagerDuty/email and either wait (the callback can stay pending indefinitely) or use TypeScript's `defer` decision to release the process and resume from the persisted session later.

6. **Preserve thinking blocks across tool turns.** When you assemble the next request after a tool result, include the assistant turn's thinking blocks as-is (with their `signature`). On Opus 4.5+/Sonnet 4.6+ they are preserved by default; on earlier models they are stripped during cache calculations. Switching `display` between `summarized` and `omitted` across turns is allowed; the signature is identical.

7. **Don't reach for `bypassPermissions`.** The docs are explicit that it skips writes to `.git`, `.claude`, `.vscode`, and other protected paths and only stops `rm -rf /` / `rm -rf ~`. Use `auto` mode (when eligible) or `acceptEdits` + tight allow lists instead. Subagents inherit `bypassPermissions` and cannot override it.

8. **Test patterns are fragile for security boundaries.** Per the docs, `Bash(curl http://github.com/ *)` will not constrain `curl -X GET http://github.com/...`, `https://...`, redirected URLs, or shell-variable expansions. For URL filtering, deny `curl`/`wget` at the Bash layer and use `WebFetch(domain:...)` allow rules; for filesystem isolation, combine settings deny rules with the OS-level sandbox.

---

## Sources

- [Streaming messages — Anthropic Messages API](https://platform.claude.com/docs/en/api/messages-streaming)
- [Extended thinking](https://platform.claude.com/docs/en/docs/build-with-claude/extended-thinking)
- [Tool use with Claude — overview](https://platform.claude.com/docs/en/docs/build-with-claude/tool-use/overview)
- [Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)
- [Agent SDK — Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)
- [Agent SDK — Handle approvals and user input (canUseTool)](https://code.claude.com/docs/en/agent-sdk/user-input)
- [Agent SDK — Intercept and control agent behavior with hooks](https://code.claude.com/docs/en/agent-sdk/hooks)
- [Claude Code — Configure permissions (settings.json schema)](https://code.claude.com/docs/en/permissions)
- [Claude Code — Choose a permission mode](https://code.claude.com/docs/en/permission-modes)
- [Claude Code — Settings files](https://code.claude.com/docs/en/settings)
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Claude Code — Security](https://code.claude.com/docs/en/security)
