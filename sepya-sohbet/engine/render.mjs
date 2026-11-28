// render.mjs — frame-exact capture: puppeteer calls window.render(t) for every frame and pipes PNGs into ffmpeg.
//   node render.mjs <story>                     full video -> stories/<story>/out/<name>.mp4 (muxes stories/<story>/audio/mix.wav if present)
//   node render.mjs <story> --stills=1,5.5,12   contact sheet of chosen seconds -> stories/<story>/out/stills.jpg
//   node render.mjs <story> --shots             contact sheet: the first, middle and last moment of every shot -> out/shots.jpg
//   node render.mjs <story> --cues              only writes audio/cues.json (shot list, lines, end card) for audio/mix.py
//   options: --scale=0.5 (draft), --from=s --to=s (a part), --crf=16, --name=x
import puppeteer from 'puppeteer-core';
import fs from 'node:fs'; import path from 'node:path'; import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { startServer } from './serve.mjs';
import { findChrome } from './chrome.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(3).map(a => a.replace(/^--/, '').split(/=(.*)/s)).map(([k, v]) => [k, v ?? '1']));
const story = process.argv[2] || 'ornek';
const SD = path.join(here, '..', 'stories', story), OUT = path.join(SD, 'out'); fs.mkdirSync(OUT, { recursive: true });
const scale = +(args.scale || 1);

const { server, port } = await startServer();
const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', protocolTimeout: 0,
  args: ['--no-sandbox', '--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--hide-scrollbars', '--force-device-scale-factor=1',
         '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
page.on('pageerror', e => console.log('PAGEERROR', e.message));
page.on('console', m => { if (['error', 'warning', 'warn'].includes(m.type())) console.log('CONSOLE', m.text()); });
await page.setViewport({ width: 540, height: 960 });
await page.goto(`http://127.0.0.1:${port}/engine/index.html?story=${story}&capture=1&scale=${scale}`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__ready || window.__error, { timeout: 180000 });
const err = await page.evaluate(() => window.__error);
if (err) { console.error('STORY ERROR', err); await browser.close(); server.close(); process.exit(1); }
const meta = await page.evaluate(() => window.__meta);
fs.mkdirSync(path.join(SD, 'audio'), { recursive: true });
fs.writeFileSync(path.join(SD, 'audio', 'cues.json'), JSON.stringify(meta.CUES, null, 1));
if (args.cues) { console.log('cues ->', path.join(SD, 'audio', 'cues.json')); await browser.close(); server.close(); process.exit(0); }
const grab = async t => {
  const url = await page.evaluate(t => { window.render(t); return document.getElementById('out').toDataURL('image/png'); }, t);
  return Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
};

async function sheet(times, name, cols = 5) {
  const dir = path.join(OUT, 'stills'); fs.mkdirSync(dir, { recursive: true });
  const files = [];
  for (const t of times) { const f = path.join(dir, `s_${t.toFixed(2)}.png`); fs.writeFileSync(f, await grab(t)); files.push(f); }
  cols = Math.min(files.length, cols);
  const tw = 270, th = 480;
  const inputs = files.flatMap(f => ['-i', f]);
  const lay = files.map((_, i) => `${(i % cols) * tw}_${Math.floor(i / cols) * th}`).join('|');
  const lab = (i) => `drawtext=text='${times[i].toFixed(2)}':fontcolor=yellow:fontsize=18:x=6:y=6`;
  const scaleF = files.map((_, i) => `[${i}:v]scale=${tw}:${th},${lab(i)}[v${i}]`).join(';');
  const filt = files.length === 1 ? `[0:v]scale=${tw}:${th},${lab(0)}` : `${scaleF};${files.map((_, i) => `[v${i}]`).join('')}xstack=inputs=${files.length}:layout=${lay}:fill=black`;
  const out = path.join(OUT, name);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputs, '-filter_complex', filt, '-q:v', '3', out]);
  console.log('sheet', out);
}

if (args.stills) {
  await sheet(args.stills.split(',').map(Number), args.name || 'stills.jpg', +(args.cols || 5));
} else if (args.shots) {
  const T = meta.SHOTS.flatMap(s => [s.a + .05, (s.a + s.b) / 2, s.b - .08]);
  await sheet(T, args.name || 'shots.jpg', 9);
} else {
  const FPS = meta.FPS, from = +(args.from || 0), to = +(args.to || meta.DUR), N = Math.round((to - from) * FPS);
  const name = args.name || meta.NAME + (scale !== 1 ? `_x${scale}` : '');
  const silent = path.join(OUT, name + '_video.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(args.crf || 16), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t1 = Date.now();
  for (let i = 0; i < N; i++) {
    const buf = await grab(from + i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 30 === 0) process.stdout.write(`frame ${i}/${N}  ${((Date.now() - t1) / 1000).toFixed(0)} s\r`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log(`\n${N} frames in ${((Date.now() - t1) / 1000).toFixed(1)} s`);
  const mix = path.join(SD, 'audio', 'mix.wav');
  const final = path.join(OUT, name + '.mp4');
  if (fs.existsSync(mix)) {
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', silent, '-ss', String(from), '-t', String(to - from), '-i', mix,
      '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', final]);
    fs.unlinkSync(silent);
  } else fs.renameSync(silent, final);
  console.log('->', final);
}
await browser.close(); server.close();
