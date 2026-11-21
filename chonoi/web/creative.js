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
    c.fillStyle = "#1c1209"; c.fillRect(x - 0.6 * s, y - 1.7 * s, 1.2 * s, 1.45 * s);  // cửa
    // nén hương ở bên phải: đỏ + khói khi đã thắp
    const hx = x + bw / 2 + 0.9 * s;
    c.strokeStyle = "#8a5a2b"; c.lineWidth = 3; c.beginPath(); c.moveTo(hx, y); c.lineTo(hx, y - 1.5 * s); c.stroke();
    if (sh.lit) {
      c.fillStyle = "#ff5a3c"; c.beginPath(); c.arc(hx, y - 1.55 * s, 3.5, 0, 7); c.fill();
      c.strokeStyle = "rgba(255,255,255,.6)"; c.lineWidth = 2; c.beginPath();
      for (let i = 0; i < 6; i++) c.lineTo(hx + Math.sin(tick / 25 + i) * 4, y - 1.7 * s - i * 6);
      c.stroke();
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
    c.strokeStyle = "#2f5d34"; c.lineWidth = 0.7 * s; c.lineCap = "round"; c.beginPath();
    for (let i = -4; i <= 4; i++) c.lineTo(x + i * 0.45 * s, y + Math.sin(i + tick / 20) * 0.5 * s);
    c.stroke();
    c.strokeStyle = "#d9c06a"; c.lineWidth = 2; c.setLineDash([4, 6]); c.stroke(); c.setLineDash([]);
    c.fillStyle = "#e8d77a"; c.beginPath(); c.arc(x + 1.9 * s, y + Math.sin(4 + tick / 20) * 0.5 * s - 0.1 * s, 0.14 * s, 0, 7); c.fill();
    txt("Mãng Xà Vương", x, y - 1 * s - 6, { align: "center" });
    c.restore();
  }
  function serpents(sx, sy, s, list, tick) {
    if (tick < lastTick) seen.clear();  // sang pha/ngày mới
    lastTick = tick;
    const ids = new Set(list.map((m) => m.id));
    list.forEach((m) => {
      let r = seen.get(m.id);
      if (!r || r.gone != null) { r = { born: tick, gone: null, pos: m.pos }; seen.set(m.id, r); }
      r.pos = m.pos;
    });
    seen.forEach((r, id) => {
      if (!ids.has(id) && r.gone == null) r.gone = tick;
      if (r.gone != null && tick - r.gone >= FADE) { seen.delete(id); return; }
      const m = { id, pos: r.pos };
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
      const k = cr.coil, n = k.chain.length, gap = 40, x0 = sx(p.pos[0]) - ((n - 1) * gap) / 2, y0 = Math.max(top + 70, sy(p.pos[1]) - 1.6 * s - 40);
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
