"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Markdown } from "@/lib/markdown";
import type {
  CompassAction,
  CompassCitation,
  CompassContextPayload,
  FleetSnapshot,
  LifecyclePhase,
} from "@/lib/types";

// Compass: the in-platform advisor, delivered as a global slide-over.
// Two surfaces: "Ask Compass" (NL Q&A grounded on the live run + corpus, with
// act-on-confirm actions) and "Agent View" (Sentinel's surfaced issues feed).

type View = "ask" | "agent";

interface Msg {
  role: "user" | "compass";
  text: string;
  source?: string;
  citations?: CompassCitation[];
  actions?: CompassAction[];
}

interface CompassApi {
  open: boolean;
  openCompass: (ctx?: CompassContextPayload, prompt?: string) => void;
  closeCompass: () => void;
}

const CompassContext = createContext<CompassApi | null>(null);

export function useCompass(): CompassApi {
  const c = useContext(CompassContext);
  if (!c) throw new Error("useCompass must be used within <CompassProvider>");
  return c;
}

const PHASE_LABEL: Record<LifecyclePhase, string> = {
  manage: "Manage",
  govern: "Govern",
  operate: "Operate",
  optimize: "Optimize",
};

function greeting(ctx: CompassContextPayload): Msg {
  if (ctx.run_id) {
    return {
      role: "compass",
      source: "deterministic",
      text:
        `Hey, I'm **Compass**. I've got ${ctx.agent_name ? `**${ctx.agent_name}**` : "this onboarding run"} open in front of me. ` +
        "Ask me to break down the decision, dig into a finding, or tell you what's next, and if you'd like, I'll walk this agent through the rest of its lifecycle for you.",
    };
  }
  return {
    role: "compass",
    source: "deterministic",
    text:
      "Hey, I'm **Compass**, your guide around here. Ask me anything about an agent, a decision, or " +
      "the six-phase lifecycle. I can also do things for you, and I'll always check with you before I act.",
    actions: [
      { id: "preboard", kind: "navigate", label: "Go to Pre-Boarding", href: "/agents" },
      { id: "capabilities", kind: "ask", label: "What can Compass do?", prompt: "What can you help me do on this platform?" },
    ],
  };
}

export function CompassProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [ctx, setCtx] = useState<CompassContextPayload>({});
  const [seed, setSeed] = useState<string | null>(null);
  const [resetKey, setResetKey] = useState(0);

  const openCompass = useCallback((c?: CompassContextPayload, prompt?: string) => {
    setOpen(true);
    if (c) {
      setCtx(c);
      setResetKey((k) => k + 1); // explicit context → fresh conversation
    }
    if (prompt) setSeed(prompt);
  }, []);

  const closeCompass = useCallback(() => setOpen(false), []);

  return (
    <CompassContext.Provider value={{ open, openCompass, closeCompass }}>
      {children}
      <CompassPanel
        open={open}
        ctx={ctx}
        seed={seed}
        resetKey={resetKey}
        onSeedConsumed={() => setSeed(null)}
        onClose={closeCompass}
      />
    </CompassContext.Provider>
  );
}

