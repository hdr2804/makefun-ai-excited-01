// ai-excited-01 entry (Node 22, standard library only): the image is the
// entry.png beside this file, drawn at build time by draw_excited.py, and
// the program copies it to /output/entry.png. The gate takes a whole PNG
// of at most 1 MiB and 1024 by 1024 pixels, and the judge sees exactly
// the bytes copied. Runs twice with byte-identical output: the file is
// fixed, so both runs copy the same bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

const src = new URL('./entry.png', import.meta.url);
const dest = join(outDir, 'entry.png');
copyFileSync(src, dest);

// The gate refuses anything over 1 MiB, so fail loudly here instead.
const size = statSync(dest).size;
if (size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB gate`);
}

// The gate tells PNG from JPEG by its first bytes; refuse a non-PNG.
const head = readFileSync(dest).subarray(0, 8);
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!head.equals(pngMagic)) {
  throw new Error('entry.png does not start with the PNG magic bytes');
}

// The gate caps the image at 1024 by 1024; refuse anything larger by
// reading the IHDR chunk's width and height (bytes 16-23, big-endian).
const ihdr = readFileSync(dest).subarray(16, 24);
const width = ihdr.readUInt32BE(0);
const height = ihdr.readUInt32BE(4);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 gate`);
}

// A whole PNG ends with its IEND chunk; refuse a truncated file.
const tail = readFileSync(dest).subarray(-12);
if (tail.toString('latin1') !== '\0\0\0\0IEND\xaeB`\x82') {
  throw new Error('entry.png does not end with the IEND chunk');
}

console.log(`wrote ${dest}: ${size} bytes`);
