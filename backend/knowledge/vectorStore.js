import fs from "node:fs/promises";
import path from "node:path";
function dot(a, b) {
  let s = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) s += a[i] * b[i];
  return s;
}

function norm(a) {
  return Math.sqrt(dot(a, a)) || 1;
}

function normalize(vec) {
  const n = norm(vec);
  return vec.map((x) => x / n);
}

export class VectorStore {
  constructor({ indexPath }) {
    this.indexPath = indexPath;
    this.items = []; // { id, fileId, fileName, chunkIndex, text, embedding, updatedAt }
    this.fileMeta = {}; // fileId -> { fileName, mimeType, modifiedTime, hash, updatedAt }
  }

  
  async load() {
    try {
      const raw = await fs.readFile(this.indexPath, "utf8");
      const parsed = JSON.parse(raw);
      this.items = Array.isArray(parsed.items) ? parsed.items : [];
      this.fileMeta = parsed.fileMeta && typeof parsed.fileMeta === "object" ? parsed.fileMeta : {};
    } catch {
      // ok if missing/invalid
      this.items = [];
      this.fileMeta = {};
    }
  }

  async save() {
    await fs.mkdir(path.dirname(this.indexPath), { recursive: true });
    await fs.writeFile(
      this.indexPath,
      JSON.stringify(
        {
          version: 1,
          savedAt: new Date().toISOString(),
          items: this.items,
          fileMeta: this.fileMeta,
        },
        null,
        2
      ),
      "utf8"
    );
  }

  upsertFileMeta(fileId, meta) {
    this.fileMeta[fileId] = { ...(this.fileMeta[fileId] || {}), ...meta, updatedAt: new Date().toISOString() };
  }

  removeFile(fileId) {
    this.items = this.items.filter((it) => it.fileId !== fileId);
    delete this.fileMeta[fileId];
  }

  upsertEmbeddings({ fileId, fileName, chunks, embeddings }) {
    // Remove existing chunks for this file, then add fresh ones
    this.items = this.items.filter((it) => it.fileId !== fileId);
    const now = new Date().toISOString();
    for (let i = 0; i < chunks.length; i++) {
      const emb = embeddings[i];
      const values = Array.isArray(emb?.values) ? emb.values : Array.isArray(emb) ? emb : null;
      if (!values) continue;
      this.items.push({
        id: `${fileId}:${i}`,
        fileId,
        fileName,
        chunkIndex: i,
        text: chunks[i],
        embedding: normalize(values),
        updatedAt: now,
      });
    }
  }

  search(queryEmbedding, { topK = 5 } = {}) {
    const q = normalize(queryEmbedding);
    const scored = this.items
      .map((it) => ({ item: it, score: dot(q, it.embedding) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
    return scored;
  }
}

