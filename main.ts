// ai-excited-01 entry (Node 22, standard library only).
// Builds the image at run time with the bundled PIL script and writes it to
// the output directory: /output in the grader, MAKEFUN_OUTPUT_DIR locally.
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const here = dirname(fileURLToPath(import.meta.url));
const outPath = join(outDir, 'entry.png');

mkdirSync(outDir, { recursive: true });

execFileSync('python3', [join(here, 'draw_excited.py'), outPath], {
  stdio: 'inherit',
});

if (!existsSync(outPath)) {
  throw new Error(`draw script did not write ${outPath}`);
}

// Gate check, same limits as the competition: a whole PNG, at most
// 1024x1024 pixels and at most 1 MiB.
const bytes = readFileSync(outPath);
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error('output is not a PNG');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`output is ${width}x${height}, over the 1024x1024 cap`);
}
if (bytes.length > 1048576) {
  throw new Error(`output is ${bytes.length} bytes, over the 1 MiB cap`);
}
console.log(
  `entry written to ${outPath} (${width}x${height}, ${statSync(outPath).size} bytes)`,
);
