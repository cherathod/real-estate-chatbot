import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

function TrendChart({ data }) {
  return (
    <div className="card shadow-sm p-3">
      <h5 className="mb-3">Trend Chart</h5>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="blue" />
          <Line type="monotone" dataKey="demand" stroke="green" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrendChart;
