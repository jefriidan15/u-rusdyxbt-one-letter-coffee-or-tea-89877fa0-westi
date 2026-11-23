import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

// One Letter: Coffee or Tea — entry for make.fun race
// u-rusdyxbt-one-letter-coffee-or-tea-89877fa0
// The program writes exactly one letter to /output/entry.txt:
// "A" for coffee. Nothing else — no word, no explanation,
// no punctuation, no newline. The file must be exactly 1 byte.
// "A" is the whole answer: coffee, first thing, no debate.

const outputDir = process.env.OUTPUT_DIR ?? "/output";
const entryPath = join(outputDir, "entry.txt");

mkdirSync(outputDir, { recursive: true });
writeFileSync(entryPath, "A", "utf8");

// Read-back check: the written file must be exactly "A".
const back = readFileSync(entryPath, "utf8");
if (back !== "A") {
  throw new Error(
    `read-back mismatch: expected exactly "A", got ${JSON.stringify(back)}`,
  );
}
