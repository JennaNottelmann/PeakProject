let selectedVehicle = null;

// Fahrzeugliste vom Server laden
const sel = document.getElementById('vehicle-select');
const opt = document.createElement('option');
opt.value = "pi_01";  // Dummy-ID
opt.textContent = "pi_01";
sel.appendChild(opt);

fetch('/api/available_vehicles')
  .then(res => res.json())
  .then(vehicles => {
    vehicles.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v.id;
      opt.textContent = v.id;
      opt.dataset.ip = v.ip;
      sel.appendChild(opt);
    });
  });


function selectVehicle() {
  const select = document.getElementById('vehicle-select');
  selectedVehicle = select.value;
  if (!selectedVehicle) return;

  document.getElementById('controls').style.display = 'block';

  const status = document.getElementById('status');
  status.textContent = "Verbunden mit " + selectedVehicle;
  status.classList.remove("disconnected");
  status.classList.add("connected");

  const selectedOption = select.options[select.selectedIndex];
  const ip = selectedOption.dataset.ip;

  const camera = document.getElementById('camera-stream');
  if (ip) {
    camera.src = `http://${ip}:8080/stream.mjpg`;
  } else {
    camera.src = ""; // fallback
  }
  camera.style.display = 'block';
}


function sendCommand(cmd) {
  if (!selectedVehicle) return alert("Kein Fahrzeug ausgewählt!");
  fetch('/api/drive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: cmd, vehicle_id: selectedVehicle })
  });
}

function startCamera() {
  if (!selectedVehicle) return;

  fetch(`/api/camera-start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ vehicle_id: selectedVehicle }),
  })
  .then(response => {
    if (response.ok) {
      console.log("[CAM] Kamera gestartet");
    } else {
      console.error("[CAM] Fehler beim Starten der Kamera");
    }
  });
}


function controlCamera(direction) {
  if (!selectedVehicle) return alert("Kein Fahrzeug ausgewählt!");
  fetch('/api/camera-control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction: direction, vehicle_id: selectedVehicle })
  });
}

function resetCamera() {
  controlCamera("center");
}

let holdInterval;

function startHoldCommand(cmd) {
  sendCommand(cmd); // sofort senden
  holdInterval = setInterval(() => sendCommand(cmd), 300); // wiederholt senden
}

function stopHoldCommand() {
  clearInterval(holdInterval);
  sendCommand("stop"); // Fahrzeug anhalten
}

let camHoldInterval;

function startCameraCommand(cmd) {
  sendCommand(cmd); // sofort senden
  camHoldInterval = setInterval(() => sendCommand(cmd), 300); // wiederholt senden
}

function stopCameraCommand() {
  clearInterval(camHoldInterval);
}
