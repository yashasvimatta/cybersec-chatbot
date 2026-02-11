import React, { useEffect, useRef, useState } from "react";

export default function ChatInput({ value, onChange, onSend, disabled, onAttach }) {
  const inputRef = useRef(null);
  const fileRef = useRef(null);
  const [attachment, setAttachment] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Allowed file types
  const ALLOWED_TYPES = [
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".txt", ".csv", ".md", ".json",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
  ];

  const handleFileSelect = (file) => {
    if (!file) return;
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_TYPES.includes(ext)) {
      alert(`Unsupported file type: ${ext}\nAllowed: ${ALLOWED_TYPES.join(", ")}`);
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      alert("File too large. Maximum is 50 MB.");
      return;
    }
    setAttachment(file);

    // Generate preview for images
    const imageTypes = [".png", ".jpg", ".jpeg", ".gif", ".webp"];
    if (imageTypes.includes(ext)) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const clearAttachment = () => {
    setAttachment(null);
    setPreview(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  const handleSend = () => {
    if (attachment) {
      onAttach?.(attachment, value);
      clearAttachment();
      onChange?.("");
    } else {
      onSend?.();
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const getFileIcon = (filename) => {
    const ext = filename?.split(".").pop().toLowerCase();
    const icons = {
      pdf: "\uD83D\uDCC4",
      docx: "\uD83D\uDCC3", doc: "\uD83D\uDCC3",
      xlsx: "\uD83D\uDCCA", xls: "\uD83D\uDCCA",
      pptx: "\uD83D\uDCCA", ppt: "\uD83D\uDCCA",
      txt: "\uD83D\uDCC4", csv: "\uD83D\uDCCA", md: "\uD83D\uDCC4",
      png: "\uD83D\uDDBC\uFE0F", jpg: "\uD83D\uDDBC\uFE0F", jpeg: "\uD83D\uDDBC\uFE0F",
      gif: "\uD83D\uDDBC\uFE0F", webp: "\uD83D\uDDBC\uFE0F",
    };
    return icons[ext] || "\uD83D\uDCC1";
  };

  const canSend = attachment || value?.trim();

  return (
    <div
      className={`chat-input-wrap ${dragOver ? "drag-over" : ""}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      {/* Attachment preview */}
      {attachment && (
        <div className="attachment-preview">
          {preview ? (
            <img src={preview} alt="Preview" className="attachment-thumb" />
          ) : (
            <span className="attachment-icon">{getFileIcon(attachment.name)}</span>
          )}
          <div className="attachment-info">
            <span className="attachment-name">{attachment.name}</span>
            <span className="attachment-size">
              {(attachment.size / 1024).toFixed(1)} KB
            </span>
          </div>
          <button
            className="attachment-remove"
            onClick={clearAttachment}
            title="Remove attachment"
            type="button"
          >
            &times;
          </button>
        </div>
      )}

      {/* Drag overlay */}
      {dragOver && (
        <div className="drag-overlay">
          <span>Drop file here</span>
        </div>
      )}

      {/* Input row */}
      <div className="controls">
        <input
          type="file"
          ref={fileRef}
          className="file-input-hidden"
          accept={ALLOWED_TYPES.join(",")}
          onChange={(e) => handleFileSelect(e.target.files?.[0])}
        />

        <button
          className="btn-attach"
          onClick={() => fileRef.current?.click()}
          disabled={disabled}
          title="Attach a file or image"
          type="button"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
          </svg>
        </button>

        <div className="input-wrapper">
          <input
            ref={inputRef}
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) handleSend();
            }}
            disabled={disabled}
            placeholder={
              attachment
                ? `Ask about ${attachment.name}...`
                : "Ask about security incidents, policies, cloud hardening..."
            }
          />
        </div>

        <button
          onClick={handleSend}
          disabled={disabled || !canSend}
          type="button"
        >
          Send
        </button>
      </div>
    </div>
  );
}
