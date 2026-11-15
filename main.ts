// make.fun ai-excited-01 entry (Node 22, standard library only): the image
// is entry.png beside this file, and the program copies it to
// /output/entry.png. Outside the grader's container, MAKEFUN_OUTPUT_DIR
// stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const target = join(outDir, 'entry.png');
copyFileSync(new URL('./entry.png', import.meta.url), target);

// The gate reads exactly this file: it must stay a whole PNG under 1 MiB.
const data = readFileSync(target);
if (data.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') {
  throw new Error('entry.png must be a PNG');
}
if (data.length > 1024 * 1024) {
  throw new Error(`entry.png is ${data.length} bytes, over the 1 MiB cap`);
}
// IHDR: width and height are the first 8 bytes after the 8-byte signature
// and the 8-byte chunk header.
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
}
