import React, { createContext, useContext, useState } from "react";
import { getStatusLabel, STATUS_LABELS, useLang } from "./i18n";

type ToastItem = { id: number; text: string; kind: "success" | "error" };

const ToastCtx = createContext<{
  toast: (text: string, kind?: "success" | "error") => void;
}>({ toast: () => {} });

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const toast = (text: string, kind: "success" | "error" = "success") => {
    const id = Date.now() + Math.random();
    setItems((prev) => [...prev, { id, text, kind }]);
    setTimeout(() => {
      setItems((prev) => prev.filter((x) => x.id !== id));
    }, 3200);
  };
  return (
    <ToastCtx.Provider value={{ toast }}>
      {children}
      <div
        aria-live="polite"
        className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-[calc(100%-2rem)] sm:w-auto"
      >
        {items.map((item) => (
          <div
            key={item.id}
            role="status"
            className="wm-card px-4 py-3 text-xs font-semibold tracking-wide flex items-center justify-between gap-3 shadow-md"
            style={{
              backgroundColor: item.kind === "error" ? "#4A1C1C" : "#14213D",
              color: "#FFFFFF",
              borderColor: item.kind === "error" ? "#4A1C1C" : "#D2B98B",
            }}
          >
            <span>{item.text}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

export function useToast() {
  return useContext(ToastCtx);
}

export function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4" aria-busy="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="wm-card overflow-hidden">
          <div className="wm-skeleton aspect-[3/4] w-full rounded-none" />
          <div className="p-3.5 space-y-2">
            <div className="wm-skeleton h-4 w-3/4" />
            <div className="wm-skeleton h-4 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function EmptyState({
  text,
  sub,
  action,
}: {
  text: string;
  sub?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="wm-card p-10 text-center space-y-3">
      <div className="w-12 h-12 mx-auto rounded-[4px] bg-[#F6F2EA] border border-[#D9D3C6] flex items-center justify-center text-[#14213D]">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
        >
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M3 10h18" />
        </svg>
      </div>
      <div className="font-serif-heading text-xl font-semibold text-[#14213D]">
        {text}
      </div>
      {sub && <div className="text-xs text-[#4E5B73] max-w-sm mx-auto">{sub}</div>}
      {action && <div className="pt-2">{action}</div>}
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const { lang } = useLang();
  const styles: Record<string, { bg: string; fg: string; border: string }> = {
    new: { bg: "#EFE6D5", fg: "#14213D", border: "#D2B98B" },
    awaiting_payment: { bg: "#F6F2EA", fg: "#4E5B73", border: "#D9D3C6" },
    paid: { bg: "#14213D", fg: "#FFFFFF", border: "#14213D" },
    ordered_china: { bg: "#F6F2EA", fg: "#14213D", border: "#14213D" },
    china_warehouse: { bg: "#F6F2EA", fg: "#14213D", border: "#7D8AA3" },
    in_transit: { bg: "#EFE6D5", fg: "#14213D", border: "#14213D" },
    in_uz: { bg: "#14213D", fg: "#D2B98B", border: "#14213D" },
    delivered: { bg: "#E6EFE9", fg: "#183A27", border: "#8FB39E" },
    cancelled: { bg: "#F5E8E8", fg: "#5C1F1F", border: "#CFA8A8" },
  };
  const st = styles[status] || styles.new;
  return (
    <span
      className="wm-badge"
      style={{
        backgroundColor: st.bg,
        color: st.fg,
        borderColor: st.border,
      }}
    >
      {getStatusLabel(status, lang)}
    </span>
  );
}

export function ConfirmModal({
  open,
  title,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const { t } = useLang();
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-[2px]">
      <div className="wm-card p-6 max-w-sm w-full space-y-5">
        <div className="space-y-1">
          <div className="text-[11px] uppercase tracking-widest text-[#7D8AA3] font-semibold">
            WHITMORE
          </div>
          <h3 className="text-xl font-semibold text-[#14213D]">{title}</h3>
        </div>
        <div className="flex justify-end gap-2 pt-2 border-t border-[#D9D3C6]">
          <button type="button" className="wm-btn-outline" onClick={onCancel}>
            {t.cancel}
          </button>
          <button type="button" className="wm-btn" onClick={onConfirm}>
            {t.confirm}
          </button>
        </div>
      </div>
    </div>
  );
}

export function LangSwitcher() {
  const { lang, setLang } = useLang();
  return (
    <div
      role="group"
      aria-label="Language switcher"
      className="inline-flex border border-[#D9D3C6] rounded-[4px] overflow-hidden bg-white"
    >
      <button
        type="button"
        onClick={() => setLang("uz")}
        className="min-h-[44px] px-3 text-xs font-semibold cursor-pointer transition-colors"
        style={{
          backgroundColor: lang === "uz" ? "#14213D" : "#FFFFFF",
          color: lang === "uz" ? "#FFFFFF" : "#14213D",
        }}
      >
        UZ
      </button>
      <button
        type="button"
        onClick={() => setLang("ru")}
        className="min-h-[44px] px-3 text-xs font-semibold cursor-pointer transition-colors border-l border-[#D9D3C6]"
        style={{
          backgroundColor: lang === "ru" ? "#14213D" : "#FFFFFF",
          color: lang === "ru" ? "#FFFFFF" : "#14213D",
        }}
      >
        RU
      </button>
    </div>
  );
}
