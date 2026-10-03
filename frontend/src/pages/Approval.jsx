import { useState } from "react";

function Approval() {
  const [status, setStatus] = useState("Pending Approval");

  return (
    <div>
      <h1>Approval Workflow</h1>
      <p>Review and approve new contract versions before deployment.</p>

      <div className="panel">
        <h2>Student Contract v4</h2>

        <p><strong>Owner:</strong> Jainam</p>
        <p><strong>Previous Version:</strong> v3</p>
        <p><strong>New Version:</strong> v4</p>
        <p>
          <strong>Compatibility:</strong>{" "}
          <span style={{ color: "#15803d" }}>Compatible</span>
        </p>

        <p>
          <strong>Semantic Validation:</strong>{" "}
          <span style={{ color: "#15803d" }}>Passed</span>
        </p>

        <p>
          <strong>Impact:</strong> 3 downstream dependencies
        </p>

        <div
          style={{
            padding: "12px",
            marginTop: "15px",
            background: "#fff7ed",
            borderRadius: "6px",
          }}
        >
          <strong>Current Status:</strong> {status}
        </div>

        <div style={{ marginTop: "20px" }}>
          <button
            onClick={() => setStatus("Approved")}
            style={styles.approve}
          >
            Approve
          </button>

          <button
            onClick={() => setStatus("Rejected")}
            style={styles.reject}
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  approve: {
    padding: "10px 18px",
    marginRight: "10px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#dcfce7",
    color: "#166534",
    fontWeight: "bold",
  },

  reject: {
    padding: "10px 18px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#fee2e2",
    color: "#b91c1c",
    fontWeight: "bold",
  },
};

export default Approval;
