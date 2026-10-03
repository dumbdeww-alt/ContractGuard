import { useEffect, useState } from "react";
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  MarkerType,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

export default function Lineage() {
  const [contracts, setContracts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/contracts")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to load contracts");
        }
        return res.json();
      })
      .then((data) => {
        setContracts(data);
        setSelected(data[0] || null);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to connect to the ContractGuard backend.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "30px" }}>
        <h2>Loading lineage...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "30px" }}>
        <h2>Contract Lineage</h2>
        <p style={{ color: "#dc2626" }}>{error}</p>
      </div>
    );
  }

  if (!selected) {
    return (
      <div style={{ padding: "30px" }}>
        <h2>No contracts found</h2>
      </div>
    );
  }

  const nodes = [
    {
      id: "producer",
      position: { x: 20, y: 210 },

      style: {
        width: "230px",
        minWidth: "230px",
        padding: "0",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        boxShadow: "0 4px 14px rgba(15, 23, 42, 0.08)",
      },

      data: {
        label: (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "15px",
              width: "100%",
              boxSizing: "border-box",
            }}
          >
            <div
              style={{
                width: "38px",
                height: "38px",
                minWidth: "38px",
                borderRadius: "9px",
                background: "#f1f5f9",
                color: "#475569",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: "700",
              }}
            >
              P
            </div>

            <div style={{ minWidth: 0 }}>
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: "800",
                  letterSpacing: "1px",
                  color: "#94a3b8",
                  marginBottom: "4px",
                }}
              >
                PRODUCER
              </div>

              <strong
                style={{
                  display: "block",
                  fontSize: "13px",
                  color: "#1f2937",
                }}
              >
                Producer #{selected.producer_id}
              </strong>
            </div>
          </div>
        ),
      },
    },

    {
      id: "contract",
      position: { x: 330, y: 200 },

      style: {
        width: "300px",
        minWidth: "300px",
        padding: "0",
        borderRadius: "12px",
        border: "2px solid #2563eb",
        background: "#ffffff",
        boxShadow: "0 5px 18px rgba(37, 99, 235, 0.12)",
      },

      data: {
        label: (
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "12px",
              padding: "16px",
              width: "100%",
              boxSizing: "border-box",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                minWidth: "40px",
                borderRadius: "9px",
                background: "#eff6ff",
                color: "#2563eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: "700",
              }}
            >
              ◆
            </div>

            <div
              style={{
                minWidth: 0,
                flex: 1,
              }}
            >
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: "800",
                  letterSpacing: "1px",
                  color: "#2563eb",
                  marginBottom: "5px",
                }}
              >
                DATA CONTRACT
              </div>

              <strong
                style={{
                  display: "block",
                  width: "100%",
                  whiteSpace: "normal",
                  overflowWrap: "anywhere",
                  wordBreak: "break-word",
                  lineHeight: "1.35",
                  fontSize: "14px",
                  color: "#111827",
                }}
              >
                {selected.name}
              </strong>

              <div
                style={{
                  marginTop: "5px",
                  fontSize: "10px",
                  color: "#94a3b8",
                }}
              >
                Contract #{selected.id}
              </div>
            </div>
          </div>
        ),
      },
    },

    {
      id: "portal",
      position: { x: 750, y: 120 },

      style: {
        width: "230px",
        minWidth: "230px",
        padding: "0",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        boxShadow: "0 4px 14px rgba(15, 23, 42, 0.08)",
      },

      data: {
        label: (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "15px",
            }}
          >
            <div
              style={{
                width: "38px",
                height: "38px",
                minWidth: "38px",
                borderRadius: "9px",
                background: "#ecfdf5",
                color: "#059669",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: "700",
              }}
            >
              ↗
            </div>

            <div>
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: "800",
                  letterSpacing: "1px",
                  color: "#94a3b8",
                  marginBottom: "4px",
                }}
              >
                CONSUMER
              </div>

              <strong
                style={{
                  fontSize: "13px",
                  color: "#1f2937",
                }}
              >
                Student Portal
              </strong>
            </div>
          </div>
        ),
      },
    },

    {
      id: "analytics",
      position: { x: 750, y: 300 },

      style: {
        width: "230px",
        minWidth: "230px",
        padding: "0",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        background: "#ffffff",
        boxShadow: "0 4px 14px rgba(15, 23, 42, 0.08)",
      },

      data: {
        label: (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "15px",
            }}
          >
            <div
              style={{
                width: "38px",
                height: "38px",
                minWidth: "38px",
                borderRadius: "9px",
                background: "#ecfdf5",
                color: "#059669",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: "700",
              }}
            >
              ↗
            </div>

            <div>
              <div
                style={{
                  fontSize: "9px",
                  fontWeight: "800",
                  letterSpacing: "1px",
                  color: "#94a3b8",
                  marginBottom: "4px",
                }}
              >
                CONSUMER
              </div>

              <strong
                style={{
                  fontSize: "13px",
                  color: "#1f2937",
                }}
              >
                Analytics Service
              </strong>
            </div>
          </div>
        ),
      },
    },
  ];

  const edges = [
    {
      id: "producer-contract",
      source: "producer",
      target: "contract",
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },

    {
      id: "contract-portal",
      source: "contract",
      target: "portal",
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },

    {
      id: "contract-analytics",
      source: "contract",
      target: "analytics",
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
    },
  ];

  return (
    <div
      style={{
        padding: "30px",
        maxWidth: "1400px",
        margin: "0 auto",
        boxSizing: "border-box",
      }}
    >
      {/* HEADER */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "24px",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "11px",
              fontWeight: "700",
              letterSpacing: "1.5px",
              color: "#64748b",
              marginBottom: "6px",
            }}
          >
            CONTRACTGUARD
          </div>

          <h1
            style={{
              margin: "0 0 8px",
              fontSize: "30px",
              color: "#111827",
            }}
          >
            Contract Lineage
            <span style={{ color: "#2563eb" }}>.</span>
          </h1>

          <p
            style={{
              margin: 0,
              color: "#64748b",
              fontSize: "14px",
            }}
          >
            Visualize how contract data flows through your system.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "9px 14px",
            border: "1px solid #e5e7eb",
            borderRadius: "20px",
            background: "#fff",
            fontSize: "12px",
            fontWeight: "600",
          }}
        >
          <span
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: "#22c55e",
            }}
          />

          Backend Connected
        </div>
      </div>

      {/* CONTRACT SELECTOR */}

      <div
        style={{
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          padding: "18px 20px",
          marginBottom: "18px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "10px",
              fontWeight: "800",
              letterSpacing: "1px",
              color: "#94a3b8",
              marginBottom: "6px",
            }}
          >
            SELECT CONTRACT
          </div>

          <select
            value={selected.id}
            onChange={(e) => {
              const contract = contracts.find(
                (item) => item.id === Number(e.target.value)
              );

              setSelected(contract);
            }}
            style={{
              minWidth: "300px",
              padding: "9px 12px",
              border: "1px solid #d1d5db",
              borderRadius: "7px",
              background: "#fff",
              fontSize: "14px",
              fontWeight: "600",
              color: "#111827",
              cursor: "pointer",
            }}
          >
            {contracts.map((contract) => (
              <option key={contract.id} value={contract.id}>
                {contract.name}
              </option>
            ))}
          </select>
        </div>

        <div
          style={{
            display: "flex",
            gap: "30px",
          }}
        >
          <Stat value="1" label="PRODUCER" />
          <Stat value="1" label="CONTRACT" />
          <Stat value="2" label="CONSUMERS" />
        </div>
      </div>

      {/* DATA FLOW */}

      <div
        style={{
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "18px 20px",
            borderBottom: "1px solid #eef2f7",
          }}
        >
          <h2
            style={{
              margin: 0,
              fontSize: "17px",
              color: "#111827",
            }}
          >
            Data Flow
          </h2>

          <p
            style={{
              margin: "4px 0 0",
              fontSize: "12px",
              color: "#94a3b8",
            }}
          >
            Producer → Contract → Downstream consumers
          </p>
        </div>

        <div
          style={{
            width: "100%",
            height: "520px",
            background: "#fafbfc",
          }}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            nodesConnectable={false}
            nodesDraggable={true}
            elementsSelectable={true}
            proOptions={{ hideAttribution: true }}
          >
            <MiniMap />
            <Controls />
            <Background gap={24} size={1} />
          </ReactFlow>
        </div>
      </div>

      {/* DETAILS */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "14px",
          marginTop: "18px",
        }}
      >
        <Info
          title="SELECTED CONTRACT"
          value={selected.name}
        />

        <Info
          title="PRODUCER"
          value={`Producer #${selected.producer_id}`}
        />

        <Info
          title="DOWNSTREAM"
          value="2 Consumers"
        />
      </div>
    </div>
  );
}

function Stat({ value, label }) {
  return (
    <div style={{ textAlign: "center" }}>
      <strong
        style={{
          display: "block",
          fontSize: "19px",
          color: "#111827",
        }}
      >
        {value}
      </strong>

      <span
        style={{
          display: "block",
          marginTop: "2px",
          fontSize: "9px",
          fontWeight: "800",
          letterSpacing: "1px",
          color: "#94a3b8",
        }}
      >
        {label}
      </span>
    </div>
  );
}

function Info({ title, value }) {
  return (
    <div
      style={{
        padding: "16px 18px",
        background: "#fff",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
      }}
    >
      <div
        style={{
          fontSize: "9px",
          fontWeight: "800",
          letterSpacing: "1px",
          color: "#94a3b8",
          marginBottom: "6px",
        }}
      >
        {title}
      </div>

      <strong
        style={{
          fontSize: "13px",
          color: "#1f2937",
          wordBreak: "break-word",
        }}
      >
        {value}
      </strong>
    </div>
  );
}