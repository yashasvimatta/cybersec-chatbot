export function chunkText(text, { maxChars = 1800, overlapChars = 200 } = {}) {
  const clean = (text ?? "").replace(/\r\n/g, "\n").trim();
  if (!clean) return [];

  const chunks = [];
  let i = 0;
  while (i < clean.length) {
    const end = Math.min(i + maxChars, clean.length);
    const chunk = clean.slice(i, end).trim();
    if (chunk) chunks.push(chunk);
    if (end >= clean.length) break;
    i = Math.max(0, end - overlapChars);
  }
  return chunks;
}

