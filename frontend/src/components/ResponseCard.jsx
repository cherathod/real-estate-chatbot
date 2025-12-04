import React from "react";

function ResponseCard({ text }) {
  return (
    <div className="card mt-4 shadow-sm">
      <div className="card-body">
        <h5 className="card-title">Summary</h5>
        <p className="card-text">{text}</p>
      </div>
    </div>
  );
}

export default ResponseCard;
