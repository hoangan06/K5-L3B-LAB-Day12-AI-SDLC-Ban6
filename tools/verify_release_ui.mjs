// Kiểm cảnh báo trên browser thật với fixture engine hợp lệ, không thay snapshot.
import { mkdtemp, readFile, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import { start, connect, waitFor } from "./bench.mjs";

const { values } = parseArgs({ options: { out: { type: "string" } } });
if (!values.out) throw new Error("Usage: node tools/verify_release_ui.mjs --out <existing-directory>");
const temporary = await mkdtemp(join(tmpdir(), "chonoi-ui-"));
let chrome, page, game;
const report = { method: "Real engine scenarios + browser input; no snapshot replacement", checks: [] };
try {
  const contract = JSON.parse(await readFile("game.contract.json", "utf8"));
  chrome = start(process.env.CHONOI_CHROME || (process.platform === "darwin"
    ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : "google-chrome"), [
    "--headless", "--no-first-run", "--remote-debugging-port=0", `--user-data-dir=${temporary}`, "about:blank",
  ]);
  const port = await waitFor("Chrome", async () => {
    chrome.output();
    return (await readFile(join(temporary, "DevToolsActivePort"), "utf8").catch(() => "")).split("\n")[0];
  });
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  page = await connect(targets.find(target => target.type === "page").webSocketDebuggerUrl);
  await page.call("Page.enable");
  await page.call("Runtime.enable");
  await page.call("Emulation.setDeviceMetricsOverride", { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  const dish = Object.keys(contract.tuning.menu)[0];
  const cases = [
    { mode: "gather", name: "gather-warnings", text: ["Thủy quái ở gần", "Oxy sắp hết"], scenario: {
      player: { pos: [60, 10], oxygen_ticks: 400 }, nodes: [], random_fish: false,
      monsters: [{ id: "M1", kind: "ca_sau", pos: [69, 10], waypoints: [[69, 10], [75, 10]] }],
    } },
    { mode: "quan", name: "customer-warning", text: ["Khách sắp giận"], scenario: {
      stock: [], random_customers: false, customers: [{ id: "C1", table_id: "T1", dish_id: dish,
        order_tick: 0, state: "waiting", patience_ticks_left: 800, order_status: "unfulfillable" }],
    } },
  ];
  for (const test of cases) {
    const scenarioPath = join(temporary, `${test.name}.json`);
    await writeFile(scenarioPath, JSON.stringify({ [test.mode]: test.scenario }));
    game = start(process.env.PYTHON || "python3", ["-m", "chonoi.live", "--mode", test.mode,
      "--seed", "42", "--scenario", scenarioPath, "--port", "0"]);
    const url = await waitFor("game", () => game.output().match(/http:\/\/127\.0\.0\.1:\d+\//)?.[0]);
    await page.call("Page.navigate", { url: url + "?nointro=1" });
    await waitFor("warning elements", async () => (await page.call("Runtime.evaluate", {
      expression: 'Boolean(document.getElementById("contrast-toggle") && typeof snap !== "undefined" && snap)',
    })).result.value);
    const rect = (await page.call("Runtime.evaluate", { expression:
      'JSON.stringify((()=>{const r=document.getElementById("contrast-toggle").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})())',
    })).result.value;
    const point = JSON.parse(rect);
    await page.call("Input.dispatchMouseEvent", { type: "mousePressed", button: "left", clickCount: 1, ...point });
    await page.call("Input.dispatchMouseEvent", { type: "mouseReleased", button: "left", clickCount: 1, ...point });
    // Phát input di chuyển thật qua handler UI, không sửa state engine.
    await page.call("Input.dispatchKeyEvent", { type: "keyDown", key: "d", code: "KeyD" });
    await new Promise(resolve => setTimeout(resolve, 150));
    await page.call("Input.dispatchKeyEvent", { type: "keyUp", key: "d", code: "KeyD" });
    const observed = await waitFor("all expected warnings in high contrast", async () => {
      if (page.errors.length) throw new Error(JSON.stringify(page.errors[0]));
      const state = (await page.call("Runtime.evaluate", { expression: `JSON.stringify({
        text:document.getElementById("warnings").textContent,
        high_contrast:document.body.classList.contains("high-contrast"), tick:snap.tick,
        phase:snap.phase, player:snap.player.pos,
        pressed:document.getElementById("contrast-toggle").getAttribute("aria-pressed")
      })` })).result.value;
      const current = JSON.parse(state);
      return current.high_contrast && current.pressed === "true" && test.text.every(text => current.text.includes(text)) ? current : null;
    });
    const screenshot = await page.call("Page.captureScreenshot", { format: "png" });
    const image = `${test.name}.png`;
    await writeFile(join(values.out, image), Buffer.from(screenshot.data, "base64"));
    report.checks.push({ name: test.name, expected: test.text, observed, screenshot: image, console_errors: page.errors.length });
    game.child.kill();
    game = null;
  }
  report.status = "PASS";
  await writeFile(join(values.out, "ui-check.json"), JSON.stringify(report, null, 2) + "\n");
  console.log("PASS UI: all three engine warnings visible in high contrast; zero console exceptions");
} finally {
  page?.close();
  game?.child.kill();
  if (chrome?.child.pid && chrome.child.exitCode === null) {
    const closed = new Promise(resolve => chrome.child.once("close", resolve));
    chrome.child.kill();
    await closed;
  }
  if (dirname(resolve(temporary)) !== resolve(tmpdir()) || !basename(temporary).startsWith("chonoi-ui-")) {
    throw new Error("Unexpected temporary directory");
  }
  await rm(temporary, { recursive: true, force: true });
}
