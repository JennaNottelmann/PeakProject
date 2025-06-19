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

    const streamWrapper = document.getElementById("camera-stream");
    const camera = document.getElementById("camera");

    camera.src = "https://stream.kaiju-cars.de/stream.mjpg";
    camera.onerror = () => {
    camera.src = "/static/404.png";
    camera.alt = "Kamera-Stream nicht verfügbar";
    };
    camera.alt = `Kamera-Stream für ${selectedVehicle}`;
    streamWrapper.style.display = "flex";

}

const streamWrapper = document.getElementById("camera-stream");
const connectBtn = document.getElementById("connect-btn");

let isConnected = false;

connectBtn.addEventListener("click", () => {
  const selected = select.value;

  if (!selected || selected === "Fahrzeug wählen") {
    alert("Bitte zuerst ein Fahrzeug auswählen.");
    return;
  }

  selectedVehicle = selected; 

  if (!isConnected) {
    camera.src = "https://stream.kaiju-cars.de/stream.mjpg";
    camera.onerror = () => {
      camera.src = "/static/404.png";
      camera.alt = "Kamera-Stream nicht verfügbar";
    };
    camera.alt = `Kamera-Stream für ${selectedVehicle}`;
    streamWrapper.style.display = "flex";

    connectBtn.textContent = "Trennen";
    isConnected = true;
  } else {
    camera.src = "";
    streamWrapper.style.display = "none";

    connectBtn.textContent = "Verbinden";
    isConnected = false;
  }
});





function sendDriveCommand(direction) {
    if (!selectedVehicle) return;
    fetch('/api/drive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: direction, vehicle_id: selectedVehicle })
    });
}

function sendCameraCommand(direction) {
    if (!selectedVehicle) return;
    fetch('/api/camera-control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vehicle_id: selectedVehicle, direction })
    });
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
    updateStatus(data);
});

function updateStatus(data) {
    const level = data.battery;
    ["b1", "b2", "b3"].forEach((id, idx) => {
        document.getElementById(id).classList.toggle("on", idx < level);
    });

    document.getElementById("temp").innerText = `🌡️ ${data.temp}°C`;
    document.getElementById("latency").innerText = `📶 ${data.latency}ms`;
}

function requestLatency() {
    if (!selectedVehicle) return;
    socket.emit("latency_ping", { vehicle_id: selectedVehicle });
}

// Auto-Joystick (links)
const autoJoystick = nipplejs.create({
    zone: document.getElementById("joystick-left"),
    mode: "static",
    position: { top: "30%", left: "50%" },
    color: "yellow",
    size: 160,
    restOpacity: 0.4
});

autoJoystick.on('move', (_, data) => {
    if (!selectedVehicle || !data?.direction) return;
    const dir = data.direction.angle;
    switch (dir) {
        case "up": 
            sendDriveCommand("forward"); 
            break;
        case "down": 
            sendDriveCommand("backward"); 
            break;
        case "left": 
            sendDriveCommand("left"); 
            break;
        case "right": 
            sendDriveCommand("right"); 
            break;
        case "up-left":
            sendDriveCommand("forward_left"); 
            break;
        case "up-right":
            sendDriveCommand("forward_right"); 
            break;
        case "down-left":
            sendDriveCommand("backward_left");
            break;
        case "down-right":
            sendDriveCommand("backward_right");
            break;

        default: 
            sendDriveCommand("stop"); 
            break;
}

});

autoJoystick.on('end', () => {
    sendDriveCommand("stop");
    setTimeout(() => sendDriveCommand("stop"), 200);
});

// Kamera-Joystick (rechts)
const camJoystick = nipplejs.create({
    zone: document.getElementById("cam-joystick"),
    mode: "static",
    position: { top: "30%", left: "50%" },
    color: "blue",
    size: 130,
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

// Status manuell abrufen (Backup-Fallback)
function fetchStatus() {
    if (!selectedVehicle) return;
    fetch(`/api/status?vehicle_id=${selectedVehicle}`)
      .then(res => {
          if (!res.ok) throw new Error("Status not found");
          return res.json();
      })
      .then(data => updateStatus(data))
      .catch(err => console.warn(err));
}
// Challenges
const challengeSelect = document.getElementById("challenge-select");
challengeSelect.addEventListener("change", () => {
    const value = challengeSelect.value;
    if (!value || !selectedVehicle) return;
    console.log("[CHALLENGE] Starte Challenge:", value);
});

function startChallenge() {
    const selectedChallenge = challengeSelect.value;
    if (!selectedVehicle || !selectedChallenge) return;

    fetch("/api/run_challenge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vehicle_id: selectedVehicle, challenge: selectedChallenge })
    });
}


setInterval(() => {
    fetchStatus();
    requestLatency();
}, 3000);
