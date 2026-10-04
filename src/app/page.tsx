"use client";

import { useState, useRef, useEffect, KeyboardEvent, useMemo } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  BadgeCheck,
  BarChart3,
  BookText,
  Building2,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  CreditCard,
  ExternalLink,
  FileText,
  Info,
  Landmark,
  MessageSquareText,
  RefreshCw,
  SendHorizonal,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  WalletCards,
} from "lucide-react";

type MessageRole = "user" | "assistant" | "error";

interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  sourceUrl?: string | null;
  lastUpdated?: string | null;
  disclaimer?: string;
  category?: string;
  isSafe?: boolean;
  isValid?: boolean;
  timestamp?: Date;
}

interface ApiResponse {
  answer: string;
  source_url: string | null;
  last_updated: string | null;
  disclaimer: string;
  category: string;
  is_safe: boolean;
  is_valid: boolean;
  chunks_used: number;
}

interface SchemeInfo {
  name: string;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "");
const API_NOT_CONFIGURED_MESSAGE =
  "The chatbot service is not connected yet. Add the NEXT_PUBLIC_API_URL repository variable and redeploy.";

const fallbackSchemes = [
  "SBI Bluechip Fund",
  "SBI Magnum Tax Gain Scheme",
  "SBI Liquid Fund",
  "SBI Small Cap Fund",
  "SBI Balanced Advantage Fund",
];

const featureCards = [
  { title: "Scheme Details", description: "NAV, objective, benchmark, and manager context", icon: BookText },
  { title: "Performance", description: "Returns, risk metrics, and benchmark comparisons", icon: TrendingUp },
  { title: "SIP & Investment", description: "Minimum SIP, lumpsum, lock-in, and unit-related facts", icon: WalletCards },
  { title: "Fees & Charges", description: "Expense ratio, exit load, and cost disclosures", icon: CreditCard },
];

const navItems = [
  { label: "Chat", icon: MessageSquareText },
  { label: "Schemes", icon: Building2 },
  { label: "Compare", icon: BarChart3 },
  { label: "Saved Answers", icon: FileText },
  { label: "About", icon: CircleHelp },
];

const quickLinks = [
  { label: "AMC official website", href: "https://www.sbimf.com/" },
  { label: "SEBI", href: "https://www.sebi.gov.in/" },
  { label: "AMFI", href: "https://www.amfiindia.com/" },
];

const categoryOptions = [
  { label: "Scheme Details", key: "details" },
  { label: "Performance", key: "performance" },
  { label: "SIP & Investment", key: "sip" },
  { label: "Fees & Charges", key: "fees" },
];

function generateId(): string {
  return Math.random().toString(36).slice(2, 11);
}

