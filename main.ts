import { copyFileSync } from 'node:fs';
import { join } from 'node:path';
copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
