import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

export default {
  id: "nemoclaw-guard",
  name: "Nemoclaw Guard",
  description: "Generic inbound approval interception for guarded actions",
  register(api) {
    const workspaceDir =
      process.env.OPENCLAW_WORKSPACE_DIR || "/home/node/.openclaw/workspace";

    const nemoclawGuardRoot =
      process.env.NEMOCLAW_GUARD_ROOT || "/opt/nemoclaw-guard";
    const runtimeStateDir = path.join(nemoclawGuardRoot, "runtime", "state");
    const approvalExecuteFileDeletePath = path.join(
      runtimeStateDir,
      "approval_execute_file_delete.py"
    );
    const approvalPrepareFileDeletePath = path.join(
      runtimeStateDir,
      "approval_prepare_file_delete.py"
    );
    const approvalApplyRuntimeOutcomePath = path.join(
      runtimeStateDir,
      "approval_apply_runtime_outcome.py"
    );
    const approvalCheckDuplicateExecPath = path.join(
      runtimeStateDir,
      "approval_check_duplicate_exec.py"
    );

    const approvalEnginePath = path.join(
      runtimeStateDir,
      "approval_engine.py"
    );

    const stateDir = path.join(workspaceDir, ".openclaw", "nemoclaw-guard");
    const stateFile = path.join(stateDir, "state.json");

    const MAX_INBOUND_EVENTS = 80;
    const FALLBACK_WINDOW_MS = 2 * 60 * 1000;

    function ensureStateDir() {
      fs.mkdirSync(stateDir, { recursive: true });
    }

    function defaultState() {
      return {
        version: 5,
        inboundEvents: [],
        recentInboundByConversation: {},
        activeSessionByConversation: {},
        routeBindingByConversation: {},
        linkedInboundBySession: {},
        activeRunBySession: {},
        pendingApprovals: {},
        guardActionsBySession: {},
        activeConversationBySession: {},
        runtimeApprovalBySession: {},
        completedRuntimeActionBySession: {}
      };
    }

    function readState() {
      try {
        ensureStateDir();
        if (!fs.existsSync(stateFile)) return defaultState();
        const parsed = JSON.parse(fs.readFileSync(stateFile, "utf8"));
        return {
          ...defaultState(),
          ...parsed,
          inboundEvents: Array.isArray(parsed?.inboundEvents) ? parsed.inboundEvents : [],
          recentInboundByConversation:
            parsed?.recentInboundByConversation && typeof parsed.recentInboundByConversation === "object"
              ? parsed.recentInboundByConversation
              : {},
          activeSessionByConversation:
            parsed?.activeSessionByConversation && typeof parsed.activeSessionByConversation === "object"
              ? parsed.activeSessionByConversation
              : {},
          routeBindingByConversation:
            parsed?.routeBindingByConversation && typeof parsed.routeBindingByConversation === "object"
              ? parsed.routeBindingByConversation
              : {},
          linkedInboundBySession:
            parsed?.linkedInboundBySession && typeof parsed.linkedInboundBySession === "object"
              ? parsed.linkedInboundBySession
              : {},
          activeRunBySession:
            parsed?.activeRunBySession && typeof parsed.activeRunBySession === "object"
              ? parsed.activeRunBySession
              : {},
          pendingApprovals:
            parsed?.pendingApprovals && typeof parsed.pendingApprovals === "object"
              ? parsed.pendingApprovals
              : {},
          guardActionsBySession:
            parsed?.guardActionsBySession && typeof parsed.guardActionsBySession === "object"
              ? parsed.guardActionsBySession
              : {},
          activeConversationBySession:
            parsed?.activeConversationBySession && typeof parsed.activeConversationBySession === "object"
              ? parsed.activeConversationBySession
              : {},
          runtimeApprovalBySession:
            parsed?.runtimeApprovalBySession && typeof parsed.runtimeApprovalBySession === "object"
              ? parsed.runtimeApprovalBySession
              : {},
          completedRuntimeActionBySession:
            parsed?.completedRuntimeActionBySession && typeof parsed.completedRuntimeActionBySession === "object"
              ? parsed.completedRuntimeActionBySession
              : {}
        };
      } catch (err) {
        api.logger.warn?.(`[nemoclaw-guard] failed to read state: ${String(err)}`);
        return defaultState();
      }
    }

    function writeState(state) {
      try {
        ensureStateDir();
        const tmp = `${stateFile}.tmp`;
        fs.writeFileSync(tmp, JSON.stringify(state, null, 2));
        fs.renameSync(tmp, stateFile);
      } catch (err) {
        api.logger.warn?.(`[nemoclaw-guard] failed to save state: ${String(err)}`);
      }
    }

    function nowIso() {
      return new Date().toISOString();
    }

    function generateApprovalId() {
      return "approval_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2,6);
    }

      function shouldRequireApproval(event, ctx) {
        const toolName = ctx?.toolName ?? event?.toolName ?? null;
        const params = event?.params ?? {};

        if (toolName !== "message") return false;

        const action = params?.action ?? null;

        if (action !== "send") return false;

        const state = readState();
        const sessionKey = ctx?.sessionKey ?? null;

        if (!sessionKey) return false;

        const guardAction = state.guardActionsBySession?.[sessionKey] ?? null;

        if (!guardAction) return false;

        return true;
      }



    function registerPendingApproval(state, data) {
      state.pendingApprovals = state.pendingApprovals || {};
      const id = generateApprovalId();

      state.pendingApprovals[id] = {
        id,
        toolName: data.toolName ?? null,
        toolCallId: data.toolCallId ?? null,
        runId: data.runId ?? null,
        sessionKey: data.sessionKey ?? null,
        conversationKey: data.conversationKey ?? null,
        paramsPreview: data.paramsPreview ?? null,
          runtimeRequestSessionId: data.runtimeRequestSessionId ?? null,
        createdAt: nowIso(),
        status: "pending"
      };

      return id;
    }

    function setGuardActionForSession(state, sessionKey, data) {
      if (!sessionKey) return;
      state.guardActionsBySession = state.guardActionsBySession || {};
      state.guardActionsBySession[sessionKey] = {
        type: data?.type ?? null,
        reason: data?.reason ?? null,
        target: data?.target ?? null,
        createdAt: nowIso()
      };
    }

    function clearGuardActionForSession(state, sessionKey) {
      if (!sessionKey || !state.guardActionsBySession) return;
      delete state.guardActionsBySession[sessionKey];
    }

    function setRuntimeApprovalForSession(state, sessionKey, data) {
      if (!sessionKey) return;
      state.runtimeApprovalBySession = state.runtimeApprovalBySession || {};
      state.runtimeApprovalBySession[sessionKey] = {
        requestSessionId: data?.requestSessionId ?? null,
        family: data?.family ?? null,
        target: data?.target ?? null,
        createdAt: nowIso()
      };
    }

    function clearRuntimeApprovalForSession(state, sessionKey) {
      if (!sessionKey || !state.runtimeApprovalBySession) return;
      delete state.runtimeApprovalBySession[sessionKey];
    }

    function getRuntimeApprovalForSession(state, sessionKey) {
      if (!sessionKey) return null;
      return state.runtimeApprovalBySession?.[sessionKey] ?? null;
    }

    function setCompletedRuntimeActionForSession(state, sessionKey, data) {
      if (!sessionKey) return;
      state.completedRuntimeActionBySession = state.completedRuntimeActionBySession || {};
      state.completedRuntimeActionBySession[sessionKey] = {
        family: data?.family ?? null,
        target: data?.target ?? null,
        requestSessionId: data?.requestSessionId ?? null,
        completedAt: nowIso()
      };
    }

    function getCompletedRuntimeActionForSession(state, sessionKey) {
      if (!sessionKey) return null;
      return state.completedRuntimeActionBySession?.[sessionKey] ?? null;
    }

    function clearCompletedRuntimeActionForSession(state, sessionKey) {
      if (!sessionKey || !state.completedRuntimeActionBySession) return;
      delete state.completedRuntimeActionBySession[sessionKey];
    }

    function extractUserTextFromMessage(message) {
      if (!message || typeof message !== "object") return null;

      if (typeof message.content === "string") {
        return message.content.trim() || null;
      }

      if (Array.isArray(message.content)) {
        const textParts = [];
        for (const part of message.content) {
          if (typeof part === "string") {
            textParts.push(part);
            continue;
          }
          if (part && typeof part === "object" && typeof part.text === "string") {
            textParts.push(part.text);
          }
        }
        const joined = textParts.join(" ").trim();
        return joined || null;
      }

      return null;
    }

    function runRuntimePython(scriptPath, payload) {
      const result = spawnSync("python3", [scriptPath], {
        input: JSON.stringify(payload),
        encoding: "utf8"
      });

      if (result.error) {
        throw result.error;
      }

      if ((result.status ?? 0) !== 0) {
        throw new Error(
          `[nemoclaw-guard] runtime script failed: ${scriptPath} rc=${result.status ?? "null"} stderr=${result.stderr || ""}`
        );
      }

      const stdout = (result.stdout || "").trim();
      if (!stdout) return null;

      return JSON.parse(stdout);
    }

      function runApprovalExecuteFileDelete(payload) {
        return runApprovalEngine("execute_file_delete", payload);
      }

      function runApprovalPrepareFileDelete(payload) {
        return runApprovalEngine("prepare_file_delete", payload);
      }

      function runApprovalApplyRuntimeOutcome(payload) {
        return runApprovalEngine("apply_runtime_outcome", payload);
      }

      function runApprovalCheckDuplicateExec(payload) {
        return runApprovalEngine("check_duplicate_exec", payload);
      }

      function runApprovalEngine(action, payload) {
        return runRuntimePython(approvalEnginePath, {
          action,
          payload
        });
      }

      function processRuntimeApprovalReply(state, sessionKey, agentId, userText) {
        const runtimeApproval = getRuntimeApprovalForSession(state, sessionKey);
        if (!runtimeApproval?.requestSessionId || !userText) return;

        try {
          const runtimeResult = runApprovalExecuteFileDelete({
            request_session_id: runtimeApproval.requestSessionId,
            text: userText
          });

          log({
            type: "runtime_approval_reply_processed",
            at: nowIso(),
            sessionKey,
            agentId: agentId ?? null,
            requestSessionId: runtimeApproval.requestSessionId,
            userText,
            runtimeResult
          });

          const updatedSession = runtimeResult?.updated_session ?? null;
          const sessionStatus = updatedSession?.status ?? null;
          const executionStatus = updatedSession?.execution_status ?? null;

          const result = runApprovalApplyRuntimeOutcome({
            state,
            session_key: sessionKey,
            runtime_approval: runtimeApproval,
            session_status: sessionStatus,
            execution_status: executionStatus
          });

          if (result?.state) {
            Object.assign(state, result.state);
          }
        } catch (err) {
          log({
            type: "runtime_approval_reply_failed",
            at: nowIso(),
            sessionKey,
            agentId: agentId ?? null,
            requestSessionId: runtimeApproval?.requestSessionId ?? null,
            userText,
            error: String(err)
          });
        }
      }

      function tryCreateRuntimeApprovalSession(linkedChatId, command) {
        if (!linkedChatId || !command || !command.includes("guarded_file_delete.sh")) {
          return null;
        }

        const targetPath = extractGuardedFileDeleteTarget(command);
        if (!targetPath) return null;

        const prepared = runApprovalPrepareFileDelete({
          chat_id: linkedChatId,
          target_path: targetPath
        });

        return {
          runtimeSession: prepared?.session ?? null,
          family: prepared?.family ?? "file.delete",
          targetPath: prepared?.target_path ?? targetPath
        };
      }

      function linkRuntimeSessionToApproval(state, sessionKey, approvalId, runtimeSessionResult) {
        const runtimeSession = runtimeSessionResult?.runtimeSession ?? null;
        if (!runtimeSession?.request_session_id) return null;

        setRuntimeApprovalForSession(state, sessionKey, {
          requestSessionId: runtimeSession.request_session_id,
          family: runtimeSessionResult?.family ?? null,
          target: runtimeSessionResult?.targetPath ?? null
        });

        if (approvalId && state.pendingApprovals?.[approvalId]) {
          state.pendingApprovals[approvalId].runtimeRequestSessionId = runtimeSession.request_session_id;
        }

        return runtimeSession;
      }

      function handleDangerousExecFlow(state, ctx, event, linkedInbound, toolName, command) {
        setGuardActionForSession(state, ctx?.sessionKey ?? null, {
          type: "exec",
          reason: "dangerous_exec_command",
          target: command
        });

        const approvalId = registerPendingApproval(state, {
          toolName: toolName,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          runId: ctx?.runId ?? event?.runId ?? null,
          sessionKey: ctx?.sessionKey ?? null,
          conversationKey:
            state.activeConversationBySession?.[ctx?.sessionKey]?.conversationKey ?? null,
          paramsPreview: {
            command
          }
        });

        let runtimeSession = null;
        try {
          const linkedChatId =
            state.activeConversationBySession?.[ctx?.sessionKey]?.conversationId ??
            linkedInbound?.conversationId ??
            null;

          const runtimeSessionResult = tryCreateRuntimeApprovalSession(
            linkedChatId,
            command
          );

          runtimeSession = linkRuntimeSessionToApproval(
            state,
            ctx?.sessionKey ?? null,
            approvalId,
            runtimeSessionResult
          );
        } catch (err) {
          log({
            type: "runtime_approval_session_create_failed",
            at: nowIso(),
            sessionKey: ctx?.sessionKey ?? null,
            agentId: ctx?.agentId ?? null,
            toolName,
            toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
            runId: ctx?.runId ?? event?.runId ?? null,
            command,
            error: String(err)
          });
        }

        writeState(state);

        log({
          type: "guard_action_marked",
          at: nowIso(),
          sessionKey: ctx?.sessionKey ?? null,
          agentId: ctx?.agentId ?? null,
          toolName,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          runId: ctx?.runId ?? event?.runId ?? null,
          command
        });

        log({
          type: "approval_pending",
          at: nowIso(),
          approvalId,
          toolName,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          runId: ctx?.runId ?? event?.runId ?? null,
          command,
          runtimeRequestSessionId: runtimeSession?.request_session_id ?? null
        });

        throw new Error("Nemoclaw Guard approval required: " + approvalId);
      }

      function handleDuplicateRuntimeExec(state, ctx, event, toolName, command) {
        const result = runApprovalCheckDuplicateExec({
          state,
          session_key: ctx?.sessionKey ?? null,
          command,
          tool_name: toolName
        });

        if (result?.is_duplicate) {
          log({
            type: "duplicate_exec_after_runtime_execution_skipped",
            at: nowIso(),
            sessionKey: ctx?.sessionKey ?? null,
            agentId: ctx?.agentId ?? null,
            toolName,
            toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
            runId: ctx?.runId ?? event?.runId ?? null,
            command,
            completedRuntimeAction: result?.completed_runtime_action ?? null
          });

          throw new Error("Nemoclaw Guard duplicate exec skipped after runtime execution");
        }
      }

      function normalizeApprovalReplyText(text) {
        if (!text || typeof text !== "string") return null;

        let cleaned = text.replace(/\r/g, "").trim();

        cleaned = cleaned.replace(/^\[Queued messages while agent was busy\]\s*/m, "").trim();

        cleaned = cleaned.replace(/Conversation info \(untrusted metadata\):\s*```json[\s\S]*?```/g, "").trim();
        cleaned = cleaned.replace(/Sender \(untrusted metadata\):\s*```json[\s\S]*?```/g, "").trim();

        const lines = cleaned
          .split("\n")
          .map((line) => line.trim())
          .filter(Boolean)
          .filter((line) => !/^Queued #\d+$/i.test(line))
          .filter((line) => line !== "---");

        cleaned = lines.join("\n").trim();

        if (!cleaned) return null;

        const tail = cleaned.split("\n").map((line) => line.trim()).filter(Boolean);
        if (!tail.length) return null;

        return tail[tail.length - 1] || null;
      }

    function extractExecCommand(params) {
      if (!params || typeof params !== "object") return null;
      if (typeof params.command === "string") return params.command;
      return null;
    }

    function extractGuardedFileDeleteTarget(command) {
      if (!command || typeof command !== "string") return null;

      const parts = command.trim().split(/\s+/);
      if (!parts.length) return null;

      const base = parts[0] || "";
      if (!/guarded_file_delete\.sh$/i.test(base)) return null;

      for (let i = 1; i < parts.length; i++) {
        const part = parts[i];
        if (!part || part.startsWith("--")) continue;
        return part;
      }

      return null;
    }

    function isDangerousExecCommand(command) {
      if (!command || typeof command !== "string") return false;

      const cmd = command.trim().toLowerCase();

      if (!cmd) return false;

        return (
          /\brm\b/.test(cmd) ||
          /\brmdir\b/.test(cmd) ||
          /\bunlink\b/.test(cmd) ||
          /\bmv\b/.test(cmd) ||
          /\bchmod\b/.test(cmd) ||
          /\bchown\b/.test(cmd) ||
          /\btruncate\b/.test(cmd) ||
          /\bshred\b/.test(cmd) ||
          /\bmkfs\b/.test(cmd) ||
          /\bdd\b/.test(cmd) ||
          /\bguarded_file_delete\.sh\b/.test(cmd) ||
          /\bguarded_file_[a-z0-9_-]+\.sh\b/.test(cmd)
        );
    }
    function buildConversationKey({ channelId, accountId, conversationId }) {
      return `${channelId || "unknown"}|${accountId || "default"}|${conversationId || "unknown"}`;
    }

    function trimInbound(ev) {
      if (!ev) return null;
      return {
        id: ev.id ?? null,
        messageId: ev.messageId ?? null,
        channelId: ev.channelId ?? null,
        accountId: ev.accountId ?? null,
        conversationId: ev.conversationId ?? null,
        conversationKey: ev.conversationKey ?? null,
        content: ev.content ?? null,
        linkedAt: ev.linkedAt ?? null,
        updatedAt: nowIso()
      };
    }

    function messagePreview(message) {
      if (!message || typeof message !== "object") return null;
      return {
        role: message.role ?? null,
        toolName: message.toolName ?? null,
        toolCallId: message.toolCallId ?? null,
        provider: message.provider ?? null,
        model: message.model ?? null,
        stopReason: message.stopReason ?? null,
        timestamp: message.timestamp ?? null,
        content: Array.isArray(message.content)
          ? { type: "array", length: message.content.length }
          : message.content == null
            ? null
            : { type: typeof message.content },
        isError: typeof message.isError === "boolean" ? message.isError : null
      };
    }

    function log(payload) {
      api.logger.info?.(`[nemoclaw-guard] ${JSON.stringify(payload)}`);
    }

    function upsertInboundEvent(state, inbound) {
      const idx = state.inboundEvents.findIndex((e) => e.id === inbound.id);
      if (idx >= 0) state.inboundEvents[idx] = { ...state.inboundEvents[idx], ...inbound };
      else state.inboundEvents.push(inbound);

      if (state.inboundEvents.length > MAX_INBOUND_EVENTS) {
        state.inboundEvents = state.inboundEvents.slice(-MAX_INBOUND_EVENTS);
      }
    }

    function findInboundById(state, inboundId) {
      return state.inboundEvents.find((e) => e.id === inboundId) || null;
    }

    function bindConversationToSession(state, conversationKey, sessionKey, agentId, inbound, method = "conversation_binding") {
      const ts = nowIso();

      state.activeSessionByConversation[conversationKey] = {
        sessionKey,
        agentId: agentId ?? null,
        conversationKey,
        updatedAt: ts
      };

      state.routeBindingByConversation[conversationKey] = {
        sessionKey,
        agentId: agentId ?? null,
        inboundId: inbound?.id ?? null,
        messageId: inbound?.messageId ?? null,
        updatedAt: ts
      };

      if (sessionKey && inbound) {
        inbound.linkedSessionKey = sessionKey;
        inbound.linkedAt = ts;

        state.linkedInboundBySession[sessionKey] = trimInbound(inbound);

        state.activeConversationBySession = state.activeConversationBySession || {};
        state.activeConversationBySession[sessionKey] = {
          conversationKey,
          inboundId: inbound?.id ?? null,
          messageId: inbound?.messageId ?? null,
          channelId: inbound?.channelId ?? null,
          accountId: inbound?.accountId ?? null,
          conversationId: inbound?.conversationId ?? null,
          setAt: ts,
          method
        };
      }
    }

    function resolveBoundInboundForSession(state, sessionKey) {
      for (const [conversationKey, binding] of Object.entries(state.activeSessionByConversation || {})) {
        if (binding?.sessionKey !== sessionKey) continue;

        const recent = state.recentInboundByConversation?.[conversationKey];
        if (recent?.id) {
          const ev = findInboundById(state, recent.id);
          if (ev) return { inbound: ev, method: "conversation_binding" };
        }

        const route = state.routeBindingByConversation?.[conversationKey];
        if (route?.inboundId) {
          const ev = findInboundById(state, route.inboundId);
          if (ev) return { inbound: ev, method: "route_binding" };
        }
      }
      return { inbound: null, method: null };
    }

    function resolveFallbackInbound(state) {
      const now = Date.now();
      const candidates = state.inboundEvents
        .filter((e) => !e.linkedAt)
        .filter((e) => {
          const t = Date.parse(e.seenAt || e.at || 0);
          return Number.isFinite(t) && now - t <= FALLBACK_WINDOW_MS;
        })
        .sort((a, b) => Date.parse(b.seenAt || b.at || 0) - Date.parse(a.seenAt || a.at || 0));

      return candidates[0] || null;
    }

    api.on("message_received", async (event, ctx) => {
      const state = readState();const inbound = {
        id:
          event?.metadata?.messageId ||
          event?.messageId ||
          `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        type: "message_received",
        at: nowIso(),
        seenAt: nowIso(),
        channelId: ctx?.channelId ?? null,
        accountId: ctx?.accountId ?? "default",
        conversationId: ctx?.conversationId ?? null,
        conversationKey: buildConversationKey({
          channelId: ctx?.channelId ?? null,
          accountId: ctx?.accountId ?? "default",
          conversationId: ctx?.conversationId ?? null
        }),
        content: typeof event?.content === "string" ? event.content : null,
        messageId: event?.metadata?.messageId ?? event?.messageId ?? null,
        from: event?.from ?? null,
        provider: event?.metadata?.provider ?? null,
        surface: event?.metadata?.surface ?? null,
        linkedSessionKey: null,
        linkedAt: null
      };

      const existingBinding = state.activeSessionByConversation[inbound.conversationKey];
      if (existingBinding?.sessionKey) {
        inbound.linkedSessionKey = existingBinding.sessionKey;
      }

      upsertInboundEvent(state, inbound);
      state.recentInboundByConversation[inbound.conversationKey] = { ...inbound };

      writeState(state);
      log(inbound);
    });

    api.on("before_message_write", (event, ctx) => {
      const state = readState();
      const msg = event?.message;
      const preview = messagePreview(msg);

      log({
        type: "before_message_write",
        at: nowIso(),
        sessionKey: ctx?.sessionKey ?? null,
        agentId: ctx?.agentId ?? null,
        messagePreview: preview
      });

      if (msg?.role !== "user" || !ctx?.sessionKey) return;

      const sessionKey = ctx.sessionKey;

      let resolved = resolveBoundInboundForSession(state, sessionKey);

      if (!resolved.inbound) {
        const fallback = resolveFallbackInbound(state);
        if (fallback) {
          resolved = { inbound: fallback, method: "recent_unlinked_fallback" };
        }
      }

      if (!resolved.inbound) return;

        bindConversationToSession(
          state,
          resolved.inbound.conversationKey,
          sessionKey,
          ctx?.agentId ?? null,
          resolved.inbound
        );

        const userText = normalizeApprovalReplyText(extractUserTextFromMessage(msg));

        processRuntimeApprovalReply(
          state,
          sessionKey,
          ctx?.agentId ?? null,
          userText
        );

        writeState(state);

      log({
        type: "session_linked",
        at: nowIso(),
        sessionKey,
        agentId: ctx?.agentId ?? null,
        method: resolved.method,
        linkedInbound: trimInbound(resolved.inbound)
      });
    });

    api.on("before_tool_call", async (event, ctx) => {
      const state = readState();
      const linkedInbound = ctx?.sessionKey ? state.linkedInboundBySession?.[ctx.sessionKey] ?? null : null;

      if (ctx?.sessionKey) {
        state.activeRunBySession[ctx.sessionKey] = {
          runId: ctx?.runId ?? null,
          toolName: ctx?.toolName ?? event?.toolName ?? null,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          updatedAt: nowIso()
        };
        writeState(state);
      }

      const params = event?.params && typeof event.params === "object"
        ? Object.fromEntries(
            Object.entries(event.params).filter(([, v]) =>
              v == null || typeof v === "string" || typeof v === "number" || typeof v === "boolean"
            )
          )
        : null;

      const toolName = ctx?.toolName ?? event?.toolName ?? null;

      if (toolName === "exec") {
        const command = extractExecCommand(event?.params);

        handleDuplicateRuntimeExec(
          state,
          ctx,
          event,
          toolName,
          command
        );

        if (isDangerousExecCommand(command)) {
          handleDangerousExecFlow(
            state,
            ctx,
            event,
            linkedInbound,
            toolName,
            command
          );
        }
      }

      if (shouldRequireApproval(event, ctx)) {
        const approvalId = registerPendingApproval(state, {
          toolName: ctx?.toolName ?? event?.toolName ?? null,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          runId: ctx?.runId ?? event?.runId ?? null,
          sessionKey: ctx?.sessionKey ?? null,
          conversationKey:
            state.activeConversationBySession?.[ctx?.sessionKey]?.conversationKey ?? null,
          paramsPreview: params
        });

        log({
          type: "approval_pending",
          at: nowIso(),
          approvalId,
          toolName: ctx?.toolName ?? event?.toolName ?? null,
          toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
          runId: ctx?.runId ?? event?.runId ?? null
        });

        clearGuardActionForSession(state, ctx?.sessionKey ?? null);
        writeState(state);
        throw new Error("Nemoclaw Guard approval required: " + approvalId);
      }

      log({
        type: "before_tool_call",
        at: nowIso(),
        sessionKey: ctx?.sessionKey ?? null,
        agentId: ctx?.agentId ?? null,
        toolName: ctx?.toolName ?? event?.toolName ?? null,
        toolCallId: ctx?.toolCallId ?? event?.toolCallId ?? null,
        runId: ctx?.runId ?? event?.runId ?? null,
        paramsPreview: params,
        linkedInbound
      });
    });

    api.on("agent_end", async (event, ctx) => {
      const state = readState();
      const linkedInbound = ctx?.sessionKey ? state.linkedInboundBySession?.[ctx.sessionKey] ?? null : null;

      if (ctx?.sessionKey && state.activeRunBySession[ctx.sessionKey]) {
        state.activeRunBySession[ctx.sessionKey].updatedAt = nowIso();
        writeState(state);
      }

      log({
        type: "agent_end",
        at: nowIso(),
        sessionKey: ctx?.sessionKey ?? null,
        agentId: ctx?.agentId ?? null,
        success: typeof event?.success === "boolean" ? event.success : null,
        durationMs: event?.durationMs ?? null,
        error: event?.error ?? null,
        messagesCount: Array.isArray(event?.messages) ? event.messages.length : null,
        linkedInbound
      });
    });
  }
};
