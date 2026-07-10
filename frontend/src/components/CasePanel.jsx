import { useEffect, useState } from "react";
import { getCrimeDetail } from "../api/client";

/**
 * Fetches full case detail (a separate, heavier call from the pin list)
 * only when a specific case is selected. Slides in from the right;
 * MapView handles shrinking the map to make room, so this panel just
 * needs to render its own content correctly.
 */
export default function CasePanel({ cmplntNum, onClose }) {
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!cmplntNum) return;
    setDetail(null);
    setError(null);
    getCrimeDetail(cmplntNum)
      .then(setDetail)
      .catch(() => setError("Could not load this case. Try again."));
  }, [cmplntNum]);

  return (
    <div
      style={{
        width: "var(--panel-width)",
        height: "100%",
        background: "var(--surface)",
        borderLeft: "1px solid var(--border)",
        overflowY: "auto",
        padding: "24px",
        flexShrink: 0,
      }}
    >
      <button
        onClick={onClose}
        style={{
          background: "none",
          border: "none",
          color: "var(--text-muted)",
          fontFamily: "var(--font-mono)",
          fontSize: "12px",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          cursor: "pointer",
          padding: 0,
          marginBottom: "20px",
        }}
      >
        &larr; Close case
      </button>

      {error && <p style={{ color: "var(--text-muted)" }}>{error}</p>}

      {!error && !detail && (
        <p style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: "13px" }}>
          Loading case file&hellip;
        </p>
      )}

      {detail && (
        <>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              color: "var(--text-muted)",
              letterSpacing: "0.05em",
              marginBottom: "4px",
            }}
          >
            CASE No. {detail.cmplnt_num}
          </div>

          <h2
            style={{
              fontFamily: "var(--font-display)",
              fontWeight: 600,
              fontSize: "28px",
              margin: "0 0 16px",
              lineHeight: 1.1,
            }}
          >
            {detail.ofns_desc}
          </h2>

          <div
            style={{
              display: "inline-block",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              background: "var(--surface-alt)",
              color: "var(--text)",
              padding: "3px 8px",
              borderRadius: "3px",
              marginBottom: "20px",
            }}
          >
            {detail.law_cat_cd}
          </div>

          <Field label="Summary">
            {detail.ai_summary || "Summary not yet generated for this case."}
          </Field>

          <Field label="Specific offense">{detail.pd_desc}</Field>
          <Field label="Location type">{detail.prem_typ_desc}</Field>
          <Field label="Borough">{detail.boro_nm}</Field>
          <Field label="Date reported" mono>
            {detail.rpt_dt}
          </Field>
          <Field label="Date occurred" mono>
            {detail.cmplnt_fr_dt} {detail.cmplnt_fr_tm}
          </Field>
          <Field label="Coordinates" mono>
            {detail.latitude.toFixed(4)}, {detail.longitude.toFixed(4)}
          </Field>
        </>
      )}
    </div>
  );
}

function Field({ label, mono, children }) {
  return (
    <div style={{ marginBottom: "18px" }}>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "11px",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "var(--text-muted)",
          marginBottom: "4px",
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: mono ? "var(--font-mono)" : "var(--font-body)",
          fontSize: mono ? "13px" : "15px",
          color: "var(--text)",
          lineHeight: 1.5,
        }}
      >
        {children}
      </div>
    </div>
  );
}
