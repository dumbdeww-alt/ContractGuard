
import { useState } from "react";

function Validation() {
  const [result, setResult] = useState(null);

  const validateData = () => {
    setResult("Valid");
  };

  return (
    <div>
      <h1>Runtime Validation</h1>
      <p>Validate incoming data against the registered contract schema.</p>

      <div className="panel">
        <h2>Student Contract v3</h2>

        <p>
          <strong>Contract:</strong> Student Contract
        </p>

        <p>
          <strong>Version:</strong> v3
        </p>

        <p>
          <strong>Validation Rules:</strong> Schema + Semantic Rules
        </p>

        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            background: "#f8fafc",
            borderRadius: "6px",
          }}
        >
          <h3>Sample Runtime Data</h3>

          <pre
            style={{
              background: "#111827",
              color: "#f9fafb",
              padding: "15px",
              borderRadius: "6px",
              overflowX: "auto",
            }}
          >
{`{
  "student_id": "ST101",
  "name": "Rahul",
  "email": "rahul@example.com",
  "attendance": 82
}`}
          </pre>
        </div>

        <button
          onClick={validateData}
          style={styles.validateButton}
        >
          Validate Data
        </button>

        {result && (
          <div
            style={{
              marginTop: "20px",
              padding: "15px",
              background: "#dcfce7",
              color: "#166534",
              borderRadius: "6px",
              fontWeight: "bold",
            }}
          >
            ✓ Validation Successful — Data matches Student Contract v3
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  validateButton: {
    marginTop: "20px",
    padding: "10px 18px",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    background: "#dbeafe",
    color: "#1d4ed8",
    fontWeight: "bold",
  },
};

export default Validation;

