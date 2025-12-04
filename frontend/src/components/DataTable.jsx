import React from "react";

function DataTable({ rows }) {
  if (!rows || rows.length === 0) return null;

  const headers = Object.keys(rows[0]);

  return (
    <div className="table-responsive mt-4">
      <h5>Filtered Data</h5>
      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            {headers.map((h, idx) => (
              <th key={idx}>{h.toUpperCase()}</th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, rIndex) => (
            <tr key={rIndex}>
              {headers.map((h, cIndex) => (
                <td key={cIndex}>{row[h]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
