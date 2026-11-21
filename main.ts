// Entry program for make.fun news-image-20261121.
// Copies the pre-rendered front page (entry.png, drawn by gen.py)
// to the output directory. No network, no randomness, no timestamps:
// every run writes the same bytes.
import { copyFileSync, mkdirSync } from "node:fs";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL("./entry.png", import.meta.url), `${outDir}/entry.png`);
