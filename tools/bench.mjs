import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";
import { parseArgs } from "node:util";

async function waitFor(description, read) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const value = await read();
    if (value) return value;
    await sleep(50);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

function start(command, args) {
  const child = spawn(command, args, { stdio: ["ignore", "pipe", "ignore"] });
  let output = "";
  let failure;
  child.stdout.setEncoding("utf8").on("data", chunk => { output += chunk; });
  child.on("error", error => { failure = error; });
  return {
    child,
    output() {
      if (failure) throw failure;
      if (child.exitCode !== null) throw new Error(`${command} exited with code ${child.exitCode}`);
      return output;
    },
  };
}

async function connect(url) {
  const socket = new WebSocket(url);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  let nextId = 0;
  return {
    close: () => socket.close(),
    call(method, params = {}, timeout = 15000) {
      const id = ++nextId;
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          socket.removeEventListener("message", receive);
          reject(new Error(`Timed out: ${method}`));
        }, timeout);
        function receive(event) {
          const response = JSON.parse(event.data);
          if (response.id !== id) return;
          clearTimeout(timer);
          socket.removeEventListener("message", receive);
          if (response.error) reject(new Error(response.error.message));
          else resolve(response.result);
        }
        socket.addEventListener("message", receive);
        socket.send(JSON.stringify({ id, method, params }));
      });
    },
  };
}

async function measureScene(seconds) {
  const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
  await frame();
  const loaded = await frame();
  const warmupEnd = loaded + 3000;
  let previous = await frame();
  while (previous < warmupEnd) previous = await frame();

  const start = previous;
  const deltas = [];
  while (previous - start < seconds * 1000) {
    const now = await frame();
    deltas.push(now - previous);
    previous = now;
  }
  const measured = (previous - start) / 1000;
  const slowest = deltas.sort((a, b) => b - a).slice(0, Math.ceil(deltas.length / 100));
  return {
    avg_fps: deltas.length / measured,
    p1_low_fps: slowest.length * 1000 / slowest.reduce((total, delta) => total + delta, 0),
    frames: deltas.length,
    measured_s: measured,
    load_ms: loaded,
  };
}

async function main() {
  const { values } = parseArgs({ options: {
    seed: { type: "string", default: "42" },
    duration: { type: "string", default: "30" },
    out: { type: "string" },
  } });
  const duration = Number(values.duration);
  if (!/^-?\d+$/.test(values.seed) || !Number.isFinite(duration) || duration <= 0 || !values.out) {
    throw new Error("Usage: node tools/bench.mjs --seed 42 --duration 30 --out bench.json");
  }

  const profile = await mkdtemp(join(tmpdir(), "chonoi-bench-"));
  let game, chrome, page;
  try {
    game = start(process.env.PYTHON || "python3", ["-m", "chonoi.live", "--mode", "gather", "--seed", values.seed, "--port", "0"]);
    const url = await waitFor("live gather", () => game.output().match(/http:\/\/127\.0\.0\.1:\d+\//)?.[0]);
    chrome = start(process.env.CHONOI_CHROME || (process.platform === "darwin"
      ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : "google-chrome"), [
      "--headless", "--no-first-run", "--disable-background-networking",
      "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank",
    ]);
    const port = await waitFor("Chrome", async () => {
      chrome.output();
      return (await readFile(join(profile, "DevToolsActivePort"), "utf8").catch(error => {
        if (error.code !== "ENOENT") throw error;
        return "";
      })).split("\n")[0];
    });
    const response = await fetch(`http://127.0.0.1:${port}/json/list`);
    const target = (await response.json()).find(item => item.type === "page");
    page = await connect(target.webSocketDebuggerUrl);
    await page.call("Emulation.setDeviceMetricsOverride", { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
    const navigation = await page.call("Page.navigate", { url });
    if (navigation.errorText) throw new Error(navigation.errorText);
    await waitFor("gather snapshot", async () => {
      const { result } = await page.call("Runtime.evaluate", { expression: 'typeof snap !== "undefined" && snap?.phase === "gather" && !snap.error' });
      return result.value;
    });
    const report = await page.call("Runtime.evaluate", {
      expression: `(${measureScene})(${duration})`, awaitPromise: true, returnByValue: true,
    }, (duration + 15) * 1000);
    if (report.exceptionDetails) throw new Error(report.exceptionDetails.text);
    await writeFile(values.out, JSON.stringify(report.result.value, null, 2) + "\n");
  } finally {
    page?.close();
    game?.child.kill();
    if (chrome?.child.pid && chrome.child.exitCode === null) {
      const closed = new Promise(resolve => chrome.child.once("close", resolve));
      chrome.child.kill();
      await closed;
    }
    await rm(profile, { recursive: true, force: true });
  }
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
