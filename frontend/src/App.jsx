import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import "./App.css";

import Contracts from "./pages/Contracts";
import Versions from "./pages/Versions";
import VersionDetails from "./pages/VersionDetails";
import Lineage from "./pages/Lineage";
import Impact from "./pages/Impact";
import Alerts from "./pages/Alerts";
import Approval from "./pages/Approval";
import Validation from "./pages/Validation";

function Dashboard() {
return ( <div className="dashboard-page"> <div className="page-header"> <div> <div className="page-label">CONTRACTGUARD</div> <h1>Dashboard<span className="title-dot">.</span></h1> <p>Monitor your data contracts and schema health.</p> </div> </div>

```
  <div className="stats">
    <div className="stat-card">
      <div className="stat-icon">📁</div>
      <div>
        <p>Total Contracts</p>
        <h2>12</h2>
        <span className="positive">↑ 8.2% this month</span>
      </div>
    </div>

    <div className="stat-card">
      <div className="stat-icon">🔄</div>
      <div>
        <p>Active Versions</p>
        <h2>28</h2>
        <span className="positive">↑ 4 new versions</span>
      </div>
    </div>

    <div className="stat-card warning">
      <div className="stat-icon">⚠️</div>
      <div>
        <p>Breaking Changes</p>
        <h2>3</h2>
        <span className="negative">Needs attention</span>
      </div>
    </div>

    <div className="stat-card">
      <div className="stat-icon">✅</div>
      <div>
        <p>Healthy Contracts</p>
        <h2>9</h2>
        <span className="positive">75% healthy</span>
      </div>
    </div>
  </div>
</div>


);
}

function App() {
return ( <BrowserRouter> <div className="app">

```
    <aside className="sidebar">
      <div className="logo">🛡️ ContractGuard</div>

      <nav>
        <Link className="nav-item" to="/">
          📊 Dashboard
        </Link>

        <Link className="nav-item" to="/contracts">
          📁 Contracts
        </Link>

        <Link className="nav-item" to="/versions">
          🕐 Versions
        </Link>

        <Link className="nav-item" to="/lineage">
          🔗 Lineage
        </Link>

        <Link className="nav-item" to="/validation">
          🧪 Validation
        </Link>

        <Link className="nav-item" to="/alerts">
          ⚠️ Breaking Changes
        </Link>

        <Link className="nav-item" to="/approval">
          ✅ Approvals
        </Link>
      </nav>

      <div className="user">
        <div className="avatar">D</div>

        <div>
          <strong>Divyesh</strong>
          <small>Quality Engineer</small>
        </div>
      </div>
    </aside>

    <main className="main">
      <Routes>
        <Route path="/" element={<Dashboard />} />

        <Route path="/contracts" element={<Contracts />} />

        <Route path="/versions" element={<Versions />} />

        <Route
          path="/version/:versionId"
          element={<VersionDetails />}
        />

        <Route path="/lineage" element={<Lineage />} />

        <Route path="/impact" element={<Impact />} />

        <Route path="/alerts" element={<Alerts />} />

        <Route path="/approval" element={<Approval />} />

        <Route path="/validation" element={<Validation />} />
      </Routes>
    </main>

  </div>
</BrowserRouter>


);
}

export default App;
