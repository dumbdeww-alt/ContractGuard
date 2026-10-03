
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Contracts() {
  const navigate = useNavigate();

  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/contracts")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load contracts");
        }
        return response.json();
      })
      .then((data) => {
        setContracts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to connect to the ContractGuard backend.");
        setLoading(false);
      });
  }, []);

  const getIcon = (name) => {
    if (name.toLowerCase().includes("schedule")) return "🚆";
    if (name.toLowerCase().includes("running")) return "📡";
    return "📄";
  };

  const filteredContracts = contracts.filter((contract) =>
    contract.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="contracts-page">

      {/* Header */}
      <div className="contracts-header">
        <div>
          <div className="page-label">DATA CONTRACT REGISTRY</div>

          <h1>
            Contracts
            <span className="title-dot">.</span>
          </h1>

          <p>
            Manage, monitor and analyze your registered data contracts.
          </p>
        </div>

        <button className="new-contract-btn">
          + New Contract
        </button>
      </div>

      {/* Stats */}
      <div className="contract-stats">

        <div className="stat-card">
          <div className="stat-icon">◈</div>
          <div>
            <span>Total Contracts</span>
            <strong>{contracts.length}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✓</div>
          <div>
            <span>Active</span>
            <strong>{contracts.length}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⌁</div>
          <div>
            <span>Versions</span>
            <strong>3</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚠</div>
          <div>
            <span>Alerts</span>
            <strong>0</strong>
          </div>
        </div>

      </div>

      {/* Contract list */}
      <div className="contracts-section">

        <div className="section-top">
          <div>
            <h2>Registered Contracts</h2>
            <p>Latest versions and contract health</p>
          </div>

          <div className="search-box">
            🔍
            <input
              type="text"
              placeholder="Search contracts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ padding: "30px" }}>
            Loading contracts...
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ padding: "30px", color: "red" }}>
            {error}
          </div>
        )}

        {/* Contract cards */}
        {!loading && !error && (
          <div className="contract-grid">

            {filteredContracts.map((contract) => (

              <div
                className="contract-card"
                key={contract.id}
              >

                {/* Card top */}
                <div className="card-top">

                  <div className="contract-icon">
                    {getIcon(contract.name)}
                  </div>

                  <div className="contract-title">
                    <h3>{contract.name}</h3>
                    <span>Data Contract</span>
                  </div>

                  <div className="status active">
                    <span className="status-dot"></span>
                    Active
                  </div>

                </div>

                {/* Version */}
                <div className="version-box">

                  <div>
                    <span className="field-label">
                      LATEST VERSION
                    </span>

                    <button
                      className="version-button"
                      onClick={() =>
                        alert(
                          `${contract.name} — Contract ID ${contract.id}`
                        )
                      }
                    >
                      View
                      <span>↗</span>
                    </button>
                  </div>

                  <div className="updated">
                    <span className="field-label">
                      LAST UPDATED
                    </span>

                    <strong>
                      {new Date(contract.updated_at).toLocaleDateString()}
                    </strong>
                  </div>

                </div>

                {/* Owner / Producer */}
                <div className="owner-row">

                  <div className="avatar">
                    P
                  </div>

                  <div>
                    <span className="field-label">
                      PRODUCER ID
                    </span>

                    <strong>
                      Producer #{contract.producer_id}
                    </strong>
                  </div>

                </div>

                {/* Actions */}
                <div className="contract-actions">

                  <button
                    className="action-btn impact"
                    aria-label="Impact"
                    onClick={() => navigate("/impact")}
                  >
                    <span>◉</span>
                    Impact
                  </button>

                  <button
                    className="action-btn alert"
                    aria-label="Alerts"
                    onClick={() => navigate("/alerts")}
                  >
                    <span>⚠</span>
                    Alerts
                  </button>

                  <button
                    className="action-btn review"
                    aria-label="Review"
                    onClick={() => navigate("/approval")}
                  >
                    <span>✓</span>
                    Review
                  </button>

                  <button
                    className="action-btn validate"
                    aria-label="Validate"
                    onClick={() => navigate("/validation")}
                  >
                    <span>⌁</span>
                    Validate
                  </button>

                </div>

              </div>

            ))}

          </div>
        )}

        {!loading && !error && filteredContracts.length === 0 && (
          <div style={{ padding: "30px" }}>
            No contracts found.
          </div>
        )}

      </div>

    </div>
  );
}

export default Contracts;

