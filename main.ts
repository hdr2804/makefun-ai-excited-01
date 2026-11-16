// ai-excited-01 — "One small leap becomes a universe"
// Node 22, standard library only. Copies the committed entry.png to the
// output location the grader expects (/output/entry.png by default).
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dest = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);

const bytes = readFileSync(dest);

// Gate asserts: the judge only sees these bytes, so fail loudly if the
// image ever stops matching the competition limits.
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
for (let i = 0; i < PNG_MAGIC.length; i++) {
  if (bytes[i] !== PNG_MAGIC[i]) throw new Error("entry.png is not a PNG");
}
if (bytes.length > 1_048_576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
}

// IHDR: width and height are big-endian uint32s at byte offsets 16 and 20.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
}

// Copy verification: what landed in /output must equal the committed file.
const source = readFileSync(src);
if (!source.equals(bytes)) throw new Error("output differs from entry.png");
console.log(`wrote ${dest} (${bytes.length} bytes, ${width}x${height})`);
