/* NEURAL NETWORK BACKGROUND */
const canvas = document.createElement("canvas");
canvas.id = "networkCanvas";
document.body.appendChild(canvas);
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
for (let i = 0; i < 80; i++) {
  particles.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * 1,
    vy: (Math.random() - 0.5) * 1
  });
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
    if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#00eaff";
    ctx.fill();
  });

  for (let i = 0; i < particles.length; i++) {
    for (let j = i; j < particles.length; j++) {
      let dx = particles[i].x - particles[j].x;
      let dy = particles[i].y - particles[j].y;
      let dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 120) {
        ctx.strokeStyle = "rgba(0,255,255,0.2)";
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.stroke();
      }
    }
  }
  requestAnimationFrame(animate);
}
animate();

/* PREDICTION METER */
document.addEventListener("DOMContentLoaded", () => {
  const meter = document.querySelector(".meter-fill");
  if (meter) {
    const width = meter.getAttribute("data-value");
    setTimeout(() => {
      meter.style.width = width + "%";
    }, 300);
  }
});

/* 3D CARD TILT EFFECT */
document.querySelectorAll(".card3d").forEach(card => {
  card.addEventListener("mousemove", e => {
    let rect = card.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;
    let centerX = rect.width / 2;
    let centerY = rect.height / 2;
    let rotateX = -(y - centerY) / 10;
    let rotateY = (x - centerX) / 10;
    card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "rotateX(0) rotateY(0)";
  });
});

/* 3D AI BRAIN (Three.js) */
if (document.getElementById("brain3d")) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById("brain3d"),
    alpha: true
  });
  renderer.setSize(400, 250);
  camera.position.z = 5;

  const geometry = new THREE.IcosahedronGeometry(2, 2);
  const material = new THREE.MeshStandardMaterial({
    color: 0x00eaff,
    wireframe: true,
    emissive: 0x00eaff,
    emissiveIntensity: 0.5
  });
  const brain = new THREE.Mesh(geometry, material);
  scene.add(brain);

  const light = new THREE.PointLight(0xffffff, 1);
  light.position.set(10, 10, 10);
  scene.add(light);

  function animate() {
    requestAnimationFrame(animate);
    brain.rotation.x += 0.005;
    brain.rotation.y += 0.01;
    renderer.render(scene, camera);
  }
  animate();
}