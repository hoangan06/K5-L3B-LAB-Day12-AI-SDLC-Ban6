"use strict";
/*
 * Lớp phủ sáng tạo (Gói 2), chỉ vẽ từ snapshot.creative (chỉ có khi chạy live --creative).
 * Tự vẽ trên canvas riêng, không sửa index.html. Dùng lại biến toàn cục `snap` của index.html và công thức dựng cảnh
 * của drawGather (cùng tỉ lệ). Không gửi gì lên server (phím mũi tên vẫn đi qua /input như bơi bình thường).
 * Hình ảnh tự thiết kế; các đền chỉ vẽ trang nghiêm, không phải quái.
 */
(function () {
  const cv2 = document.createElement("canvas");
  cv2.id = "creative-layer";
  cv2.style.cssText = "position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:5";
  document.body.appendChild(cv2);
  const c = cv2.getContext("2d");
  const ARROW = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

  function fit() {
    const dpr = window.devicePixelRatio || 1, w = innerWidth, h = innerHeight;
    if (cv2.width !== Math.round(w * dpr) || cv2.height !== Math.round(h * dpr)) { cv2.width = Math.round(w * dpr); cv2.height = Math.round(h * dpr); }
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.clearRect(0, 0, w, h);
    return [w, h];
  }
  const FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif";
  const hc = () => document.body.classList.contains("high-contrast");
  // Chữ >= 18 px, không chân, có viền; tương phản cao: chữ trắng trên nền đen viền vàng.
  function txt(s, x, y, o = {}) {
    const size = Math.max(18, o.size || 18);
    c.font = "700 " + size + "px " + FONT;
    c.textAlign = o.align || "left"; c.textBaseline = o.base || "alphabetic"; c.lineJoin = "round";
    if (hc() && o.plain) {  // đã nằm trong khung đen: chỉ chữ trắng
      c.strokeStyle = "#000"; c.lineWidth = 4; c.strokeText(s, x, y); c.fillStyle = "#fff"; c.fillText(s, x, y);
      return;
    }
    if (hc()) {
      const w = c.measureText(s).width, h = size + 8;
      const x0 = c.textAlign === "center" ? x - w / 2 : c.textAlign === "right" ? x - w : x;
      const y0 = c.textBaseline === "alphabetic" ? y - size : c.textBaseline === "middle" ? y - h / 2 : y;
      c.fillStyle = "#000"; c.fillRect(x0 - 6, y0 - 3, w + 12, h);
      c.strokeStyle = "#ffef00"; c.lineWidth = 2; c.strokeRect(x0 - 6, y0 - 3, w + 12, h);
      c.fillStyle = "#fff"; c.fillText(s, x, y);
      return;
    }
    c.strokeStyle = "rgba(6,16,24,.92)"; c.lineWidth = 5; c.strokeText(s, x, y);
    c.fillStyle = o.color || "#fff"; c.fillText(s, x, y);
  }
  const panel = (x, y, w, h, edge) => {
    c.fillStyle = hc() ? "#000" : "rgba(8,20,30,.8)"; c.fillRect(x, y, w, h);
    c.strokeStyle = hc() ? "#ffef00" : edge; c.lineWidth = 2; c.strokeRect(x + 1, y + 1, w - 2, h - 2);
  };
  function arrow(cx, cy, dir, size, fill, stroke) {
    const [dx, dy] = ARROW[dir];
    c.save(); c.translate(cx, cy); c.rotate(Math.atan2(dy, dx));
    c.fillStyle = fill; c.strokeStyle = stroke; c.lineWidth = 2;
    c.beginPath(); c.moveTo(size, 0); c.lineTo(-size * 0.2, -size * 0.8); c.lineTo(-size * 0.2, -size * 0.3);
    c.lineTo(-size, -size * 0.3); c.lineTo(-size, size * 0.3); c.lineTo(-size * 0.2, size * 0.3); c.lineTo(-size * 0.2, size * 0.8);
    c.closePath(); c.fill(); c.stroke(); c.restore();
  }
  const lerp = (a, b, k) => a + (b - a) * k;
  function shrine(sx, sy, s, sh, ongFish, tick) {   // thân đền/miếu vẽ pixel ở index.html (lớp cảnh); ở đây chỉ còn vòng tiến độ thắp hương
    const x = sx(sh.x), y = sy(0);
    if (!sh.lit && sh.progress > 0) {  // vòng tiến độ thắp hương + chữ
      const k = Math.min(1, sh.progress / sh.stand_ticks), cy = y - 1.2 * s, r = 2.8 * s;
      c.strokeStyle = "rgba(255,255,255,.3)"; c.lineWidth = 6; c.beginPath(); c.arc(x, cy, r, 0, 7); c.stroke();
      c.strokeStyle = hc() ? "#ffef00" : "#ffd54f"; c.lineWidth = 6; c.lineCap = "round"; c.beginPath();
      c.arc(x, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * k); c.stroke(); c.lineCap = "butt";
      txt("Thắp hương… " + Math.round(k * 100) + "%", x, y + 0.9 * s + 18, { align: "center", color: "#ffd54f" });
    }
  }
  // Mãng Xà: trồi lên từ sâu + gợn nước khi xuất hiện, chìm xuống khi biến mất. Thời gian đếm theo tick (pause thì đứng yên).
  const FADE = 60, seen = new Map();  // id -> {born, gone, pos}
  let lastTick = 0;
  function serpent(sx, sy, s, m, tick, k, sink) {
    const x = sx(m.pos[0]), y0 = sy(m.pos[1]), y = y0 + (1 - k) * 3.5 * s;
    c.save();
    // gợn nước: ba vòng elip lan ra quanh chỗ xuất hiện/biến mất
    const t = sink ? 1 - k : k;
    for (let i = 0; i < 3; i++) {
      const q = (t * 1.2 + i / 3) % 1;
      c.strokeStyle = "rgba(190,235,255," + (0.6 * (1 - q) * (sink ? k : 1)) + ")"; c.lineWidth = 2;
      c.beginPath(); c.ellipse(x, y0, (1.2 + q * 3.5) * s, (0.35 + q * 0.9) * s, 0, 0, 7); c.stroke();
    }
    c.globalAlpha = Math.max(0, Math.min(1, k));
    // Vẽ kiểu pixel như cá sấu của lớp lõi: lưới ô vuông 1 px thấp (= s / 8.5, cùng tỉ lệ 1 m ≈ 8.5 px), từng cột thân.
    // Thân dài ~7 m (60 cột), dày dần về phía đầu; uốn sin chạy dọc thân theo tick; đầu quay theo hướng bơi (m.dir).
    const chase = m.state === "chase", dir = m.dir || 1, p = s / 8.5, n = 60;
    const P = (ix, iy, w, h, col) => { c.fillStyle = col; c.fillRect(Math.round(x + dir * ix * p - (dir < 0 ? w * p : 0)), Math.round(y + iy * p), Math.ceil(w * p), Math.ceil(h * p)); };
    const body = chase ? "#7a8f2e" : "#4f8a45", dark = chase ? "#3d4a14" : "#2a4f2a", belly = "#e9d58a", gold = "#d9a72a";
    const ph = tick / (chase ? 5 : 9), amp = chase ? 4 : 3;
    let hy = 0;
    for (let i = 0; i < n; i++) {   // i = 0 đuôi, n-1 cổ
      const u = i / (n - 1), ix = i - n, th = 2 + Math.round(7 * Math.pow(u, 0.6));
      const yo = Math.round(Math.sin(u * 8 - ph) * amp * (0.4 + 0.6 * (1 - u))), top = yo - Math.floor(th / 2);
      P(ix, top - 1, 1, th + 2, "#14240f");                    // viền tối cho nổi trên nền nước
      P(ix, top, 1, th, i % 6 < 3 ? body : dark);
      if (th > 2 && i % 3 === 0) P(ix, top, 1, 1, gold);        // vảy vàng trên lưng
      if (th > 2) P(ix, top + th - 1, 1, 1, belly);              // bụng sáng
      if (i === n - 1) hy = yo;
    }
    // đầu 9×6 ô, mắt đỏ, vương miện vàng 3 chóp, lưỡi chẻ thè ra
    P(0, hy - 6, 13, 11, "#14240f"); P(0, hy - 5, 12, 9, body); P(1, hy - 5, 10, 2, dark); P(0, hy + 2, 12, 2, belly);
    P(7, hy - 3, 3, 3, "#ff2a2a"); P(9, hy - 3, 1, 1, "#000");
    for (const [cx, hh] of [[1, 3], [4, 5], [7, 3]]) P(cx, hy - 6 - hh, 2, hh, gold);
    P(1, hy - 6, 8, 1, gold);
    const fl = Math.sin(tick / (chase ? 3 : 8)) > 0 ? 4 : 1;
    P(12, hy, fl, 1, "#e0324a"); if (fl > 1) { P(12 + fl, hy - 1, 1, 1, "#e0324a"); P(12 + fl, hy + 1, 1, 1, "#e0324a"); }
    c.restore(); c.save(); c.globalAlpha = Math.max(0, Math.min(1, k));
    txt(chase ? "Mãng Xà Vương đang đuổi!" : "Mãng Xà Vương", x + dir * 0.4 * s, y - 2.0 * s, { align: "center", color: chase ? "#ffb4a8" : "#fff" });
    c.restore();
  }
  function serpents(sx, sy, s, list, tick) {
    if (tick < lastTick) seen.clear();  // sang pha/ngày mới
    lastTick = tick;
    const ids = new Set(list.map((m) => m.id));
    list.forEach((m) => {
      let r = seen.get(m.id);
      if (!r || r.gone != null) { r = { born: tick, gone: null, pos: m.pos }; seen.set(m.id, r); }
      r.pos = m.pos; r.state = m.state; r.vel = m.vel;
      if (m.vel && Math.abs(m.vel[0]) > 1e-4) r.dir = m.vel[0] > 0 ? 1 : -1;  // đầu quay theo hướng bơi; đứng yên thì giữ hướng cũ
    });
    seen.forEach((r, id) => {
      if (!ids.has(id) && r.gone == null) r.gone = tick;
      if (r.gone != null && tick - r.gone >= FADE) { seen.delete(id); return; }
      const m = { id, pos: r.pos, state: r.state, vel: r.vel, dir: r.dir };
      if (r.gone != null) serpent(sx, sy, s, m, tick, 1 - (tick - r.gone) / FADE, true);
      else serpent(sx, sy, s, m, tick, Math.min(1, (tick - r.born) / FADE), false);
    });
  }
  const bottomOf = (sel) => { const e = document.querySelector(sel); return e && e.offsetParent ? e.getBoundingClientRect().bottom : 0; };

  function frame() {
    requestAnimationFrame(frame);
    const [w, h] = fit();
    const cr = typeof snap !== "undefined" && snap ? snap.creative : null;
    if (cr && cr.enabled && !(cr.active && (snap.phase || snap.mode) === "gather" && !snap.ui?.screen)) {
      // vừa ngất -> sim sang quán ngay: vẫn cho thấy kết quả xúc xắc cá Ông thêm ~8 giây (trước đây bị mất)
      const dice = cr.messages.filter((m) => m.text.startsWith("Xúc xắc") && snap.tick - m.tick < 480).slice(-1);
      dice.forEach((m) => { c.font = "700 20px " + FONT; const pw = c.measureText(m.text).width + 40;
        panel(w / 2 - pw / 2, 74, pw, 44, "#ffd54f"); txt(m.text, w / 2, 103, { align: "center", color: "#fff3b0", plain: true }); });
      return;
    }
    if (!cr) return;
    const meta = snap.meta || {}, b = meta.bounds || { x: [0, 100], d: [0, 30] };
    const X = b.x[1], D = b.d[1], SKY = 6;
    const top = snap.mode === "day" ? 112 : 64, bottom = 68;
    let s = Math.max(1, Math.min((w - 20) / (X + 4), (h - top - bottom) / (D + SKY + 1)));
    const ox = (w - s * (X + 4)) / 2 + 2 * s, oy = top + SKY * s;
    let sx = (x) => ox + x * s, sy = (d) => oy + d * s;
    const gv = window.gatherView;  // lớp pixel công bố toạ độ thì dùng chung, tránh vẽ lệch
    if (gv) { sx = gv.sx; sy = gv.sy; s = gv.s; }
    cr.shrines.forEach((sh) => shrine(sx, sy, s, sh, sh.id === "ca_ong", snap.tick));
    serpents(sx, sy, s, cr.serpents, snap.tick);
    const p = snap.player;
    if (cr.coil && p) {  // chuỗi mũi tên trên đầu nhân vật
      const k = cr.coil, n = k.chain.length, gap = 40, x0 = sx(p.pos[0]) - ((n - 1) * gap) / 2, y0 = Math.max(top + 70, sy(p.pos[1]) - 3.4 * s - 50);
      const msg = "Bị quấn! Gõ đúng chuỗi mũi tên"; c.font = "700 18px " + FONT;
      const pw = Math.max((n - 1) * gap + 56, c.measureText(msg).width + 28), cxm = sx(p.pos[0]);
      panel(cxm - pw / 2, y0 - 30, pw, 100, "#4fc3f7");
      k.chain.forEach((d, i) => arrow(x0 + i * gap, y0, d, 15, i < k.index ? "#7ddc8a" : i === k.index ? "#ffd54f" : "#cfd8dc", "#10242f"));
      c.fillStyle = "rgba(255,255,255,.25)"; c.fillRect(x0 - 18, y0 + 24, (n - 1) * gap + 36, 8);
      c.fillStyle = "#ef7a5a"; c.fillRect(x0 - 18, y0 + 24, ((n - 1) * gap + 36) * Math.max(0, k.time_left / k.time_total), 8);
      txt(msg, sx(p.pos[0]), y0 + 58, { align: "center", plain: true });
    }
    // ô buff (trái): dưới dòng cảnh báo #warnings và HUD, không chồng nút tương phản (phải) hay HUD độ tươi (phải dưới)
    const by = Math.max(top + 56, bottomOf("#warnings"), bottomOf(".hud"), bottomOf(".day-hud")) + 10;
    cr.buffs.forEach((bf, i) => {
      const bwid = 252, x = 14 + i * (bwid + 8), y = by;
      panel(x, y, bwid, 54, bf.id === "ba_thuy" ? "#4fc3f7" : "#ffd54f");
      if (bf.id === "ba_thuy") {  // sóng nước + mũi tên tăng tốc
        c.strokeStyle = "#4fc3f7"; c.lineWidth = 3; c.beginPath(); c.moveTo(x + 8, y + 36); c.quadraticCurveTo(x + 15, y + 22, x + 22, y + 36); c.quadraticCurveTo(x + 29, y + 50, x + 36, y + 36); c.stroke();
        arrow(x + 23, y + 16, "right", 8, "#4fc3f7", "#4fc3f7");
      } else {  // cá Ông: dáng cá voi
        c.fillStyle = "#6fb1d8"; c.beginPath(); c.ellipse(x + 24, y + 27, 16, 9, 0, 0, 7); c.fill();
        c.beginPath(); c.moveTo(x + 38, y + 27); c.lineTo(x + 47, y + 16); c.lineTo(x + 47, y + 38); c.fill();
      }
      txt(bf.name, x + 54, y + 22, { plain: true });
      txt(bf.left_ticks == null ? "chờ hồi sinh" : "còn " + Math.ceil(bf.left_ticks / 60) + "s", x + 54, y + 45, { color: "#ffd54f", plain: true });
    });
    // thông điệp gần đây
    cr.messages.filter((m) => snap.tick - m.tick < 360).slice(-3).forEach((m, i) => {
      txt(m.text, w / 2, oy + 48 + i * 32, { align: "center", color: "#fff3b0" });
    });
  }
  requestAnimationFrame(frame);
})();
