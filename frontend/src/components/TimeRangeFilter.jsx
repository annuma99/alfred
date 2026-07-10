const RANGES = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
];

/**
 * Presentation-only -- doesn't fetch anything itself. Just reports the
 * user's choice up to App.jsx, which triggers MapView to re-fetch pins.
 */
export default function TimeRangeFilter({ value, onChange }) {
  return (
    <div
      style={{
        display: "flex",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "4px",
        overflow: "hidden",
      }}
    >
      {RANGES.map((range) => (
        <button
          key={range.value}
          onClick={() => onChange(range.value)}
          style={{
            padding: "8px 16px",
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            border: "none",
            borderRight: "1px solid var(--border)",
            cursor: "pointer",
            background: value === range.value ? "var(--text)" : "transparent",
            color: value === range.value ? "var(--bg)" : "var(--text)",
          }}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
}
