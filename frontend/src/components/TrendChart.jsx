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
    // A card container for the chart
    <div className="card shadow-sm p-3">
      <h5 className="mb-3">Trend Chart</h5>

      {/* ResponsiveContainer makes the chart resize automatically */}
      <ResponsiveContainer width="100%" height={300}>
        {/* LineChart displays the graph using the provided data */}
        <LineChart data={data}>
          
          {/* Light grid lines behind the chart */}
          <CartesianGrid strokeDasharray="3 3" />
          
          {/* X-axis uses the "year" field from the data */}
          <XAxis dataKey="year" />
          
          {/* Y-axis adjusts automatically based on numbers */}
          <YAxis />
          
          {/* Tooltip shows values on hover */}
          <Tooltip />

          {/* Line showing price trend over years */}
          <Line type="monotone" dataKey="price" stroke="blue" />

          {/* Line showing demand trend over years */}
          <Line type="monotone" dataKey="demand" stroke="green" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrendChart;
