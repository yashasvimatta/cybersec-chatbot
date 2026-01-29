export function parseDriveFolderId(folderOrLink) {
  const input = (folderOrLink ?? "").trim();
  if (!input) return null;

  // Common share link: https://drive.google.com/drive/folders/<FOLDER_ID>
  const m = input.match(/\/folders\/([a-zA-Z0-9_-]+)/);
  if (m?.[1]) return m[1];

  // Sometimes: https://drive.google.com/open?id=<ID>
  const m2 = input.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if (m2?.[1]) return m2[1];

  // Assume raw folder id
  if (/^[a-zA-Z0-9_-]{10,}$/.test(input)) return input;
  return null;
}

