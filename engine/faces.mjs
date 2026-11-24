// faces.mjs — character sheet of a story: every look × every expression -> stories/<story>/out/faces.png
//   node faces.mjs <story> [--zoom]     (--zoom: heads only)
import puppeteer from 'puppeteer-core';
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import { startServer } from './serve.mjs';
import { findChrome } from './chrome.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const story = process.argv[2] || 'is-odasi', zoom = process.argv.includes('--zoom');
const OUT = path.join(here, '..', 'stories', story, 'out'); fs.mkdirSync(OUT, { recursive: true });
const CHROME = findChrome();
const ANGLE = process.platform === 'win32' ? ['--use-angle=d3d11'] : process.platform === 'darwin' ? ['--use-angle=metal'] : [];
// Linux containers: root needs --no-sandbox; extra flags (e.g. software GL: --use-angle=swiftshader --enable-unsafe-swiftshader) via CHROME_FLAGS
if (process.platform === 'linux' && process.getuid && process.getuid() === 0) ANGLE.push('--no-sandbox');
if (process.env.CHROME_FLAGS) ANGLE.push(...process.env.CHROME_FLAGS.split(/\s+/).filter(Boolean));
const { server, port } = await startServer();
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--ignore-gpu-blocklist', ...ANGLE, '--hide-scrollbars'] });
const page = await browser.newPage();
page.on('pageerror', e => console.log('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${port}/engine/faces.html?story=${story}${zoom ? '&zoom=1' : ''}`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__ready, { timeout: 60000 });
const url = await page.evaluate(() => document.getElementById('sheet').toDataURL('image/png'));
const file = path.join(OUT, zoom ? 'faces_zoom.png' : 'faces.png');
fs.writeFileSync(file, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
console.log('->', file);
await browser.close(); server.close();
