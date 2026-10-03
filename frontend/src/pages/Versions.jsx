
import { useNavigate } from "react-router-dom";

function Versions() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Contract Versions</h1>
      <p>View schema versions and their compatibility status.</p>

      <div className="panel">
        <h2>Student Contract</h2>

        <div style={styles.versionCard}>
          <h3>Version 1</h3>
          <p>Initial student contract schema.</p>
          <span style={styles.compatible}>Compatible</span>
        </div>

        <div style={styles.versionCard}>
          <h3>Version 2</h3>
          <p>Added attendance field.</p>
          <span style={styles.compatible}>Compatible</span>
        </div>

        <div style={styles.versionCard}>
          <h3>Version 3</h3>
          <p>Added email and updated student information.</p>
          <span style={styles.compatible}>Compatible</span>
        </div>

        <div style={styles.versionCard}>
          <h3>Version 4</h3>
          <p>Changed attendance field type.</p>
          <span style={styles.breaking}>Breaking Change</span>
        </div>

        <div style={{ marginTop: "20px" }}>
          <button
            onClick={() => navigate("/impact")}
            style={styles.impactButton}
          >
            View Impact
          </button>

          <button
            onClick={() => navigate("/alerts")}
            style={styles.alertButton}
          >
            View Alerts
          </button>

          <button
            onClick={() => navigate("/approval")}
            style={styles.approvalButton}
          >
            Review Approval
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  versionCard: {
    padding: "15px",
    marginTop: "12px",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    background: "#f9fafb",
  },

  compatible: {
    display: "inline-block",
    padding: "5px 10px",
    borderRadius: "5px",
    background: "#dcfce7",
    color: "#166534",
    fontWeight: "bold",
  },

  breaking: {
    display: "inline-block",
    padding: "5px 10px",
    borderRadius: "5px",
    background: "#fee2e2",
    color: "#b91c1c",
    fontWeight: "bold",
  },

  impactButton: {
    padding: "9px 14px",
    marginRight: "8px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#e0e7ff",
    color: "#3730a3",
    fontWeight: "bold",
  },

  alertButton: {
    padding: "9px 14px",
    marginRight: "8px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#fee2e2",
    color: "#b91c1c",
    fontWeight: "bold",
  },

  approvalButton: {
    padding: "9px 14px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#fef3c7",
    color: "#92400e",
    fontWeight: "bold",
  },
};

export default Versions;