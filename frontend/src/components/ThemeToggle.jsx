export default function ThemeToggle({ theme, onToggle }) {
  return (
    <button
      onClick={onToggle}
      aria-label="Toggle color theme"
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        color: "var(--text)",
        borderRadius: "4px",
        padding: "8px 14px",
        fontFamily: "var(--font-mono)",
        fontSize: "12px",
        letterSpacing: "0.05em",
        textTransform: "uppercase",
        cursor: "pointer",
      }}
    >
      {theme === "light" ? "Dark mode" : "Light mode"}
    </button>
  );
}
