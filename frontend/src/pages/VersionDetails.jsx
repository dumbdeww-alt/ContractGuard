import React from "react";

function VersionDetails() {
  return (
    <div style={{ padding: "30px" }}>
      <h1>Student Contract</h1>

      <p>
        <strong>Version:</strong> v3
      </p>

      <p>
        <strong>Owner:</strong> Jainam
      </p>

      <p>
        <strong>Status:</strong> Active
      </p>

      <hr />

      <h2>Schema</h2>

      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          marginTop: "20px",
        }}
      >
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "10px" }}>
              Field
            </th>
            <th style={{ textAlign: "left", padding: "10px" }}>
              Data Type
            </th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <td style={{ padding: "10px" }}>student_id</td>
            <td style={{ padding: "10px" }}>string</td>
          </tr>

          <tr>
            <td style={{ padding: "10px" }}>name</td>
            <td style={{ padding: "10px" }}>string</td>
          </tr>

          <tr>
            <td style={{ padding: "10px" }}>email</td>
            <td style={{ padding: "10px" }}>string</td>
          </tr>

          <tr>
            <td style={{ padding: "10px" }}>course</td>
            <td style={{ padding: "10px" }}>string</td>
          </tr>

          <tr>
            <td style={{ padding: "10px" }}>semester</td>
            <td style={{ padding: "10px" }}>integer</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default VersionDetails;