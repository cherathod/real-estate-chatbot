import React from "react";

function DataTable({ rows }) {
  // If there is no data, don't show anything
  if (!rows || rows.length === 0) return null;

  // Get table column names from the first row's keys
  const headers = Object.keys(rows[0]);

  return (
    <div className="table-responsive mt-4">
      <h5>Filtered Data</h5>

      <table className="table table-bordered table-hover">
        <thead className="table-light">
          <tr>
            {/* Create a header column for each key */}
            {headers.map((h, idx) => (
              <th key={idx}>{h.toUpperCase()}</th> // Show the header in uppercase
            ))}
          </tr>
        </thead>

        <tbody>
          {/* Loop through each row of data */}
          {rows.map((row, rIndex) => (
            <tr key={rIndex}>
              {/* Loop through each column for this row */}
              {headers.map((h, cIndex) => (
                <td key={cIndex}>{row[h]}</td> // Show the value for each column
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