function CompassPanel({
  open,
  ctx,
  seed,
  resetKey,
  onSeedConsumed,
  onClose,
}: {
  open: boolean;
  ctx: CompassContextPayload;
  seed: string | null;
  resetKey: number;
  onSeedConsumed: () => void;
  onClose: () => void;
}) {
  const router = useRouter();
  const [view, setView] = useState<View>("ask");
  const [messages, setMessages] = useState<Msg[]>([greeting(ctx)]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState<CompassAction | null>(null);
  const [fleet, setFleet] = useState<FleetSnapshot | null>(null);
  const [fleetErr, setFleetErr] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  async function send(text: string) {
    const q = text.trim();
    if (!q || busy) return;
    setInput("");
    setConfirm(null);
    setMessages((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    try {
      const r = await api.askCompass(q, ctx);
      setMessages((m) => [
        ...m,
        { role: "compass", text: r.answer, source: r.source, citations: r.citations, actions: r.suggested_actions },
      ]);
    } catch (e) {
      setMessages((m) => [...m, { role: "compass", text: `I couldn't reach my brain just then. ${String(e)}` }]);
    } finally {
      setBusy(false);
    }
  }

  async function runAction(a: CompassAction) {
    if (a.kind === "navigate" && a.href) {
      onClose();
      router.push(a.href);
      return;
    }
    if (a.kind === "ask" && a.prompt) {
      void send(a.prompt);
      return;
    }
    if (a.kind === "advance_lifecycle") {
      if (a.confirm && confirm?.id !== a.id) {
        setConfirm(a);
        return;
      }
      setConfirm(null);
      if (!a.candidate_id || busy) return;
      setMessages((m) => [...m, { role: "user", text: a.label }]);
      setBusy(true);
      try {
        const r = await api.runFullLifecycle(a.candidate_id);
        const body = r.events.length
          ? r.events.map((e) => `- **${PHASE_LABEL[e.phase]}**: ${e.summary}`).join("\n")
          : "Looks like every lifecycle phase was already attested on this agent.";
        setMessages((m) => [
          ...m,
          {
            role: "compass",
            source: "deterministic",
            text: `All set. Here's what just landed on the personnel file, each one signed and hash-chained:\n\n${body}`,
          },
        ]);
      } catch (e) {
        setMessages((m) => [...m, { role: "compass", text: `I couldn't advance the lifecycle: ${String(e)}` }]);
      } finally {
        setBusy(false);
      }
    }
  }

  // Fresh conversation whenever the context changes.
  useEffect(() => {
    setMessages([greeting(ctx)]);
    setView("ask");
    setConfirm(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetKey]);

  // Auto-send a seeded prompt once after opening.
  useEffect(() => {
    if (open && seed) {
      void send(seed);
      onSeedConsumed();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, seed]);

  // Lazy-load the Sentinel feed when Agent View is first shown.
  useEffect(() => {
    if (open && view === "agent" && !fleet && !fleetErr) {
      api.operateFleet().then(setFleet).catch((e) => setFleetErr(String(e)));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, view]);

  // Autoscroll the transcript.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  return (
    <>
      <div
        aria-hidden={!open}
        onClick={onClose}
        className={`fixed inset-0 z-[60] bg-black/30 transition-opacity duration-300 ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        role="dialog"
        aria-label="Compass advisor"
        aria-hidden={!open}
        className={`fixed right-0 top-0 z-[70] flex h-full w-full max-w-md flex-col border-l border-outline-variant/40 bg-surface shadow-2xl transition-transform duration-300 ${
          open ? "translate-x-0" : "pointer-events-none translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between gap-2 border-b border-outline-variant/40 px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/10 text-primary">
              <span className="material-symbols-outlined text-[20px]">explore</span>
            </span>
            <div>
              <div className="font-heading text-sm font-semibold text-on-surface">Compass</div>
              <div className="text-[11px] text-on-surface-variant">In-platform advisor</div>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close Compass"
            className="rounded-lg p-1.5 text-on-surface-variant hover:bg-surface-container"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div role="tablist" className="flex gap-1 border-b border-outline-variant/40 px-3 py-2">
          {(["ask", "agent"] as View[]).map((v) => (
            <button
              key={v}
              role="tab"
              aria-selected={view === v}
              onClick={() => setView(v)}
              className={`rounded-md px-3 py-1.5 text-xs font-semibold ${
                view === v ? "bg-primary text-on-primary" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              {v === "ask" ? "Ask Compass" : "Agent View"}
            </button>
          ))}
        </div>

        {view === "ask" ? (
          <>
            <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
              {messages.map((m, i) => (
                <MessageBubble
                  key={i}
                  msg={m}
                  confirm={confirm}
                  onAction={runAction}
                  onCancelConfirm={() => setConfirm(null)}
                />
              ))}
              {busy && <div className="pl-1 text-xs text-on-surface-variant">Compass is thinking it over…</div>}
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void send(input);
              }}
              className="border-t border-outline-variant/40 p-3"
            >
              <div className="flex items-end gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send(input);
                    }
                  }}
                  rows={1}
                  placeholder="Ask Compass…"
                  className="max-h-32 min-h-[40px] flex-1 resize-none rounded-lg border border-outline-variant/60 bg-surface-container-lowest px-3 py-2 text-sm text-on-surface focus:border-primary focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={busy || !input.trim()}
                  className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-on-primary hover:bg-primary-hover disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </form>
          </>
        ) : (
          <AgentView
            fleet={fleet}
            err={fleetErr}
            onAsk={(prompt) => {
              setView("ask");
              void send(prompt);
            }}
          />
        )}
      </aside>
    </>
  );
}

function iconFor(kind: CompassAction["kind"]): string {
  if (kind === "navigate") return "arrow_forward";
  if (kind === "advance_lifecycle") return "play_arrow";
  return "help";
}

function MessageBubble({
  msg,
  confirm,
  onAction,
  onCancelConfirm,
}: {
  msg: Msg;
  confirm: CompassAction | null;
  onAction: (a: CompassAction) => void;
  onCancelConfirm: () => void;
}) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-primary px-3 py-2 text-sm text-on-primary">
          {msg.text}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-2">
      <div className="max-w-[92%] rounded-2xl rounded-bl-sm border border-outline-variant/40 bg-surface-container-lowest px-3 py-2">
        <Markdown text={msg.text} />
        {msg.source === "gemini" && (
          <div className="mt-1.5 inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
            <span className="material-symbols-outlined text-[12px]">auto_awesome</span> Gemini · Vertex AI
          </div>
        )}
      </div>
      {msg.citations?.length ? (
        <div className="flex flex-wrap gap-1 pl-1">
          {msg.citations.map((c, i) => (
            <span
              key={i}
              title={c.snippet}
              className="rounded bg-surface-container px-1.5 py-0.5 text-[10px] text-on-surface-variant"
            >
              {c.title}
            </span>
          ))}
        </div>
      ) : null}
      {msg.actions?.length ? (
        <div className="flex flex-wrap gap-1.5 pl-1">
          {msg.actions.map((a) =>
            confirm?.id === a.id ? (
              <span
                key={a.id}
                className="inline-flex items-center gap-1.5 rounded-lg border border-primary/50 bg-primary/5 px-2 py-1 text-xs text-on-surface"
              >
                {a.description ?? "Confirm this action?"}
                <button
                  onClick={() => onAction(a)}
                  className="rounded bg-primary px-2 py-0.5 text-[11px] font-semibold text-on-primary"
                >
                  Confirm
                </button>
                <button onClick={onCancelConfirm} className="rounded px-1.5 py-0.5 text-[11px] text-on-surface-variant">
                  Cancel
                </button>
              </span>
            ) : (
              <button
                key={a.id}
                onClick={() => onAction(a)}
                className="inline-flex items-center gap-1 rounded-lg border border-outline-variant/60 px-2 py-1 text-xs font-medium text-on-surface hover:border-primary/50 hover:bg-primary/5"
              >
                <span className="material-symbols-outlined text-[14px]">{iconFor(a.kind)}</span>
                {a.label}
              </button>
            ),
          )}
        </div>
      ) : null}
    </div>
  );
}

function AgentView({
  fleet,
  err,
  onAsk,
}: {
  fleet: FleetSnapshot | null;
  err: string | null;
  onAsk: (prompt: string) => void;
}) {
  if (err) return <div className="p-4 text-sm text-decision-blocked">I couldn&apos;t load the Sentinel feed: {err}</div>;
  if (!fleet) return <div className="p-4 text-sm text-on-surface-variant">Pulling up the Sentinel feed…</div>;
  const flagged = fleet.members.filter((m) => m.anomalies.length > 0);
  return (
    <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
      <div className="rounded-lg border border-outline-variant/40 bg-surface-container-lowest p-3 text-xs text-on-surface-variant">
        <span className="font-semibold text-on-surface">Sentinel</span> keeps watch over the active roster in
        the background and flags anything worth a look here. {fleet.summary.agents_with_anomalies} of{" "}
        {fleet.summary.agents} agents have open signals.
      </div>
      {flagged.length === 0 ? (
        <p className="text-sm text-decision-ready">Nothing flagged across the roster. Everyone&apos;s within policy.</p>
      ) : (
        flagged.map((m) => (
          <div
            key={m.candidate_agent_id}
            className="rounded-xl border border-decision-conditional/40 bg-decision-conditional/5 p-3"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="font-heading text-sm font-semibold text-on-surface">{m.name}</div>
              <span className="text-[10px] text-on-surface-variant">{m.onboarding_decision}</span>
            </div>
            <ul className="mt-2 space-y-1">
              {m.anomalies.map((a) => (
                <li key={a.rule_id} className="text-xs text-on-surface-variant">
                  <span
                    className={`mr-1 rounded px-1 text-[10px] font-bold uppercase ${
                      a.severity === "high"
                        ? "bg-decision-blocked/15 text-decision-blocked"
                        : "bg-decision-conditional/15 text-decision-conditional"
                    }`}
                  >
                    {a.severity}
                  </span>
                  {a.summary}
                </li>
              ))}
            </ul>
            <button
              onClick={() =>
                onAsk(
                  `What's going on with ${m.name} (${m.candidate_agent_id}), and what should I do about the flagged signals?`,
                )
              }
              className="mt-2 text-xs font-semibold text-primary hover:underline"
            >
              Ask Compass about this →
            </button>
          </div>
        ))
      )}
    </div>
  );
}
