const socket = io();
let selectedVehicle = null;
let vehicleIPs = {};

const camera = document.getElementById("camera");
const select = document.getElementById("vehicle-select");

socket.on("pi_list", (piList) => {
    console.log("[CLIENT] Neue Pi-Liste empfangen:", piList);
    select.innerHTML = "";
    vehicleIPs = {};
    piList.forEach((pi) => {
        const id = typeof pi === "string" ? pi : pi.id;
        const ip = typeof pi === "string" ? "?" : pi.ip;
        const opt = document.createElement("option");
        opt.value = id;
        opt.textContent = id;
        select.appendChild(opt);
        vehicleIPs[id] = ip;
    });
});

socket.emit("request_pi_list");

function selectVehicle() {
  selectedVehicle = select.value;
  if (!selectedVehicle) return;
  const piIP = vehicleIPs[selectedVehicle];
  camera.src = `/api/stream/${selectedVehicle}`;
  camera.alt = `Kamera-Stream von ${selectedVehicle} (${piIP})`;
  camera.style.display = "block";
}


function sendCommand(command) {
  if (selectedVehicle) {
    socket.emit("command", { pi_id: selectedVehicle, command });
  }
}

function toggleFullscreen() {
  const docEl = document.documentElement;

  if (!document.fullscreenElement && docEl.requestFullscreen) {
    docEl.requestFullscreen().catch(err => {
      alert("Fullscreen nicht möglich: " + err.message);
    });
  } else if (document.exitFullscreen) {
    document.exitFullscreen();
  }
}

socket.on("status_update", (data) => {
  if (data.pi_id !== selectedVehicle) return;

  const level = data.battery;
  ["b1", "b2", "b3"].forEach((id, idx) => {
    document.getElementById(id).classList.toggle("on", idx < level + 1);
  });

  document.getElementById("temp").innerText = `🌡️ ${data.temp}°C`;
  document.getElementById("latency").innerText = `📶 ${data.latency}ms`;
});


// Joystick links (Auto)
const autoJoystick = nipplejs.create({
  zone: document.getElementById("joystick-left"),
  mode: "static",
  position: { top: "50%", left: "50%" },
  color: "yellow",
  size: 100,
  restOpacity: 0.4
});

autoJoystick.on('move', (_, data) => {
  if (!selectedVehicle || !data?.direction) return;

  const dir = data.direction.angle;
  switch (dir) {
    case "up": sendCommand("forward"); break;
    case "down": sendCommand("backward"); break;
    case "left": sendCommand("left"); break;
    case "right": sendCommand("right"); break;
    case "up-left": sendCommand("left"); break;
    case "up-right": sendCommand("right"); break;
    case "down-left": sendCommand("backward_left"); break;
    case "down-right": sendCommand("backward_right"); break;
    default: sendCommand("stop"); break;
  }
});

autoJoystick.on('end', () => {
  sendCommand("stop");
  setTimeout(() => sendCommand("stop"), 200); // doppelt stoppen
});



// Joystick rechts (Kamera)
const camJoystick = nipplejs.create({
  zone: document.getElementById("cam-joystick"),
  mode: "static",
  position: { top: "50%", left: "50%" },
  color: "blue",
  size: 80,
  restOpacity: 0.4
});

camJoystick.on('move', (_, data) => {
  if (!selectedVehicle || !data?.direction) return;
  const dir = data.direction.angle;
  switch (dir) {
    case "up": sendCameraCommand("up"); break;
    case "down": sendCameraCommand("down"); break;
    case "left": sendCameraCommand("left"); break;
    case "right": sendCameraCommand("right"); break;
    default: break;
  }
});
camJoystick.on('end', () => sendCameraCommand("center"));
console.log("[JOYSTICK] Sending:", direction);


function sendCommand(direction) {
  if (!selectedVehicle) return;
  fetch('/api/drive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: direction, vehicle_id: selectedVehicle })
  });
}

let lastPingTime = 0;

function pingPi() {
  if (!selectedVehicle) return;
  lastPingTime = Date.now();
  socket.emit("ping_from_dashboard", {
    vehicle_id: selectedVehicle,
    timestamp: lastPingTime
  });
}

socket.on("pong_from_pi", (data) => {
  const latency = Date.now() - data.timestamp;
  document.getElementById("latency").innerText = `📶 ${latency}ms`;
});



function fetchStatus() {
  if (!selectedVehicle) return;
  fetch(`/api/status?vehicle_id=${selectedVehicle}`)
    .then(res => res.json())
    .then(data => {
      const level = data.battery;
      ["b1", "b2", "b3"].forEach((id, idx) => {
        document.getElementById(id).classList.toggle("on", idx < level + 1);
      });
      document.getElementById("latency").innerText = `📶 ${data.latency}ms`;
      document.getElementById("temp").innerText = `🌡️ ${data.temp}°C`;
    });
}

const challengeSelect = document.getElementById("challenge-select");
challengeSelect.addEventListener("change", () => {
  const value = challengeSelect.value;
  if (!value || !selectedVehicle) return;
  console.log("[CHALLENGE] Starte Challenge:", value);
});

function startChallenge() {
  const selectedChallenge = document.getElementById("challenge-select").value;
  if (!selectedVehicle || !selectedChallenge) return;

  fetch("/api/challenge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vehicle_id: selectedVehicle, challenge: selectedChallenge })
  });
}


function sendCameraCommand(direction) {
  if (!selectedVehicle) return;
  socket.emit("command", {
    pi_id: selectedVehicle,
    command: `camera:${direction}`
  });
}



setInterval(() => {
  fetchStatus();
  pingPi();
}, 3000);
