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
  function shrine(sx, sy, s, sh, ongFish, tick) {
    const x = sx(sh.x), y = sy(0);
    // tỉ lệ: người cao ~1,7 đơn vị; thân miếu 2,4, mái lên tới 4,0 (cao hơn người)
    const bw = 3.6 * s, bh = 2.4 * s, roofTop = 4.0 * s;
    c.fillStyle = "#3b2a1a"; c.fillRect(x - bw / 2 - 0.3 * s, y - 0.25 * s, bw + 0.6 * s, 0.25 * s);  // bệ
    c.fillStyle = "#6b4a2f"; c.fillRect(x - bw / 2, y - bh, bw, bh - 0.25 * s);
    c.fillStyle = "#8a6240"; c.fillRect(x - bw / 2, y - bh, 0.3 * s, bh - 0.25 * s); c.fillRect(x + bw / 2 - 0.3 * s, y - bh, 0.3 * s, bh - 0.25 * s);
    c.fillStyle = ongFish ? "#2b6f8f" : "#a63a2f";
    c.beginPath(); c.moveTo(x - bw / 2 - 0.7 * s, y - bh); c.lineTo(x - 0.5 * s, y - roofTop); c.lineTo(x + 0.5 * s, y - roofTop); c.lineTo(x + bw / 2 + 0.7 * s, y - bh); c.closePath(); c.fill();
    c.strokeStyle = "#f5de95"; c.lineWidth = 2; c.stroke();
    const dw = 1.2 * s, dh = 1.45 * s, dx = x - dw / 2, dy = y - 0.25 * s - dh;
    if (sh.lit) {  // đã thắp: ánh nến vàng ấm trong cửa, quầng sáng, ngọn nến lung linh theo tick
      const fl = 0.85 + 0.15 * Math.sin(tick / 7) + 0.05 * Math.sin(tick / 3);
      const g = c.createRadialGradient(x, y - 0.9 * s, 0.1 * s, x, y - 0.9 * s, 2.6 * s * fl);
      g.addColorStop(0, "rgba(255,200,90,.55)"); g.addColorStop(1, "rgba(255,170,60,0)");
      c.fillStyle = g; c.fillRect(x - 2.8 * s, y - 3.5 * s, 5.6 * s, 3.5 * s);
      c.fillStyle = "#ffcf6b"; c.fillRect(dx, dy, dw, dh);
      c.fillStyle = "#ff9d3c"; c.fillRect(dx + 0.15 * s, dy + 0.45 * s, dw - 0.3 * s, dh - 0.45 * s);
      c.fillStyle = "#fff4c4"; c.fillRect(x - 0.08 * s, y - 0.25 * s - 0.55 * s, 0.16 * s, 0.4 * s);  // thân nến
      c.beginPath(); c.ellipse(x, y - 0.25 * s - 0.72 * s, 0.1 * s * fl, 0.22 * s * fl, 0, 0, 7); c.fillStyle = "#ffe36b"; c.fill();
      c.strokeStyle = "#5a2a10"; c.lineWidth = 2; c.strokeRect(dx, dy, dw, dh);
    } else { c.fillStyle = "#1c1209"; c.fillRect(dx, dy, dw, dh); }
    // bát hương bên phải: chưa thắp = ba nén nâu không khói; đã thắp = ba nén đỏ đầu cháy + khói uốn lượn
    const hx = x + bw / 2 + 0.9 * s, bt = y - 0.45 * s;
    c.fillStyle = "#7a5a32"; c.beginPath(); c.moveTo(hx - 0.55 * s, bt); c.lineTo(hx + 0.55 * s, bt); c.lineTo(hx + 0.4 * s, y); c.lineTo(hx - 0.4 * s, y); c.closePath(); c.fill();
    c.strokeStyle = "#f5de95"; c.lineWidth = 2; c.stroke();
    const tops = [];
    [-0.28, 0, 0.28].forEach((o, n) => {
      const sx0 = hx + o * s, tp = bt - (1.5 + (n === 1 ? 0.2 : 0)) * s;
      c.strokeStyle = sh.lit ? "#c8301f" : "#8a5a2b"; c.lineWidth = 3; c.lineCap = "round";
      c.beginPath(); c.moveTo(sx0, bt); c.lineTo(sx0, tp); c.stroke(); c.lineCap = "butt";
      tops.push([sx0, tp]);
    });
    if (sh.lit) {
      tops.forEach(([tx, ty], n) => {  // đầu nén cháy đỏ
        c.fillStyle = "#ff7a3c"; c.beginPath(); c.arc(tx, ty, 4.5, 0, 7); c.fill();
        c.fillStyle = "#fff0a0"; c.beginPath(); c.arc(tx, ty, 2, 0, 7); c.fill();
        // vài cuộn khói xám trắng: mỗi cuộn bay lên rồi mờ dần, uốn lượn theo sin
        for (let k = 0; k < 4; k++) {
          const ph = ((tick / 150 + k / 4 + n * 0.31) % 1), H = 4.5 * s;
          const px = tx + Math.sin(ph * 9 + n * 2) * (0.25 + ph * 0.5) * s, py = ty - 6 - ph * H, r = 7 + ph * 16;
          c.fillStyle = "rgba(236,238,240," + (0.8 * (1 - ph)).toFixed(3) + ")";
          c.beginPath(); c.arc(px, py, r, 0, 7); c.fill();
        }
      });
    }
    txt(sh.name, x, y - roofTop - 8, { align: "center", color: ongFish ? "#bfe6ff" : "#ffe9b0" });
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
    // thân dài ~7 m, thân dày dần về phía đầu; uốn sin chạy dọc thân theo tick; đầu quay theo hướng bơi (m.dir)
    const N = 34, L = 7 * s, chase = m.state === "chase", dir = m.dir || 1;
    const amp = (chase ? 0.55 : 0.4) * s, spd = chase ? 9 : 16, ph = tick / spd;
    const seg = [];
    for (let i = 0; i < N; i++) {  // i = 0 là đuôi, N-1 là đầu
      const u = i / (N - 1), px = (u - 1) * L, py = Math.sin(u * 9 - ph) * amp * (0.35 + 0.65 * (1 - u));
      seg.push([px, py, (0.12 + 0.88 * Math.pow(Math.sin(Math.min(1, u * 1.15) * Math.PI / 2), 0.7)) * 0.5 * s]);
    }
    c.save(); c.translate(x, y); c.scale(dir, 1);
    c.fillStyle = "rgba(190,235,150,.45)"; seg.forEach(([px, py, r]) => { c.beginPath(); c.arc(px, py, r + 3, 0, 7); c.fill(); });  // viền sáng cho nổi trên nền nước tối
    seg.forEach(([px, py, r], i) => {
      c.fillStyle = i % 4 < 2 ? "#4f8a45" : "#6aa24f"; c.beginPath(); c.arc(px, py, r, 0, 7); c.fill();
      c.fillStyle = "#c9a24a"; c.beginPath(); c.ellipse(px, py - r * 0.35, r * 0.28, r * 0.5, 0, 0, 7); c.fill();  // vảy vàng đồng trên lưng
      if (i % 4 === 0) { c.fillStyle = "#e9d58a"; c.beginPath(); c.arc(px, py + r * 0.45, r * 0.3, 0, 7); c.fill(); }  // bụng sáng
    });
    c.strokeStyle = "#1f3a22"; c.lineWidth = 2; c.beginPath(); seg.forEach(([px, py, r]) => c.lineTo(px, py - r)); c.stroke();
    const [hx, hy, hr] = seg[N - 1];
    c.fillStyle = "#5f9a4a"; c.beginPath(); c.ellipse(hx + 0.5 * s, hy, 0.95 * s, 0.62 * s, 0, 0, 7); c.fill();  // đầu
    c.strokeStyle = "#1f3a22"; c.lineWidth = 2; c.stroke();
    c.fillStyle = "#f2c94c";  // mào/vương miện nhỏ
    c.beginPath();
    c.moveTo(hx - 0.2 * s, hy - 0.5 * s);
    [[-0.3, -1.25], [0.15, -0.95], [0.55, -1.4], [0.95, -0.9], [1.1, -0.45]].forEach(([qx, qy]) => c.lineTo(hx + qx * s, hy + qy * s * 0.9));
    c.lineTo(hx + 0.9 * s, hy - 0.3 * s); c.closePath(); c.fill(); c.strokeStyle = "#8a6a10"; c.lineWidth = 1.5; c.stroke();
    c.fillStyle = "#ff2a2a"; c.beginPath(); c.arc(hx + 0.75 * s, hy - 0.17 * s, 0.17 * s, 0, 7); c.fill();  // mắt đỏ
    c.fillStyle = "#000"; c.beginPath(); c.arc(hx + 0.8 * s, hy - 0.17 * s, 0.07 * s, 0, 7); c.fill();
    const fl = Math.sin(tick / (chase ? 3 : 8)) > 0 ? 1 : 0.35, tx0 = hx + 1.4 * s;  // lưỡi chẻ thè ra
    c.strokeStyle = "#e0324a"; c.lineWidth = 2.5; c.beginPath(); c.moveTo(tx0, hy + 0.1 * s); c.lineTo(tx0 + 0.7 * s * fl, hy + 0.1 * s);
    c.moveTo(tx0 + 0.7 * s * fl, hy + 0.1 * s); c.lineTo(tx0 + 1.0 * s * fl, hy - 0.05 * s);
    c.moveTo(tx0 + 0.7 * s * fl, hy + 0.1 * s); c.lineTo(tx0 + 1.0 * s * fl, hy + 0.25 * s); c.stroke();
    c.restore();
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
    if (!cr || !cr.active || (snap.phase || snap.mode) !== "gather" || snap.ui?.screen) return;
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
