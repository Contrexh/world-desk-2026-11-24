// Entry for make.fun news-image-20261124: ships the front page as poster.png and
// copies it to /output/entry.png, the file the gate and the judge read.
import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const out = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(out, { recursive: true });
copyFileSync(new URL('./poster.png', import.meta.url), join(out, 'entry.png'));
