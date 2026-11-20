// Entrypoint: stage the rendered artwork into the grading output directory.
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
const sourceImage = join(dirname(fileURLToPath(import.meta.url)), 'entry.png');

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourceImage, join(outputDir, 'entry.png'));
