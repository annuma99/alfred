import { useEffect, useState } from "react";
import MapView from "./components/MapView";
import CasePanel from "./components/CasePanel";
import TimeRangeFilter from "./components/TimeRangeFilter";
import ThemeToggle from "./components/ThemeToggle";

export default function App() {
  const [theme, setTheme] = useState("light");
  const [selectedBorough, setSelectedBorough] = useState(null);
  const [timeRange, setTimeRange] = useState("week");
  const [selectedCrime, setSelectedCrime] = useState(null);

  // Applies the theme to the document root so theme.css's [data-theme]
  // selector can flip every CSS variable in one place.
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const panelOpen = Boolean(selectedCrime);

  return (
    <div style={{ height: "100vh", width: "100vw", display: "flex", flexDirection: "column" }}>
      {/* Header bar: floats above the map, holds global controls */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "14px 24px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontWeight: 700,
              fontSize: "26px",
              letterSpacing: "0.02em",
              margin: 0,
            }}
          >
            ALFRED
          </h1>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            NYC crime dashboard
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <TimeRangeFilter value={timeRange} onChange={setTimeRange} />
          <ThemeToggle theme={theme} onToggle={() => setTheme(theme === "light" ? "dark" : "light")} />
        </div>
      </header>

      {/* Body: map + slide-in panel, side by side */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <div
          style={{
            flex: 1,
            minWidth: 0,
            transition: "flex-basis var(--transition)",
          }}
        >
          <MapView
            theme={theme}
            selectedBorough={selectedBorough}
            onSelectBorough={setSelectedBorough}
            timeRange={timeRange}
            onSelectCrime={setSelectedCrime}
          />
        </div>

        {/* Panel slides in via width transition -- 0 when closed, full
            width when a case is selected. Kept mounted (width: 0) rather
            than conditionally rendered, so the slide actually animates
            instead of popping in. */}
        <div
          style={{
            width: panelOpen ? "var(--panel-width)" : "0px",
            transition: "width var(--transition)",
            overflow: "hidden",
            flexShrink: 0,
          }}
        >
          {panelOpen && (
            <CasePanel cmplntNum={selectedCrime} onClose={() => setSelectedCrime(null)} />
          )}
        </div>
      </div>
    </div>
  );
}
