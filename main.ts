// ai-excited-01 entry (Node 22, standard library only): the image is the
// entry.png beside this file, drawn in code by draw_excited.py at build time,
// and this program copies it to /output/entry.png. The gate takes a whole
// PNG or JPEG of at most 1 MiB and 1024 by 1024 pixels, and the judge sees
// exactly the bytes copied.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = new URL('./entry.png', import.meta.url);
const data = readFileSync(src);

// PNG magic: 89 50 4E 47 0D 0A 1A 0A
if (data[0] !== 0x89 || data[1] !== 0x50 || data[2] !== 0x4e || data[3] !== 0x47) {
  throw new Error('entry.png is not a PNG');
}
if (data.length > 1048576) {
  throw new Error(`entry.png is ${data.length} bytes, over the 1 MiB cap`);
}
// IHDR: width/height are the first 8 bytes after the 8-byte signature + 4-byte
// length + 4-byte 'IHDR' tag (offsets 16 and 20, big-endian).
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
}

const dest = join(outDir, 'entry.png');
copyFileSync(src, dest);
// The judge sees exactly these bytes: prove the copy is byte-identical.
const srcHash = createHash('sha256').update(data).digest('hex');
const outHash = createHash('sha256').update(readFileSync(dest)).digest('hex');
if (srcHash !== outHash || statSync(dest).size !== data.length) {
  throw new Error('copy to /output/entry.png did not match the source');
}
console.log(`copied entry.png (${width}x${height}, ${data.length} bytes, sha256 ${srcHash.slice(0, 16)}…)`);
