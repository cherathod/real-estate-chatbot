import React, { useState } from "react";
import api from "./services/api";

import ChatInput from "./components/ChatInput";
import ResponseCard from "./components/ResponseCard";
import TrendChart from "./components/TrendChart";
import DataTable from "./components/DataTable";

function App() {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);

  const handleQuery = async (query) => {
    try {
      setLoading(true);

      const response = await api.post("/analyze/", { query });

      setSummary(response.data.summary);
      setChartData(response.data.chartData);
      setTableData(response.data.tableData);
    } catch (error) {
      alert("Error fetching analysis. Check backend!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">

      <h2 className="text-center mb-4">🏡 Real Estate Analysis Chatbot</h2>

      {/* Chat input */}
      <ChatInput onSend={handleQuery} />

      {/* Loading indicator */}
      {loading && <p className="text-center mt-4">Processing your request...</p>}

      {/* Summary */}
      {summary && <ResponseCard text={summary} />}

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="mt-4">
          <TrendChart data={chartData} />
        </div>
      )}

      {/* Table */}
      {tableData.length > 0 && (
        <div className="mt-5">
          <DataTable rows={tableData} />
        </div>
      )}

    </div>
  );
}

export default App;
