import React from "react";

export default function Alerts() {
  const alerts = [
    {
      title: "Student Contract v4 has a breaking change",
      contract: "Student Contract",
      version: "v3 → v4",
      severity: "Critical",
      affected: "Student API",
    },
    {
      title: "Student Portal may be affected",
      contract: "Student Contract",
      version: "v3 → v4",
      severity: "High",
      affected: "Student Portal",
    },
    {
      title: "Analytics Service requires review",
      contract: "Student Contract",
      version: "v3 → v4",
      severity: "Medium",
      affected: "Analytics Service",
    },
  ];

  return (
    <div style={styles.page}>
      <h1>Breaking Change Alerts</h1>

      <p style={styles.subtitle}>
        Monitor schema changes that may break downstream consumers.
      </p>

      <div style={styles.summary}>
        <div style={styles.card}>
          <h3>Total Alerts</h3>
          <strong style={styles.number}>3</strong>
        </div>

        <div style={styles.card}>
          <h3>Critical</h3>
          <strong style={{ ...styles.number, color: "#dc2626" }}>
            1
          </strong>
        </div>

        <div style={styles.card}>
          <h3>Needs Review</h3>
          <strong style={{ ...styles.number, color: "#ea580c" }}>
            2
          </strong>
        </div>
      </div>

      <h2>Active Alerts</h2>

      {alerts.map((alert, index) => (
        <div key={index} style={styles.alert}>
          <div>
            <h3>⚠ {alert.title}</h3>

            <p>
              <strong>Contract:</strong> {alert.contract}
            </p>

            <p>
              <strong>Version:</strong> {alert.version}
            </p>

            <p>
              <strong>Affected System:</strong> {alert.affected}
            </p>
          </div>

          <span
            style={{
              ...styles.badge,
              background:
                alert.severity === "Critical"
                  ? "#fee2e2"
                  : alert.severity === "High"
                  ? "#ffedd5"
                  : "#fef3c7",
              color:
                alert.severity === "Critical"
                  ? "#b91c1c"
                  : alert.severity === "High"
                  ? "#c2410c"
                  : "#92400e",
            }}
          >
            {alert.severity}
          </span>
        </div>
      ))}
    </div>
  );
}

const styles = {
  page: {
    padding: "30px",
    fontFamily: "Arial, sans-serif",
  },

  subtitle: {
    color: "#666",
    marginBottom: "25px",
  },

  summary: {
    display: "flex",
    gap: "20px",
    marginBottom: "35px",
  },

  card: {
    flex: 1,
    padding: "20px",
    border: "1px solid #ddd",
    borderRadius: "10px",
    background: "#fff",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  },

  number: {
    fontSize: "28px",
    marginTop: "10px",
    display: "block",
  },

  alert: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "20px",
    marginTop: "15px",
    border: "1px solid #ddd",
    borderRadius: "10px",
    background: "#fff",
  },

  badge: {
    padding: "8px 15px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "13px",
  },
};