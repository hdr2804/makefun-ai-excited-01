// ai-excited-01 entry: the program copies the image the build drew
// (draw_excited.py, PIL, build-time only) to the grader's output
// directory. Node 22, standard library only.
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const src = new URL('./entry.png', import.meta.url);
const bytes = readFileSync(src);
// Gate: whole PNG, at most 1 MiB and 1024 by 1024 pixels.
if (bytes.length > 1048576) throw new Error(`entry.png is ${bytes.length} bytes, over 1 MiB`);
if (!bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) {
  throw new Error('entry.png is not a PNG');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) throw new Error(`entry.png is ${width}x${height}, over 1024x1024`);
if (bytes.subarray(12, 16).toString('latin1') !== 'IHDR') throw new Error('entry.png has no IHDR chunk');
const dest = join(outDir, 'entry.png');
copyFileSync(src, dest);
// The program is a pure copy: the bytes it writes must equal the bytes it read.
if (!readFileSync(dest).equals(bytes)) throw new Error('output bytes differ from entry.png');
