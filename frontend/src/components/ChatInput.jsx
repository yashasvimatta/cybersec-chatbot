import React, { useEffect, useRef } from "react";

export default function ChatInput({ value, onChange, onSend, disabled }) {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="controls">
      <div className="input-wrapper">
        <input
          ref={inputRef}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") onSend?.();
          }}
          disabled={disabled}
          placeholder="Ask about security incidents, policies, cloud hardening..."
        />
      </div>
      <button onClick={() => onSend?.()} disabled={disabled || !value?.trim()} type="button">
        Send
      </button>
    </div>
  );
}
