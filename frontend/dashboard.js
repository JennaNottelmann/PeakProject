let selectVehicle = null;

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

function selectVehicle() {
  selectedVehicle = document.getElementById('vehicle-select').value;
  document.getElementById('controls').style.display = 'block';
  alert("Fahrzeug verbunden: " + selectedVehicle);
}

function sendCommand(cmd) {
  if (!selectedVehicle) return alert("Kein Fahrzeug gewählt!");
  fetch('/api/drive', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ command: cmd, vehicle_id: selectedVehicle })
  });
}


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

function selectVehicle() {
  selectedVehicle = document.getElementById('vehicle-select').value;
  document.getElementById('controls').style.display = 'block';
  const status = document.getElementById('status');
  status.textContent = "Verbunden mit " + selectedVehicle;
  status.classList.remove("disconnected");
  status.classList.add("connected");
}

function sendCommand(cmd) {
  if (!selectedVehicle) return alert("Kein Fahrzeug ausgewählt!");
  fetch('/api/drive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: cmd, vehicle_id: selectedVehicle })
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
