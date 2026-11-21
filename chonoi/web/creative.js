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
  function txt(s, x, y, o = {}) {
    c.font = (o.size || 13) + "px system-ui, sans-serif";
    c.fillStyle = o.color || "#fff"; c.textAlign = o.align || "left"; c.textBaseline = o.base || "alphabetic";
    c.fillText(s, x, y);
  }
  function arrow(cx, cy, dir, size, fill, stroke) {
    const [dx, dy] = ARROW[dir];
    c.save(); c.translate(cx, cy); c.rotate(Math.atan2(dy, dx));
    c.fillStyle = fill; c.strokeStyle = stroke; c.lineWidth = 2;
    c.beginPath(); c.moveTo(size, 0); c.lineTo(-size * 0.2, -size * 0.8); c.lineTo(-size * 0.2, -size * 0.3);
    c.lineTo(-size, -size * 0.3); c.lineTo(-size, size * 0.3); c.lineTo(-size * 0.2, size * 0.3); c.lineTo(-size * 0.2, size * 0.8);
    c.closePath(); c.fill(); c.stroke(); c.restore();
  }
  function shrine(sx, sy, s, sh, ongFish) {
    const x = sx(sh.x), y = sy(0);
    c.fillStyle = "#6b4a2f"; c.fillRect(x - 0.9 * s, y - 1.4 * s, 1.8 * s, 1.4 * s);
    c.fillStyle = ongFish ? "#2b6f8f" : "#a63a2f";
    c.beginPath(); c.moveTo(x - 1.5 * s, y - 1.4 * s); c.lineTo(x, y - 2.6 * s); c.lineTo(x + 1.5 * s, y - 1.4 * s); c.closePath(); c.fill();
    c.fillStyle = "#1c1209"; c.fillRect(x - 0.3 * s, y - 0.9 * s, 0.6 * s, 0.9 * s);
    // nén hương: đỏ + khói khi đã thắp
    c.strokeStyle = "#8a5a2b"; c.lineWidth = 2; c.beginPath(); c.moveTo(x + 1.2 * s, y); c.lineTo(x + 1.2 * s, y - 1.1 * s); c.stroke();
    if (sh.lit) {
      c.fillStyle = "#ff5a3c"; c.beginPath(); c.arc(x + 1.2 * s, y - 1.15 * s, 2.5, 0, 7); c.fill();
      c.strokeStyle = "rgba(255,255,255,.55)"; c.lineWidth = 1.5; c.beginPath();
      for (let i = 0; i < 6; i++) c.lineTo(x + 1.2 * s + Math.sin(performance.now() / 400 + i) * 3, y - 1.2 * s - i * 5);
      c.stroke();
    }
    txt(sh.name, x, y - 2.9 * s, { size: 11, align: "center", color: "#4a2b17" });
    if (!sh.lit && sh.progress > 0) {  // vòng tiến độ thắp hương
      c.strokeStyle = "#ffd54f"; c.lineWidth = 4; c.beginPath();
      c.arc(x, y - 0.7 * s, 1.9 * s, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * sh.progress) / sh.stand_ticks); c.stroke();
      txt("Đang thắp hương… đứng yên", x, y + 1.4 * s, { size: 11, align: "center", color: "#ffd54f" });
    }
  }
  function serpent(sx, sy, s, m, tick) {
    const x = sx(m.pos[0]), y = sy(m.pos[1]);
    c.strokeStyle = "#2f5d34"; c.lineWidth = 0.7 * s; c.lineCap = "round"; c.beginPath();
    for (let i = -4; i <= 4; i++) c.lineTo(x + i * 0.45 * s, y + Math.sin(i + tick / 20) * 0.5 * s);
    c.stroke();
    c.strokeStyle = "#d9c06a"; c.lineWidth = 2; c.setLineDash([4, 6]); c.stroke(); c.setLineDash([]);
    c.fillStyle = "#e8d77a"; c.beginPath(); c.arc(x + 1.9 * s, y + Math.sin(4 + tick / 20) * 0.5 * s - 0.1 * s, 0.14 * s, 0, 7); c.fill();
    txt("Mãng Xà Vương", x, y - 1 * s, { size: 12, align: "center" });
  }

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
    cr.shrines.forEach((sh) => shrine(sx, sy, s, sh, sh.id === "ca_ong"));
    cr.serpents.forEach((m) => serpent(sx, sy, s, m, snap.tick));
    const p = snap.player;
    if (cr.coil && p) {  // chuỗi mũi tên trên đầu nhân vật
      const k = cr.coil, n = k.chain.length, gap = 30, x0 = sx(p.pos[0]) - ((n - 1) * gap) / 2, y0 = Math.max(top + 24, sy(p.pos[1]) - 1.6 * s - 20);
      c.fillStyle = "rgba(8,20,30,.7)"; c.fillRect(x0 - 20, y0 - 22, (n - 1) * gap + 40, 62);
      k.chain.forEach((d, i) => arrow(x0 + i * gap, y0, d, 11, i < k.index ? "#7ddc8a" : i === k.index ? "#ffd54f" : "#cfd8dc", "#10242f"));
      c.fillStyle = "rgba(255,255,255,.25)"; c.fillRect(x0 - 14, y0 + 20, (n - 1) * gap + 28, 6);
      c.fillStyle = "#ef7a5a"; c.fillRect(x0 - 14, y0 + 20, ((n - 1) * gap + 28) * Math.max(0, k.time_left / k.time_total), 6);
      txt("Bị quấn! Gõ đúng chuỗi mũi tên", sx(p.pos[0]), y0 + 38, { size: 11, align: "center" });
    }
    // biểu tượng buff + thời gian còn lại (trái, dưới HUD)
    cr.buffs.forEach((bf, i) => {
      const x = 14 + i * 142, y = top + 56;  // dưới dòng cảnh báo
      c.fillStyle = "rgba(8,20,30,.72)"; c.fillRect(x, y, 134, 34);
      c.strokeStyle = bf.id === "ba_thuy" ? "#4fc3f7" : "#ffd54f"; c.lineWidth = 2; c.strokeRect(x + 1, y + 1, 132, 32);
      if (bf.id === "ba_thuy") {  // sóng nước + mũi tên tăng tốc
        c.strokeStyle = "#4fc3f7"; c.lineWidth = 2; c.beginPath(); c.moveTo(x + 6, y + 22); c.quadraticCurveTo(x + 11, y + 12, x + 16, y + 22); c.quadraticCurveTo(x + 21, y + 32, x + 26, y + 22); c.stroke();
        arrow(x + 17, y + 10, "right", 6, "#4fc3f7", "#4fc3f7");
      } else {  // cá Ông: dáng cá voi
        c.fillStyle = "#6fb1d8"; c.beginPath(); c.ellipse(x + 17, y + 17, 11, 6, 0, 0, 7); c.fill();
        c.beginPath(); c.moveTo(x + 27, y + 17); c.lineTo(x + 33, y + 10); c.lineTo(x + 33, y + 24); c.fill();
      }
      txt(bf.name, x + 38, y + 14, { size: 11 });
      txt(bf.left_ticks == null ? "chờ hồi sinh" : "còn " + Math.ceil(bf.left_ticks / 60) + "s", x + 38, y + 28, { size: 12, color: "#ffd54f" });
    });
    // thông điệp gần đây
    cr.messages.filter((m) => snap.tick - m.tick < 360).slice(-3).forEach((m, i, a) => {
      txt(m.text, w / 2, oy + 44 + i * 18, { size: 14, align: "center", color: "#fff3b0" });
    });
  }
  requestAnimationFrame(frame);
})();
