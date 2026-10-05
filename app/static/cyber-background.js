/**
 * CareerMatch Agent v2.0 - 3D Perspective Digital Cyber Grid & Neural Constellation
 * High-performance 3D perspective wireframe horizon, interactive mouse tilt,
 * floating glowing data nodes, and sweeping radar wavefronts.
 */
(function () {
  'use strict';

  const canvas = document.createElement('canvas');
  canvas.id = 'cyber-bg-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '-1';
  canvas.style.opacity = '1';
  document.body.prepend(canvas);

  const ctx = canvas.getContext('2d');
  let width, height, dpr;
  let isRunning = true;
  let time = 0;

  // Mouse tilt physics with smooth lerp
  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0, active: false };

  // Floating 3D Starfield / Data Nodes
  let starNodes = [];
  const NUM_STARS = 65;

  // Wavefront pulses
  const wavePulses = [];

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
    initStarNodes();
  }

  function initStarNodes() {
    starNodes = [];
    for (let i = 0; i < NUM_STARS; i++) {
      starNodes.push({
        x: (Math.random() - 0.5) * width * 1.5,
        y: Math.random() * height * 0.85,
        z: Math.random() * 800 + 100,
        vz: Math.random() * 0.6 + 0.3,
        radius: Math.random() * 2.0 + 1.0,
        isViolet: Math.random() > 0.65,
        phase: Math.random() * Math.PI * 2
      });
    }
  }

  // Add periodic radar wavefront expansion
  setInterval(() => {
    if (isRunning && wavePulses.length < 3) {
      wavePulses.push({
        radius: 0,
        maxRadius: Math.max(width, height) * 0.8,
        speed: 2.2,
        alpha: 0.4
      });
    }
  }, 3500);

  function update() {
    time += 0.015;

    // Smoothly interpolate mouse tilt
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    // Update star nodes
    for (let i = 0; i < starNodes.length; i++) {
      const s = starNodes[i];
      s.z -= s.vz;
      if (s.z <= 20) {
        s.z = 800;
        s.x = (Math.random() - 0.5) * width * 1.5;
        s.y = Math.random() * height * 0.85;
      }
      s.phase += 0.025;
    }

    // Update wavefront pulses
    for (let i = wavePulses.length - 1; i >= 0; i--) {
      const p = wavePulses[i];
      p.radius += p.speed;
      p.alpha = Math.max(0, 0.4 * (1 - p.radius / p.maxRadius));
      if (p.radius >= p.maxRadius) {
        wavePulses.splice(i, 1);
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    // Deep cosmic gradient
    const bgGrad = ctx.createRadialGradient(
      width * 0.5 + mouse.x * 40,
      height * 0.35 + mouse.y * 30,
      50,
      width * 0.5,
      height * 0.5,
      Math.max(width, height) * 0.85
    );
    bgGrad.addColorStop(0, '#0a1329');
    bgGrad.addColorStop(0.45, '#070c1a');
    bgGrad.addColorStop(1, '#040711');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // --- 3D PERSPECTIVE HORIZON DIGITAL GRID ---
    const horizonY = height * 0.62 + mouse.y * 25;
    const vanishX = width * 0.5 + mouse.x * 60;
    const gridDepth = 18;
    const gridLines = 26;
    const gridSpacing = width * 1.6 / gridLines;

    // Horizon glowing neon line & atmosphere
    const horizonGrad = ctx.createLinearGradient(0, horizonY - 60, 0, horizonY + 30);
    horizonGrad.addColorStop(0, 'rgba(0, 240, 255, 0)');
    horizonGrad.addColorStop(0.65, 'rgba(0, 240, 255, 0.08)');
    horizonGrad.addColorStop(1, 'rgba(139, 92, 246, 0.12)');
    ctx.fillStyle = horizonGrad;
    ctx.fillRect(0, horizonY - 60, width, 90);

    ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, horizonY);
    ctx.lineTo(width, horizonY);
    ctx.stroke();

    // Perspective perspective depth lines (moving towards viewer)
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, horizonY, width, height - horizonY);
    ctx.clip();

    // Longitudinal grid lines radiating from vanishing point
    ctx.lineWidth = 0.9;
    for (let i = -gridLines; i <= gridLines * 2; i++) {
      const bottomX = (i - gridLines / 2) * gridSpacing + (width * 0.5);
      const alpha = Math.max(0.04, 0.22 * (1 - Math.abs(bottomX - width * 0.5) / (width * 1.2)));
      ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
      ctx.beginPath();
      ctx.moveTo(vanishX, horizonY);
      ctx.lineTo(bottomX, height + 100);
      ctx.stroke();
    }

    // Lateral perspective lines moving forward smoothly
    const speedOffset = (time * 30) % 1;
    for (let i = 0; i < gridDepth; i++) {
      const factor = (i + speedOffset) / gridDepth;
      // Exponential perspective curve for realistic depth
      const pY = horizonY + Math.pow(factor, 2.3) * (height - horizonY + 60);
      const alpha = Math.min(0.35, Math.pow(factor, 1.8) * 0.45);

      if (pY >= horizonY && pY <= height) {
        ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
        ctx.lineWidth = 0.8 + factor * 0.8;
        ctx.beginPath();
        ctx.moveTo(0, pY);
        ctx.lineTo(width, pY);
        ctx.stroke();
      }
    }
    ctx.restore();

    // --- EXPANDING RADAR WAVEFRONTS ---
    for (let i = 0; i < wavePulses.length; i++) {
      const p = wavePulses[i];
      ctx.beginPath();
      ctx.ellipse(vanishX, horizonY, p.radius, p.radius * 0.35, 0, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0, 240, 255, ${p.alpha})`;
      ctx.lineWidth = 1.4;
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // --- FLOATING 3D STAR DATA NODES & LASER INTERSECTIONS ---
    const activeNodes = [];
    for (let i = 0; i < starNodes.length; i++) {
      const s = starNodes[i];
      const scale = 400 / s.z;
      const screenX = vanishX + s.x * scale;
      const screenY = (height * 0.35) + (s.y - height * 0.35) * scale + mouse.y * 15;

      if (screenX >= -50 && screenX <= width + 50 && screenY >= -50 && screenY <= horizonY + 40) {
        const pulse = 0.5 + 0.5 * Math.sin(s.phase);
        const nodeAlpha = Math.min(0.9, (1 - s.z / 900) * (0.4 + pulse * 0.4));
        activeNodes.push({ x: screenX, y: screenY, alpha: nodeAlpha, isViolet: s.isViolet, r: s.radius * scale });

        // Draw node
        ctx.beginPath();
        ctx.arc(screenX, screenY, Math.max(0.8, s.radius * scale), 0, Math.PI * 2);
        ctx.fillStyle = s.isViolet
          ? `rgba(168, 85, 247, ${nodeAlpha})`
          : `rgba(0, 240, 255, ${nodeAlpha})`;
        ctx.shadowColor = s.isViolet ? '#a855f7' : '#00f0ff';
        ctx.shadowBlur = 8 * scale;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    // Connect close star nodes with high-tech laser filaments
    for (let i = 0; i < activeNodes.length; i++) {
      const n1 = activeNodes[i];
      for (let j = i + 1; j < activeNodes.length; j++) {
        const n2 = activeNodes[j];
        const dx = n1.x - n2.x;
        const dy = n1.y - n2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 110) {
          const lineAlpha = (1 - dist / 110) * Math.min(n1.alpha, n2.alpha) * 0.35;
          ctx.beginPath();
          ctx.strokeStyle = n1.isViolet
            ? `rgba(168, 85, 247, ${lineAlpha})`
            : `rgba(0, 240, 255, ${lineAlpha})`;
          ctx.lineWidth = 0.8;
          ctx.moveTo(n1.x, n1.y);
          ctx.lineTo(n2.x, n2.y);
          ctx.stroke();
        }
      }
    }

    // Gentle ambient mouse aura
    if (mouse.active) {
      const mX = mouse.targetX * width * 0.5 + width * 0.5;
      const mY = mouse.targetY * height * 0.5 + height * 0.5;
      const aura = ctx.createRadialGradient(mX, mY, 0, mX, mY, 200);
      aura.addColorStop(0, 'rgba(0, 240, 255, 0.08)');
      aura.addColorStop(1, 'rgba(0, 240, 255, 0)');
      ctx.fillStyle = aura;
      ctx.fillRect(mX - 200, mY - 200, 400, 400);
    }
  }

  function loop() {
    if (!isRunning) return;
    update();
    draw();
    requestAnimationFrame(loop);
  }

  window.addEventListener('resize', resize);

  window.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX / width - 0.5) * 2;
    mouse.targetY = (e.clientY / height - 0.5) * 2;
    mouse.active = true;
  });

  window.addEventListener('mouseleave', () => {
    mouse.targetX = 0;
    mouse.targetY = 0;
    mouse.active = false;
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      isRunning = false;
    } else {
      isRunning = true;
      requestAnimationFrame(loop);
    }
  });

  resize();
  requestAnimationFrame(loop);
})();
