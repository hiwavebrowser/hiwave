// CH2.B4 oracle: the canvas_context_tests assertions in the pinned Chromium.
import { readFileSync, writeFileSync } from 'node:fs';
import { chromium } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b4/tools/parity_oracle/node_modules/playwright/index.mjs';
import { getDeterministicLaunchOptions } from '/Users/petecopeland/Repos/.worktrees/z-ch2-b4/tools/parity_oracle/deterministic.mjs';

const root = '/Users/petecopeland/Repos/.worktrees/z-ch2-b4/';
const dir = root + 'target/b4-oracle/';
const report = readFileSync(root + 'crates/hiwave-app/src/ui/report.html', 'utf8');
const chart = readFileSync(root + 'crates/hiwave-app/src/ui/chart.umd.min.js', 'utf8');
const host = "<script>window.ipc = { postMessage: function (raw) { var cmd = JSON.parse(raw).cmd; if (cmd !== 'get_today_stats') return; Promise.resolve().then(function () { window.dispatchEvent(new CustomEvent('hiwave-response', { detail: { type: 'success', data: { pages_visited: 42, trackers_blocked: 311, ads_blocked: 97, popups_blocked: 3, bandwidth_saved: 0, time_saved: 0, focus_time: 0 } } })); }); } }; window.__errs = []; console.error = function (m) { window.__errs.push(String(m)); };</script>";
const marker = '<!-- Chart.js is injected by Rust before page load -->';
writeFileSync(dir + 'report.html', report.replace(marker, () => host + '<script>' + chart + '</script>'));
writeFileSync(dir + 'canvas.html', '<!doctype html><canvas id=c width=300 height=150></canvas>');

const b = await chromium.launch(getDeterministicLaunchOptions());
console.log('chromium', b.version());
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.goto('file://' + dir + 'canvas.html');
console.log(await p.evaluate(() => {
  var c = document.getElementById('c'); var x = c.getContext('2d');
  return JSON.stringify([x !== null, x && x.canvas === c, c.getContext('2d') === x, String(x && Object.prototype.toString.call(x))]);
}));
await p.goto('file://' + dir + 'report.html');
await p.waitForTimeout(500);
console.log(await p.evaluate(() => JSON.stringify([
  document.getElementById('error-container').textContent.trim(), window.__errs,
  document.getElementById('stat-trackers').textContent,
  !!(activityChart && activityChart.canvas), !!(protectionChart && protectionChart.canvas)])));
await b.close();
