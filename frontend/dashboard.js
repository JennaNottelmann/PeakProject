let selectedVehicle = null;

// Fahrzeugliste vom Server laden
fetch('/api/available_vehicles')
  .then(res => res.json())
  .then(vehicles => {
    const sel = document.getElementById('vehicle-select');
    vehicles.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v;
      opt.textContent = v;
      sel.appendChild(opt);
    });
  });

// Fahrzeug verbinden + Statusanzeige aktualisieren
function selectVehicle() {
  selectedVehicle = document.getElementById('vehicle-select').value;
  if (!selectedVehicle) return;

  document.getElementById('controls').style.display = 'block';

  const status = document.getElementById('status');
  status.textContent = "Verbunden mit " + selectedVehicle;
  status.classList.remove("disconnected");
  status.classList.add("connected");

  // Kamera-Stream setzen
  const camera = document.getElementById('camera-stream');
  camera.src = `/stream/${selectedVehicle}`; // z. B. MJPEG Stream URL
  camera.style.display = 'block';
}

// Bewegungsbefehl an Fahrzeug senden
function sendCommand(cmd) {
  if (!selectedVehicle) return alert("Kein Fahrzeug ausgewählt!");
  fetch('/api/drive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: cmd, vehicle_id: selectedVehicle })
  });
}

// Kamera bewegen
function controlCamera(direction) {
  if (!selectedVehicle) return alert("Kein Fahrzeug ausgewählt!");
  fetch('/api/camera-control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction: direction, vehicle_id: selectedVehicle })
  });
}

// Kamera zurücksetzen (zentrieren)
function resetCamera() {
  controlCamera("center");
}
