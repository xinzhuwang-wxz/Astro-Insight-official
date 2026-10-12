"use client";
import { useEffect, useRef } from "react";

export function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    let raf = 0;
    let frame = 0;

    const dpr = Math.max(1, window.devicePixelRatio || 1);
    function resize() {
      const { innerWidth: w, innerHeight: h } = window;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener("resize", resize);

    type Star = {
      x: number; y: number; z: number; vz: number; size: number; hue: number; tw: number; tws: number;
    };
    type Meteor = { x: number; y: number; vx: number; vy: number; life: number } | null;
    const layers = [
      { count: 120, speed: 0.006, size: 0.9 },
      { count: 160, speed: 0.012, size: 1.2 },
      { count: 220, speed: 0.02, size: 1.6 },
    ];
    const stars: Star[] = [];
    let meteor: Meteor = null;
    function spawnStars() {
      stars.length = 0;
      const W = window.innerWidth, H = window.innerHeight;
      for (const [i, layer] of layers.entries()) {
        for (let n = 0; n < layer.count; n++) {
          stars.push({
            x: Math.random() * W,
            y: Math.random() * H,
            z: i + 1,
            vz: layer.speed + Math.random() * layer.speed * 0.7,
            size: (Math.random() * 0.8 + 0.3) * layer.size,
            hue: 210 + Math.random() * 60,
            tw: Math.random() * Math.PI * 2,
            tws: 0.01 + Math.random() * 0.02,
          });
        }
      }
    }
    spawnStars();

    function nebulaBackground() {
      const W = canvas.width, H = canvas.height;
      const g = ctx.createRadialGradient(W * 0.7, H * 0.3, 0, W * 0.7, H * 0.3, Math.max(W, H) * 0.8);
      g.addColorStop(0, "rgba(30, 60, 120, 0.35)");
      g.addColorStop(0.4, "rgba(20, 20, 50, 0.25)");
      g.addColorStop(1, "rgba(0, 0, 0, 0.9)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    }

    // --- Perlin noise nebula overlay (offscreen for perf) ---
    const NOISE_SCALE = 0.0025; // lower = larger features
    const NOISE_ALPHA = 0.08; // overall opacity
    const NOISE_UPDATE_EVERY = 4; // frames
    const off = document.createElement("canvas");
    const offCtx = off.getContext("2d", { willReadFrequently: true })!;
    function resizeOff() {
      off.width = Math.max(160, Math.floor(window.innerWidth * 0.25));
      off.height = Math.max(100, Math.floor(window.innerHeight * 0.25));
    }
    resizeOff();

    // Classic Perlin noise
    const p = new Uint8Array(512);
    (function initPerm() {
      const perm = new Uint8Array(256);
      for (let i = 0; i < 256; i++) perm[i] = i;
      for (let i = 255; i > 0; i--) {
        const j = (Math.random() * (i + 1)) | 0;
        [perm[i], perm[j]] = [perm[j], perm[i]];
      }
      for (let i = 0; i < 512; i++) p[i] = perm[i & 255];
    })();
    const fade = (t: number) => t * t * t * (t * (t * 6 - 15) + 10);
    const lerp = (a: number, b: number, t: number) => a + t * (b - a);
    const grad = (hash: number, x: number, y: number) => {
      const h = hash & 3;
      const u = h & 1 ? -x : x;
      const v = h & 2 ? -y : y;
      return u + v;
    };
    function noise2(x: number, y: number) {
      const X = Math.floor(x) & 255;
      const Y = Math.floor(y) & 255;
      x -= Math.floor(x);
      y -= Math.floor(y);
      const u = fade(x);
      const v = fade(y);
      const A = p[X] + Y;
      const B = p[X + 1] + Y;
      return lerp(
        lerp(grad(p[A], x, y), grad(p[B], x - 1, y), u),
        lerp(grad(p[A + 1], x, y - 1), grad(p[B + 1], x - 1, y - 1), u),
        v
      );
    }

    function updateNebula(t: number) {
      // animate via time offset
      const img = offCtx.createImageData(off.width, off.height);
      let i = 0;
      const tOff = t * 0.00012;
      for (let y = 0; y < off.height; y++) {
        for (let x = 0; x < off.width; x++) {
          const nx = x * NOISE_SCALE;
          const ny = y * NOISE_SCALE;
          // fBm: combine octaves
          let n = 0, amp = 1, freq = 1, sumAmp = 0;
          for (let o = 0; o < 3; o++) {
            n += noise2(nx * freq + tOff * 0.6, ny * freq) * amp;
            sumAmp += amp;
            amp *= 0.5;
            freq *= 2;
          }
          n = n / sumAmp; // normalize to ~[-1,1]
          const v = (n + 1) * 0.5; // [0..1]
          // palette between deep purple and azure
          const r = Math.floor(30 + 120 * v);
          const g = Math.floor(40 + 100 * v * 0.9);
          const b = Math.floor(90 + 150 * v);
          img.data[i++] = r;
          img.data[i++] = g;
          img.data[i++] = b;
          img.data[i++] = Math.floor(255 * NOISE_ALPHA);
        }
      }
      offCtx.putImageData(img, 0, 0);
    }

    function maybeSpawnMeteor() {
      if (meteor || Math.random() > 0.006) return;
      const fromTop = Math.random() < 0.5;
      const x = Math.random() * window.innerWidth;
      const y = fromTop ? -50 : window.innerHeight + 50;
      const vx = -4 - Math.random() * 2;
      const vy = fromTop ? 2 + Math.random() * 1.5 : -2 - Math.random() * 1.5;
      meteor = { x, y, vx, vy, life: 1 };
    }

    function drawMeteor() {
      if (!meteor) return;
      meteor.x += meteor.vx;
      meteor.y += meteor.vy;
      meteor.life -= 0.01;
      if (meteor.life <= 0 || meteor.x < -100 || meteor.y > window.innerHeight + 100 || meteor.y < -100) {
        meteor = null;
        return;
      }
      const trail = 120;
      const grd = ctx.createLinearGradient(meteor.x, meteor.y, meteor.x - meteor.vx * trail, meteor.y - meteor.vy * trail);
      grd.addColorStop(0, "rgba(255,255,255,0.9)");
      grd.addColorStop(1, "rgba(120,180,255,0)");
      ctx.strokeStyle = grd;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(meteor.x, meteor.y);
      ctx.lineTo(meteor.x - meteor.vx * trail, meteor.y - meteor.vy * trail);
      ctx.stroke();
    }

    function step() {
      frame++;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // 深空底色
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
  nebulaBackground();
  if (frame % NOISE_UPDATE_EVERY === 0) updateNebula(performance.now());
  // draw scaled nebula noise overlay
  ctx.globalCompositeOperation = "screen";
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(off, 0, 0, canvas.width / dpr, canvas.height / dpr);
  ctx.globalCompositeOperation = "source-over";

      // 星星
      for (const s of stars) {
        s.tw += s.tws; // 闪烁相位
        // 视差纵向漂移 + 轻微斜向
        s.x -= s.vz * 40 * s.z;
        s.y += s.vz * 10 * (s.z * 0.5);
        if (s.x < -10) s.x = window.innerWidth + 10;
        if (s.y > window.innerHeight + 10) s.y = -10;

        const twinkle = 0.7 + 0.3 * Math.sin(s.tw);
        const alpha = Math.min(1, 0.3 + 0.35 * s.z) * twinkle;
        const r = s.size * (0.8 + 0.5 * s.z) * twinkle;

        // 星点
        ctx.beginPath();
        ctx.fillStyle = `hsla(${s.hue}, 80%, ${70 + s.z * 8}%, ${alpha})`;
        ctx.arc(s.x, s.y, r, 0, Math.PI * 2);
        ctx.fill();

        // 星尾（运动模糊）
        ctx.beginPath();
        ctx.strokeStyle = `hsla(${s.hue}, 80%, 70%, ${alpha * 0.35})`;
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(s.x + s.vz * 150 * s.z, s.y - s.vz * 60 * s.z);
        ctx.stroke();
      }

      // 偶发流星
      maybeSpawnMeteor();
      drawMeteor();

      raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
  // cleanup
  off.width = off.height = 0;
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 -z-10 pointer-events-none" aria-hidden />;
}