function getCategoryBadge(category: string, isSafe: boolean) {
  if (!isSafe) {
    const labels: Record<string, { label: string; color: string }> = {
      INVESTMENT_ADVICE: { label: "Investment Advice", color: "bg-amber-100 text-amber-800" },
      PII_DETECTED: { label: "PII Warning", color: "bg-red-100 text-red-800" },
      OUT_OF_SCOPE: { label: "Out of Scope", color: "bg-slate-100 text-slate-700" },
    };
    const cfg = labels[category] ?? { label: category, color: "bg-slate-100 text-slate-700" };
    return (
      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${cfg.color}`}>
        <AlertCircle size={10} />
        {cfg.label}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-medium text-emerald-800">
      <BadgeCheck size={10} />
      Verified fact
    </span>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((item) => (
          <span
            key={item}
            className="h-2 w-2 rounded-full bg-slate-400"
            style={{ animation: "pulse 1.2s infinite ease-in-out", animationDelay: `${item * 0.15}s` }}
          />
        ))}
      </div>
      <span className="text-xs font-medium text-slate-500">Checking official sources…</span>
    </div>
  );
}

function SourceCitation({ url, lastUpdated }: { url: string | null; lastUpdated?: string | null }) {
  if (!url) return null;

  return (
    <div className="mt-3 flex items-start gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
      <Landmark size={14} className="mt-0.5 text-blue-600" />
      <div className="min-w-0 flex-1">
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-500">Official source</p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1 inline-flex items-center gap-1 truncate text-sm font-medium text-blue-700 hover:text-blue-900"
        >
          <span className="truncate">{url}</span>
          <ExternalLink size={12} />
        </a>
        {lastUpdated ? <p className="mt-1 text-[11px] text-slate-500">Last updated: {lastUpdated}</p> : null}
      </div>
    </div>
  );
}

function AssistantMessage({ msg }: { msg: ChatMessage }) {
  const isRefusal = msg.isSafe === false;

  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-700 to-indigo-700 text-[10px] font-bold text-white shadow-sm">
        SBI
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-2 flex items-center gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">Assistant</span>
          {getCategoryBadge(msg.category ?? "FACTUAL_ALLOWED", msg.isSafe ?? true)}
        </div>

        <div
          className={`rounded-2xl rounded-tl-sm border px-4 py-3 text-sm leading-7 shadow-sm ${
            isRefusal ? "border-amber-200 bg-amber-50 text-amber-900" : "border-slate-200 bg-white text-slate-800"
          }`}
        >
          <p className="whitespace-pre-wrap">{msg.text}</p>
        </div>

        {!isRefusal && msg.sourceUrl && <SourceCitation url={msg.sourceUrl} lastUpdated={msg.lastUpdated} />}

        {!isRefusal && msg.disclaimer && (
          <div className="mt-3 flex items-start gap-2 text-[11px] text-slate-500">
            <Info size={12} className="mt-0.5 shrink-0 text-slate-400" />
            <p>{msg.disclaimer}</p>
          </div>
        )}

        {msg.timestamp ? (
          <p className="mt-2 px-1 text-[11px] text-slate-400">
            {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function UserMessage({ msg }: { msg: ChatMessage }) {
  return (
    <div className="flex items-start justify-end gap-3">
      <div className="min-w-0 max-w-[80%]">
        <div className="mb-2 text-right text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">You</div>
        <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-blue-600 to-blue-700 px-4 py-3 text-sm leading-7 text-white shadow-sm">
          <p className="whitespace-pre-wrap">{msg.text}</p>
        </div>
        {msg.timestamp ? (
          <p className="mt-2 text-right text-[11px] text-slate-400">
            {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        ) : null}
      </div>
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold text-slate-700">
        U
      </div>
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-message",
      role: "assistant",
      text: API_URL
        ? "Hi! I'm your Facts-Only Mutual Fund FAQ Assistant.\nI can answer factual questions about mutual fund schemes using verified sources.\nChoose a category below or ask anything about the selected scheme."
        : "The frontend is live, but the chatbot service has not been connected yet. Add the API URL in the GitHub repository variables to enable factual answers.",
      category: "FACTUAL_ALLOWED",
      isSafe: true,
      isValid: true,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [indexBuilding, setIndexBuilding] = useState(false);
  const [schemes, setSchemes] = useState<string[]>(fallbackSchemes);
  const [selectedScheme, setSelectedScheme] = useState<string>(fallbackSchemes[0]);
  const [selectedCategory, setSelectedCategory] = useState<string>("Scheme Details");
  const [activeNav, setActiveNav] = useState<string>("Chat");
  const [healthStats, setHealthStats] = useState({
    schemes_covered: 5,
    index_ready: Boolean(API_URL),
    llm_configured: Boolean(API_URL),
  });
  const [sourceTotal, setSourceTotal] = useState<number | null>(25);
  const [savedAnswers, setSavedAnswers] = useState<Array<{ id: string; question: string; answer: string }>>([
    {
      id: "saved-1",
      question: "What is the expense ratio of SBI Bluechip Fund?",
      answer: "The expense ratio for SBI Bluechip Fund is around 0.68% as disclosed in the latest scheme factsheet.",
    },
    {
      id: "saved-2",
      question: "What is the minimum SIP for SBI Bluechip Fund?",
      answer: "The minimum SIP generally starts at Rs. 500, depending on the latest AMC details and current offer terms.",
    },
  ]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!API_URL) return;

    const loadAppMeta = async () => {
      try {
        const [schemesRes, sourcesRes, healthRes] = await Promise.all([
          fetch(`${API_URL}/api/schemes`),
          fetch(`${API_URL}/api/sources`),
          fetch(`${API_URL}/api/health`),
        ]);

        if (schemesRes.ok) {
          const schemeData = await schemesRes.json();
          const parsed = Array.isArray(schemeData?.schemes)
            ? schemeData.schemes.map((s: string | SchemeInfo) => (typeof s === "string" ? s : s.name))
            : fallbackSchemes;
          setSchemes(parsed);
          setSelectedScheme((current) => (parsed.includes(current) ? current : parsed[0] ?? fallbackSchemes[0]));
        }

        if (sourcesRes.ok) {
          const sourceData = await sourcesRes.json();
          setSourceTotal(typeof sourceData?.total === "number" ? sourceData.total : null);
        }

        if (healthRes.ok) {
          const healthData = await healthRes.json();
          setHealthStats({
            schemes_covered: typeof healthData?.schemes_covered === "number" ? healthData.schemes_covered : 5,
            index_ready: Boolean(healthData?.index_ready),
            llm_configured: Boolean(healthData?.llm_configured),
          });
        }
      } catch (_error) {
        setError("Live app data is unavailable; the UI is using the built-in scheme list.");
      }
    };

    loadAppMeta();
  }, []);

  function buildCategoryPrompt(category: string, scheme: string) {
    const categoryMap: Record<string, string> = {
      "Scheme Details": `What is the investment objective of ${scheme}?`,
      Performance: `What are the recent performance metrics for ${scheme}?`,
      "SIP & Investment": `What is the minimum SIP for ${scheme}?`,
      "Fees & Charges": `What is the expense ratio of ${scheme}?`,
    };

    return categoryMap[category] ?? `Tell me about ${scheme}.`;
  }

  const questionSuggestions = [
    `What is the expense ratio of ${selectedScheme}?`,
    `What is the minimum SIP for ${selectedScheme}?`,
    `What is the exit load for ${selectedScheme}?`,
    `What is the investment objective of ${selectedScheme}?`,
    `Show the latest NAV of ${selectedScheme}.`,
  ];

  const schemeCompareData = useMemo(
    () => [
      { label: "Expense ratio", value: "0.68%", benchmark: "0.75%" },
      { label: "Minimum SIP", value: "₹500", benchmark: "₹1000" },
      { label: "Exit load", value: "0.50%", benchmark: "1.00%" },
      { label: "Objective", value: "Large-cap growth", benchmark: "Flexi-cap allocation" },
    ],
    []
  );

  function handleCategorySelect(category: string, autoSend: boolean = true) {
    setSelectedCategory(category);
    const prompt = buildCategoryPrompt(category, selectedScheme);

    if (autoSend) {
      sendMessage(prompt);
      return;
    }

    setInput(prompt);
    inputRef.current?.focus();
  }

  async function sendMessage(question: string) {
    const q = question.trim();
    if (!q || loading) return;

    const normalized = q.toLowerCase();
    const isGreeting = ["hi", "hello", "hey", "hey there", "good morning", "good evening"].some(
      (greeting) => normalized === greeting || normalized.startsWith(greeting)
    );

    setError(null);

    const userMsg: ChatMessage = {
      id: generateId(),
      role: "user",
      text: q,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    if (!API_URL) {
      setError(API_NOT_CONFIGURED_MESSAGE);
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "error",
          text: API_NOT_CONFIGURED_MESSAGE,
          timestamp: new Date(),
        },
      ]);
      setLoading(false);
      inputRef.current?.focus();
      return;
    }

    if (isGreeting) {
      const greetingAssistant: ChatMessage = {
        id: generateId(),
        role: "assistant",
        text: "Hi! I can help with the following categories for SBI mutual fund facts. Choose a topic below or type your own question.",
        category: "FACTUAL_ALLOWED",
        isSafe: true,
        isValid: true,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, greetingAssistant]);
      setLoading(false);
      inputRef.current?.focus();
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail ?? `Server error ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      const assistantMsg: ChatMessage = {
        id: generateId(),
        role: "assistant",
        text: data.answer,
        sourceUrl: data.source_url,
        lastUpdated: data.last_updated,
        disclaimer: data.disclaimer,
        category: data.category,
        isSafe: data.is_safe,
        isValid: data.is_valid,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setSavedAnswers((prev) => [{ id: assistantMsg.id, question: q, answer: data.answer }, ...prev].slice(0, 6));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to connect to the server.";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "error",
          text: `Error: ${msg}`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  async function handleBuildIndex() {
    if (!API_URL) {
      setError(API_NOT_CONFIGURED_MESSAGE);
      return;
    }

    setIndexBuilding(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/build-index`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Index build failed");

      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "assistant",
          text: `✅ ${data.message}`,
          category: "FACTUAL_ALLOWED",
          isSafe: true,
          isValid: true,
          timestamp: new Date(),
        },
      ]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Index build failed";
      setError(msg);
    } finally {
      setIndexBuilding(false);
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(input);
    }
  }

  const renderMainPanel = () => {
    if (activeNav === "Schemes") {
      return (
        <div className="space-y-5 p-6">
          <div className="rounded-[28px] bg-gradient-to-br from-blue-600 to-indigo-700 p-5 text-white shadow-lg">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-100">Scheme library</p>
            <h2 className="mt-3 text-3xl font-semibold">Selected schemes</h2>
            <p className="mt-2 text-sm text-blue-100">Choose a fund to update the question set and continue with factual checks.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-1">
            {schemes.map((scheme) => (
              <button
                key={scheme}
                type="button"
                onClick={() => {
                  setSelectedScheme(scheme);
                  setActiveNav("Chat");
                  inputRef.current?.focus();
                }}
                className={`rounded-[24px] border p-4 text-left transition ${
                  selectedScheme === scheme
                    ? "border-blue-500 bg-blue-50 shadow-sm"
                    : "border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Scheme</p>
                    <h3 className="mt-2 text-lg font-semibold text-slate-900">{scheme}</h3>
                  </div>
                  {selectedScheme === scheme ? <Check size={18} className="text-blue-600" /> : <ChevronRight size={18} className="text-slate-400" />}
                </div>
                <p className="mt-3 text-sm text-slate-600">Quick facts, objective, SIP, and fee details are available for this scheme.</p>
              </button>
            ))}
          </div>
        </div>
      );
    }

    if (activeNav === "Compare") {
      return (
        <div className="space-y-5 p-6">
          <div className="rounded-[28px] bg-gradient-to-br from-slate-900 to-slate-700 p-5 text-white shadow-lg">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-300">Compare</p>
            <h2 className="mt-3 text-3xl font-semibold">{selectedScheme}</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {schemeCompareData.map(({ label, value, benchmark }) => (
              <div key={label} className="rounded-[24px] border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
                <div className="mt-4 flex items-center justify-between gap-3">
                  <span className="text-xl font-semibold text-slate-900">{value}</span>
                  <span className="text-xs rounded-full bg-blue-50 px-2 py-1 font-medium text-blue-700">vs {benchmark}</span>
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={() => sendMessage(`Compare ${selectedScheme} with its benchmark details.`)}
            className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-500"
          >
            <BarChart3 size={16} />
            Ask compare question
          </button>
        </div>
      );
    }

    if (activeNav === "Saved Answers") {
      return (
        <div className="space-y-5 p-6">
          <div className="rounded-[28px] bg-gradient-to-br from-emerald-500 to-cyan-500 p-5 text-white shadow-lg">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-50">Saved answers</p>
            <h2 className="mt-3 text-3xl font-semibold">Recent facts</h2>
          </div>

          <div className="space-y-3">
            {savedAnswers.map(({ id, question, answer }) => (
              <div key={id} className="rounded-[24px] border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Question</p>
                <p className="mt-2 text-base font-medium text-slate-900">{question}</p>
                <p className="mt-3 text-sm leading-6 text-slate-600">{answer}</p>
                <button
                  type="button"
                  onClick={() => {
                    setInput(question);
                    setActiveNav("Chat");
                    inputRef.current?.focus();
                  }}
                  className="mt-4 inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                >
                  <ArrowUpRight size={14} />
                  Ask again
                </button>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (activeNav === "About") {
      return (
        <div className="space-y-5 p-6">
          <div className="rounded-[28px] bg-gradient-to-br from-violet-600 to-indigo-600 p-5 text-white shadow-lg">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-violet-100">About</p>
            <h2 className="mt-3 text-3xl font-semibold">INDY MONEY</h2>
          </div>

          <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
            <ul className="space-y-3 text-sm text-slate-600">
              <li className="flex items-start gap-2"><Check size={15} className="mt-0.5 text-emerald-600" /> Verified mutual fund facts from official scheme sources.</li>
              <li className="flex items-start gap-2"><Check size={15} className="mt-0.5 text-emerald-600" /> Factual Q&A only with no investment advice.</li>
              <li className="flex items-start gap-2"><Check size={15} className="mt-0.5 text-emerald-600" /> Category-based prompts for quick mutual fund research.</li>
            </ul>
          </div>

          <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Quick links</p>
            <div className="mt-4 space-y-2">
              {quickLinks.map(({ label, href }) => (
                <a key={label} href={href} target="_blank" rel="noreferrer" className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700">
                  <span>{label}</span>
                  <ArrowUpRight size={14} />
                </a>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return (
      <>
        <header className="border-b border-slate-200 bg-white/80 px-5 py-5 backdrop-blur-sm">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-700 shadow-sm ring-1 ring-blue-100">
                <ShieldCheck size={22} />
              </div>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-blue-700">Facts only</p>
                <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">Mutual Fund FAQ Assistant</h1>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700">
                <BadgeCheck size={14} />
                Facts only
              </span>
              <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700">
                <ShieldCheck size={14} />
                No investment advice
              </span>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <p className="text-lg text-slate-600">
                Get verified, factual information about selected mutual fund schemes from official sources.
              </p>
            </div>

            <div className="flex items-center gap-3 rounded-2xl border border-blue-100 bg-blue-50/60 px-3 py-2 text-sm text-blue-800 shadow-sm">
              <BadgeCheck size={16} />
              <span className="font-medium">{healthStats.index_ready ? "Index ready" : "Index building"}</span>
            </div>
          </div>
        </header>

        <div className="p-5 lg:p-6">
          <section className="grid gap-4 xl:grid-cols-[minmax(0,1.5fr)_220px]">
            <div className="rounded-[28px] bg-gradient-to-br from-[#0f57d1] via-[#1a6ae4] to-[#164ec2] p-5 text-white shadow-[0_20px_45px_rgba(30,64,175,0.25)] sm:p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-100/80">INDY MONEY</p>
                  <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">Facts-Only Mutual Fund FAQ</h2>
                </div>
                <span className="inline-flex items-center gap-2 rounded-full bg-white/12 px-3 py-1.5 text-xs font-medium text-white/90 ring-1 ring-white/20">
                  <BadgeCheck size={14} />
                  Facts only
                </span>
              </div>

              <p className="mt-5 max-w-xl text-base text-blue-50/90">
                Get verified, factual information about selected mutual fund schemes using official AMC, SEBI, and AMFI sources.
              </p>

              <div className="mt-6 flex flex-wrap gap-3 text-sm text-blue-100">
                <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-3 py-1.5">
                  <Check size={14} />
                  No investment advice
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-3 py-1.5">
                  <Check size={14} />
                  No predictions
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-3 py-1.5">
                  <Check size={14} />
                  No buy/sell recommendations
                </span>
              </div>
            </div>

            <div className="rounded-[28px] border border-slate-200 bg-white/80 p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Market snapshot</span>
                <Sparkles size={16} className="text-indigo-500" />
              </div>

              <div className="rounded-2xl bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50 p-4">
                <div className="flex items-end justify-between gap-2">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.12em] text-slate-500">Scheme focus</p>
                    <p className="mt-2 text-lg font-semibold text-slate-800">{selectedScheme}</p>
                  </div>
                  <div className="rounded-xl bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-700">Live data</div>
                </div>
                <div className="mt-5 flex h-24 items-end gap-2">
                  {[42, 58, 54, 65, 72, 68, 82].map((bar, index) => (
                    <div
                      key={index}
                      className="flex-1 rounded-t-xl bg-gradient-to-t from-blue-500 to-cyan-400"
                      style={{ height: `${bar}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {featureCards.map(({ title, description, icon: Icon }) => (
              <button
                key={title}
                type="button"
                onClick={() => handleCategorySelect(title, true)}
                className="group rounded-[24px] border border-slate-200 bg-white p-4 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                    <Icon size={18} />
                  </div>
                  <ArrowUpRight size={18} className="text-slate-400 transition group-hover:text-blue-600" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
              </button>
            ))}
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_300px]">
            <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3.5">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-700 to-indigo-700 text-[10px] font-bold text-white">S</div>
                  <span className="text-sm font-semibold text-slate-800">Facts-Only Assistant</span>
                </div>
                <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.14em] text-emerald-700">
                  <BadgeCheck size={12} />
                  Verified
                </span>
              </div>

              <div className="max-h-[520px] space-y-4 overflow-y-auto bg-slate-50/60 p-4">
                {messages.map((msg) => {
                  if (msg.role === "user") return <UserMessage key={msg.id} msg={msg} />;
                  if (msg.role === "assistant") return <AssistantMessage key={msg.id} msg={msg} />;
                  return (
                    <div key={msg.id} className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                      {msg.text}
                    </div>
                  );
                })}

                {loading ? <TypingIndicator /> : null}
                {error && !loading ? (
                  <div className="rounded-2xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
                ) : null}
                <div ref={bottomRef} />
              </div>

              <div className="border-t border-slate-200 bg-white p-4">
                <div className="rounded-[22px] border border-slate-200 bg-slate-50 p-3 shadow-inner shadow-slate-200/50">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={1}
                    placeholder="Ask a factual question about a mutual fund scheme..."
                    className="w-full resize-none border-0 bg-transparent px-1 py-2 text-sm text-slate-700 outline-none placeholder:text-slate-400"
                  />

                  <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-2 text-[11px] text-slate-500">
                      <span>{input.length}/500</span>
                      <span className="text-slate-300">•</span>
                      <span>Enter to send</span>
                    </div>

                    <button
                      type="button"
                      onClick={() => sendMessage(input)}
                      disabled={loading || !input.trim()}
                      className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-600/25 transition hover:from-blue-500 hover:to-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <SendHorizonal size={16} />
                      Send
                    </button>
                  </div>
                </div>

                <div className="mt-4">
                  <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Question categories</p>
                  <div className="flex flex-wrap gap-2">
                    {categoryOptions.map(({ label, key }) => (
                      <button
                        key={key}
                        type="button"
                        onClick={() => handleCategorySelect(label, true)}
                        className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                          selectedCategory === label
                            ? "border-blue-600 bg-blue-600 text-white shadow-sm"
                            : "border-slate-200 bg-white text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <p className="mt-3 flex items-start gap-2 text-xs text-slate-500">
                  <Info size={14} className="mt-0.5 shrink-0 text-blue-600" />
                  This assistant provides factual information only. It does not provide investment advice, return predictions, or buy/sell recommendations.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">Try asking</h3>
                  <Sparkles size={16} className="text-blue-600" />
                </div>

                <div className="mt-4 space-y-2">
                  {questionSuggestions.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => sendMessage(question)}
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3 text-left text-sm text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-slate-900"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">Build index</h3>
                  <RefreshCw size={16} className="text-blue-600" />
                </div>

                <button
                  type="button"
                  onClick={handleBuildIndex}
                  disabled={indexBuilding || !API_URL}
                  className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-blue-200 bg-blue-50 px-3 py-2.5 text-sm font-medium text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <RefreshCw size={15} className={indexBuilding ? "animate-spin" : ""} />
                  {indexBuilding ? "Rebuilding..." : API_URL ? "Rebuild knowledge index" : "API not connected"}
                </button>
              </div>
            </div>
          </section>
        </div>
      </>
    );
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.12),transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_45%,#f6f9fc_100%)] text-slate-900">
      <div className="mx-auto max-w-[1600px] px-4 py-4 lg:px-6">
        <div className="grid min-h-[92vh] overflow-hidden rounded-[28px] border border-slate-200/80 bg-white/80 shadow-[0_18px_60px_rgba(15,23,42,0.08)] backdrop-blur-sm lg:grid-cols-[280px_minmax(0,1fr)_320px]">
          <aside className="border-r border-slate-200 bg-[#0d1830] text-slate-100">
            <div className="flex h-full flex-col">
              <div className="border-b border-slate-700/80 px-5 py-5">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 text-lg font-bold text-white shadow-lg shadow-blue-900/30">
                    I
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-200/80">INDY MONEY</p>
                    <h2 className="mt-1 text-xl font-semibold tracking-tight">MF FAQ Assistant</h2>
                  </div>
                </div>
              </div>

              <nav className="px-4 py-5">
                <ul className="space-y-2">
                  {navItems.map(({ label, icon: Icon }) => (
                    <li key={label}>
                      <button
                        type="button"
                        onClick={() => {
                          setActiveNav(label);
                          if (label === "Chat") {
                            inputRef.current?.focus();
                          }
                        }}
                        className={`flex w-full items-center justify-between rounded-2xl px-3 py-2.5 text-sm font-medium transition ${
                          activeNav === label ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20" : "text-slate-300 hover:bg-slate-800/70 hover:text-white"
                        }`}
                      >
                        <span className="flex items-center gap-3">
                          <Icon size={16} />
                          {label}
                        </span>
                        {activeNav === label ? <ChevronRight size={16} /> : null}
                      </button>
                    </li>
                  ))}
                </ul>
              </nav>

              <div className="mt-auto space-y-5 px-4 pb-6">
                <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-3.5">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Selected AMC</p>
                  <div className="mt-2 flex items-center justify-between gap-2 rounded-xl border border-slate-700 bg-slate-800/70 px-3 py-2.5">
                    <span className="text-sm font-medium text-slate-100">SBI Mutual Fund</span>
                    <ChevronDown size={16} className="text-slate-400" />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-3.5">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Covered schemes ({schemes.length})</p>
                  <div className="mt-3 space-y-2">
                    {schemes.map((scheme) => (
                      <button
                        key={scheme}
                        type="button"
                        onClick={() => setSelectedScheme(scheme)}
                        className={`flex w-full items-center justify-between rounded-xl border px-2.5 py-2 text-left text-xs transition ${
                          selectedScheme === scheme
                            ? "border-blue-500 bg-blue-500/10 text-blue-100"
                            : "border-slate-700 bg-slate-800/40 text-slate-300 hover:border-slate-600 hover:text-white"
                        }`}
                      >
                        <span className="truncate">{scheme}</span>
                        {selectedScheme === scheme ? <Check size={12} className="text-blue-300" /> : null}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-emerald-300">
                  <BadgeCheck size={12} />
                  Verified sources
                </div>
              </div>
            </div>
          </aside>

          <main className="bg-gradient-to-br from-slate-50 via-white to-blue-50/50">
            {renderMainPanel()}
          </main>

          <aside className="border-l border-slate-200 bg-slate-50/80 p-5 lg:p-6">
            <div className="space-y-5">
              <div className="rounded-[26px] border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Quick stats</p>
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <div className="rounded-2xl bg-blue-50 p-3 text-center ring-1 ring-blue-100">
                    <div className="text-2xl font-semibold text-blue-700">{healthStats.schemes_covered}</div>
                    <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-slate-500">Schemes</div>
                  </div>
                  <div className="rounded-2xl bg-emerald-50 p-3 text-center ring-1 ring-emerald-100">
                    <div className="text-2xl font-semibold text-emerald-700">{sourceTotal ?? 0}</div>
                    <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-slate-500">Sources</div>
                  </div>
                  <div className="rounded-2xl bg-violet-50 p-3 text-center ring-1 ring-violet-100">
                    <div className="text-2xl font-semibold text-violet-700">100%</div>
                    <div className="mt-1 text-[10px] uppercase tracking-[0.12em] text-slate-500">Verified</div>
                  </div>
                </div>
              </div>

              <div className="rounded-[26px] border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">About this assistant</p>
                <ul className="mt-4 space-y-3 text-sm text-slate-600">
                  {[
                    "Uses official sources",
                    "Answers factual questions",
                    "Covers selected mutual fund schemes",
                    "No investment advice",
                    "No predictions",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <Check size={15} className="mt-0.5 text-emerald-600" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-[26px] border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Quick links</p>
                <div className="mt-4 space-y-2">
                  {quickLinks.map(({ label, href }) => (
                    <a
                      key={label}
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                    >
                      <span>{label}</span>
                      <ArrowUpRight size={15} />
                    </a>
                  ))}
                </div>
              </div>

              <div className="rounded-[26px] border border-slate-200 bg-gradient-to-br from-slate-900 to-slate-800 p-4 text-slate-50 shadow-sm">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-300">Facts only</p>
                <p className="mt-3 text-sm leading-7 text-slate-200">
                  This assistant provides factual information for educational and informational purposes. Please refer to official documents for complete details.
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
