import { useEffect, useState } from "react";
import { getOffenseTypes } from "../api/client";

/**
 * Populated from GET /crimes/offense-types rather than a hardcoded list,
 * so the options never drift out of sync with what's actually in the
 * database. Reports the selected offense up to App.jsx, same pattern
 * as TimeRangeFilter -- this component doesn't fetch pins itself.
 */
export default function OffenseFilter({ value, onChange }) {
  const [options, setOptions] = useState([]);

  useEffect(() => {
    getOffenseTypes()
      .then(setOptions)
      .catch(() => setOptions([]));
  }, []);

  return (
    <select
      value={value || ""}
      onChange={(e) => onChange(e.target.value || null)}
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        color: "var(--text)",
        borderRadius: "4px",
        padding: "8px 12px",
        fontFamily: "var(--font-mono)",
        fontSize: "12px",
        letterSpacing: "0.05em",
        textTransform: "uppercase",
        cursor: "pointer",
        maxWidth: "220px",
      }}
    >
      <option value="">All crime types</option>
      {options.map((opt) => (
        <option key={opt.ofns_desc} value={opt.ofns_desc}>
          {opt.ofns_desc} ({opt.crime_count})
        </option>
      ))}
    </select>
  );
}
