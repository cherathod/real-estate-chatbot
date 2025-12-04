import React, { useState } from "react";

function ChatInput({ onSend }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    onSend(query);
    setQuery("");
  };

  return (
    <form className="d-flex gap-2" onSubmit={handleSubmit}>
      <input
        type="text"
        className="form-control"
        placeholder="Ask about a locality (e.g., Analyze Wakad)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button className="btn btn-primary" type="submit">
        Send
      </button>
    </form>
  );
}

export default ChatInput;
