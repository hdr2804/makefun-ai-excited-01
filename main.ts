// ai-excited-01 entry (Node 22, standard library only): builds the image with
// the PIL script beside this file and writes it to /output/entry.png.
//
// The image is drawn fresh on every run from a fixed seed, so both runs write
// byte-identical PNGs. Outside the grader's container, MAKEFUN_OUTPUT_DIR
// stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { execFileSync } from 'node:child_process';
import { closeSync, existsSync, mkdirSync, openSync, readSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

execFileSync('python3', [join(here, 'draw_excited.py'), join(outDir, 'entry.png')], {
  stdio: 'inherit',
});

const out = join(outDir, 'entry.png');
if (!existsSync(out)) {
  throw new Error('draw_excited.py wrote no entry.png');
}
// Gate the file the judge will see: whole PNG, at most 1 MiB, 1024x1024.
const bytes = statSync(out).size;
if (bytes > 1048576) {
  throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB cap`);
}
const header = Buffer.alloc(33);
const fd = openSync(out, 'r');
readSync(fd, header, 0, 33, 0);
closeSync(fd);
if (header.readUInt32BE(16) !== 1024 || header.readUInt32BE(20) !== 1024) {
  throw new Error('entry.png is not 1024x1024');
}
console.log(`entry.png OK: 1024x1024, ${bytes} bytes`);
