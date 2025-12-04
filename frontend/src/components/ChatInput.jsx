import React, { useState } from "react";

function ChatInput({ onSend }) {
  // This state stores whatever the user types in the input box
  const [query, setQuery] = useState("");

  // This function runs when the form is submitted
  const handleSubmit = (e) => {
    e.preventDefault(); // Prevents page refresh after form submit

    // If the input is empty or only spaces, do nothing
    if (!query.trim()) return;

    onSend(query); // Send the user's query to the parent component
    setQuery(""); // Clear the input box after sending
  };

  return (
    <form className="d-flex gap-2" onSubmit={handleSubmit}>
      {/* Text box where user types their message */}
      <input
        type="text"
        className="form-control"
        placeholder="Ask about a locality (e.g., Analyze Wakad)"
        value={query} // The input box shows the value stored in state
        onChange={(e) => setQuery(e.target.value)} // Update state when user types
      />

      {/* Button to send the query */}
      <button className="btn btn-primary" type="submit">
        Send
      </button>
    </form>
  );
}

export default ChatInput;
