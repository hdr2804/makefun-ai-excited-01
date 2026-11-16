// ai-excited-01 entry (Node 22, standard library only): the image is the
// entry.png beside this file, drawn at build time by draw_excited.py, and
// this program copies it to /output/entry.png. The gate takes a whole PNG
// of at most 1 MiB and 1024 by 1024 pixels, and the judge sees exactly the
// bytes copied, so the program runs twice and both runs must write the
// same bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

// The gate takes a whole PNG of at most 1 MiB: refuse to write anything
// that is not a PNG, or that is over the cap, instead of failing the
// grade silently.
const src = new URL('./entry.png', import.meta.url);
const bytes = readFileSync(src);
if (bytes.length < 8 || bytes[0] !== 0x89 || bytes[1] !== 0x50 || bytes[2] !== 0x4e || bytes[3] !== 0x47) {
  throw new Error('entry.png is not a PNG (bad magic bytes)');
}
if (bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB gate cap`);
}
// The IHDR chunk carries the dimensions at bytes 16-23 (big-endian);
// the gate also caps the image at 1024 by 1024 pixels.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

copyFileSync(src, join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
