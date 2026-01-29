import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { google } from "googleapis";

import { chunkText } from "./chunkText.js";

const DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.readonly";

function sha256(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex");
}

async function streamToString(stream) {
  const chunks = [];
  for await (const c of stream) chunks.push(c);
  return Buffer.concat(chunks).toString("utf8");
}

async function createDriveClient() {
  const auth = new google.auth.GoogleAuth({ scopes: [DRIVE_SCOPE] });
  return google.drive({ version: "v3", auth });
}

async function listFolderFiles(drive, folderId, { pageSize = 200 } = {}) {
  const out = [];
  let pageToken = undefined;
  do {
    const res = await drive.files.list({
      q: `'${folderId}' in parents and trashed = false`,
      fields: "nextPageToken, files(id, name, mimeType, modifiedTime, size)",
      pageSize,
      pageToken,
    });
    out.push(...(res.data.files || []));
    pageToken = res.data.nextPageToken || undefined;
  } while (pageToken);
  return out;
}

async function downloadAsText(drive, file) {
  const mime = file.mimeType || "";

  // Google Docs
  if (mime === "application/vnd.google-apps.document") {
    const res = await drive.files.export(
      { fileId: file.id, mimeType: "text/plain" },
      { responseType: "stream" }
    );
    return await streamToString(res.data);
  }

  // Google Slides/Sheets: export a best-effort text format
  if (mime === "application/vnd.google-apps.spreadsheet") {
    const res = await drive.files.export(
      { fileId: file.id, mimeType: "text/csv" },
      { responseType: "stream" }
    );
    return await streamToString(res.data);
  }
  if (mime === "application/vnd.google-apps.presentation") {
    const res = await drive.files.export(
      { fileId: file.id, mimeType: "text/plain" },
      { responseType: "stream" }
    );
    return await streamToString(res.data);
  }

  // For normal files, download media (only makes sense for text-ish files)
  const res = await drive.files.get({ fileId: file.id, alt: "media" }, { responseType: "stream" });
  const raw = await streamToString(res.data);

  // Heuristic: reject clearly-binary downloads
  const sample = raw.slice(0, 2000);
  if (sample.includes("\u0000")) return null;
  return raw;
}

export async function syncDriveFolderToVectorStore({
  ai,
  folderId,
  store,
  embeddingsModel = "gemini-embedding-001",
  maxFiles = 200,
}) {
  const drive = await createDriveClient();
  const files = (await listFolderFiles(drive, folderId)).slice(0, maxFiles);

  let changed = 0;
  let skipped = 0;
  let failed = 0;

  for (const f of files) {
    const fileId = f.id;
    const fileName = f.name || "Untitled";
    const modifiedTime = f.modifiedTime || "";
    const mimeType = f.mimeType || "";

    try {
      const text = await downloadAsText(drive, f);
      if (!text || !text.trim()) {
        skipped++;
        continue;
      }

      // Hard cap to keep indexing predictable
      const capped = text.length > 200_000 ? text.slice(0, 200_000) : text;
      const hash = sha256(capped);

      const prev = store.fileMeta[fileId];
      if (prev?.hash === hash) {
        skipped++;
        continue;
      }

      const chunks = chunkText(capped, { maxChars: 1800, overlapChars: 200 });
      if (chunks.length === 0) {
        skipped++;
        continue;
      }

      const embedResp = await ai.models.embedContent({
        model: embeddingsModel,
        contents: chunks,
      });

      const embeddings = embedResp?.embeddings || [];
      store.upsertEmbeddings({ fileId, fileName, chunks, embeddings });
      store.upsertFileMeta(fileId, { fileName, mimeType, modifiedTime, hash });

      changed++;
    } catch (e) {
      failed++;
      store.upsertFileMeta(fileId, { fileName, mimeType, modifiedTime, error: String(e?.message || e) });
    }
  }

  // Remove files that no longer exist in folder
  const currentIds = new Set(files.map((f) => f.id));
  for (const existingId of Object.keys(store.fileMeta)) {
    if (!currentIds.has(existingId)) store.removeFile(existingId);
  }

  await store.save();

  return {
    total: files.length,
    changed,
    skipped,
    failed,
    savedIndexPath: store.indexPath,
  };
}

