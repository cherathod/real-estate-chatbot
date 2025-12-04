import React from "react";

function ResponseCard({ text }) {
  return (
    // A simple Bootstrap card to display the summary text
    <div className="card mt-4 shadow-sm">
      <div className="card-body">
        {/* Title of the card */}
        <h5 className="card-title">Summary</h5>

        {/* The summary text coming from the API */}
        <p className="card-text">{text}</p>
      </div>
    </div>
  );
}

export default ResponseCard;
