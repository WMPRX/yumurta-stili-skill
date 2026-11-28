// faces.mjs — one page with every species × expression and every pose: node faces.mjs [baykus,kirpi] -> out/faces.png
import puppeteer from 'puppeteer-core'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { startServer } from './serve.mjs'; import { findChrome } from './chrome.mjs';
const here = path.dirname(fileURLToPath(import.meta.url));
const { server, port } = await startServer();
const b = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', args: ['--no-sandbox'] });
const p = await b.newPage(); p.on('pageerror', e => console.log('PAGEERROR', e.message));
await p.goto(`http://127.0.0.1:${port}/engine/faces.html?tur=${process.argv[2] || 'baykus,kirpi'}`); await p.waitForFunction(() => window.__ready, { timeout: 30000 });
const url = await p.evaluate(() => document.getElementById('c').toDataURL('image/png'));
fs.mkdirSync(path.join(here, '..', 'out'), { recursive: true });
const f = path.join(here, '..', 'out', 'faces.png'); fs.writeFileSync(f, Buffer.from(url.split(',')[1], 'base64')); console.log(f);
await b.close(); server.close();
