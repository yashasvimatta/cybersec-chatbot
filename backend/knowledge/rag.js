import path from "node:path";
import { VectorStore } from "./vectorStore.js";
import { parseDriveFolderId } from "./driveUtils.js";
import { syncDriveFolderToVectorStore } from "./driveSync.js";

const DEFAULT_INDEX_PATH = path.join(process.cwd(), "data", "rag-index.json");

let _store = null;
let _syncTimer = null;
let _syncing = false;
let _lastSync = null;
let _lastSyncResult = null;

function envInt(name, fallback) {
  const v = Number.parseInt(process.env[name] || "", 10);
  return Number.isFinite(v) ? v : fallback;
}

export async function initRag({ ai }) {
  if (_store) return { store: _store, lastSync: _lastSync, lastSyncResult: _lastSyncResult };

  _store = new VectorStore({ indexPath: DEFAULT_INDEX_PATH });
  await _store.load();

  const folderRaw = process.env.DRIVE_FOLDER;
  const folderId = parseDriveFolderId(folderRaw);
  const intervalMinutes = envInt("DRIVE_SYNC_INTERVAL_MINUTES", 30);

  // Kick off periodic sync only if configured
  if (folderId) {
    const run = async () => {
      if (_syncing) return;
      _syncing = true;
      try {
        const result = await syncDriveFolderToVectorStore({
          ai,
          folderId,
          store: _store,
        });
        _lastSync = new Date().toISOString();
        _lastSyncResult = result;
        console.log(
          `📚 Drive KB sync: total=${result.total} changed=${result.changed} skipped=${result.skipped} failed=${result.failed}`
        );
      } catch (e) {
        console.error("📚 Drive KB sync error:", e);
      } finally {
        _syncing = false;
      }
    };

    // Run once at startup, then periodically
    run();
    _syncTimer = setInterval(run, Math.max(5, intervalMinutes) * 60 * 1000);
  } else {
    console.log("📚 Drive KB sync disabled (set DRIVE_FOLDER to enable).");
  }

  return { store: _store, lastSync: _lastSync, lastSyncResult: _lastSyncResult };
}

export function getRagStatus() {
  return {
    enabled: Boolean(parseDriveFolderId(process.env.DRIVE_FOLDER)),
    indexPath: _store?.indexPath || DEFAULT_INDEX_PATH,
    items: _store?.items?.length || 0,
    files: _store ? Object.keys(_store.fileMeta || {}).length : 0,
    syncing: _syncing,
    lastSync: _lastSync,
    lastSyncResult: _lastSyncResult,
  };
}

export async function buildRagContext({ ai, queryText }) {
  if (!_store) return { context: "", matches: [] };
  const topK = envInt("RAG_TOP_K", 5);
  if (!_store.items.length) return { context: "", matches: [] };

  const embedResp = await ai.models.embedContent({
    model: "gemini-embedding-001",
    contents: queryText,
  });

  const emb0 = Array.isArray(embedResp?.embeddings) ? embedResp.embeddings[0] : null;
  const qValues = Array.isArray(emb0?.values) ? emb0.values : null;
  if (!qValues) return { context: "", matches: [] };

  const results = _store.search(qValues, { topK });
  const context =
    results.length === 0
      ? ""
      : [
          "Company knowledge base snippets (use if relevant):",
          ...results.map(
            ({ item }, idx) =>
              `\n[${idx + 1}] Source: ${item.fileName} (chunk ${item.chunkIndex + 1})\n${item.text}`
          ),
        ].join("\n");

  return {
    context,
    matches: results.map((r) => ({ id: r.item.id, fileName: r.item.fileName, score: r.score })),
  };
}

