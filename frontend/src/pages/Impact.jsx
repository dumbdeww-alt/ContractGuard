import React from "react";

export default function Impact() {
  const impacts = [
    {
      name: "Student API",
      type: "Direct Dependency",
      status: "Breaking",
      description: "Consumes Student Contract fields directly.",
    },
    {
      name: "Student Portal",
      type: "Downstream Consumer",
      status: "High Impact",
      description: "Uses Student API and may fail if contract fields change.",
    },
    {
      name: "Analytics Service",
      type: "Downstream Consumer",
      status: "Medium Impact",
      description: "Uses student data for analytics and reporting.",
    },
  ];

  return (
    <div style={styles.page}>
      <h1>Impact Analysis</h1>

      <p style={styles.subtitle}>
        Analyze systems affected by changes to the Student Contract.
      </p>

      <div style={styles.summary}>
        <div style={styles.card}>
          <h3>Contract</h3>
          <p>Student Contract</p>
          <strong>v3 → v4</strong>
        </div>

        <div style={styles.card}>
          <h3>Total Dependencies</h3>
          <p style={styles.number}>3</p>
        </div>

        <div style={styles.card}>
          <h3>Breaking Changes</h3>
          <p style={{ ...styles.number, color: "#dc2626" }}>1</p>
        </div>
      </div>

      <div style={styles.section}>
        <h2>Affected Systems</h2>

        {impacts.map((impact, index) => (
          <div key={index} style={styles.impactCard}>
            <div>
              <h3>{impact.name}</h3>
              <p>{impact.description}</p>
              <small>{impact.type}</small>
            </div>

            <span
              style={{
                ...styles.status,
                background:
                  impact.status === "Breaking"
                    ? "#fee2e2"
                    : impact.status === "High Impact"
                    ? "#ffedd5"
                    : "#fef3c7",
                color:
                  impact.status === "Breaking"
                    ? "#b91c1c"
                    : impact.status === "High Impact"
                    ? "#c2410c"
                    : "#92400e",
              }}
            >
              {impact.status}
            </span>
          </div>
        ))}
      </div>

      <div style={styles.section}>
        <h2>Impact Summary</h2>

        <div style={styles.warning}>
          <strong>⚠ Breaking Change Detected</strong>
          <p>
            A change in Student Contract v4 may affect the Student API and its
            downstream consumers.
          </p>
        </div>
      </div>
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
    marginBottom: "30px",
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
    fontWeight: "bold",
    margin: "5px 0",
  },

  section: {
    marginTop: "25px",
  },

  impactCard: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "18px",
    marginTop: "12px",
    border: "1px solid #ddd",
    borderRadius: "10px",
    background: "#fff",
  },

  status: {
    padding: "8px 14px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "13px",
  },

  warning: {
    padding: "20px",
    marginTop: "15px",
    borderRadius: "10px",
    background: "#fff7ed",
    border: "1px solid #fed7aa",
  },
};