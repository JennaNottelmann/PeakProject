document.addEventListener("DOMContentLoaded", function() {
  // Prüfen, ob Zustimmung schon erteilt wurde
  if (localStorage.getItem("cookieConsent") === "true") {
    return;
  }

  // Banner erzeugen
  const banner = document.createElement("div");
  banner.id = "cookie-banner";
  banner.style.position = "fixed";
  banner.style.bottom = "0";
  banner.style.left = "0";
  banner.style.right = "0";
  banner.style.background = "rgba(0, 0, 0, 0.9)";
  banner.style.color = "#fff";
  banner.style.padding = "1rem";
  banner.style.textAlign = "center";
  banner.style.zIndex = "9999";
  banner.style.fontSize = "0.9rem";
  banner.innerHTML = `
    Diese Website verwendet Cookies. Mit der Nutzung erklärst du dich damit einverstanden.
    <button id="cookie-ok" style="
      margin-left: 1rem;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 5px;
      background: #e3dd13;
      color: #000;
      font-weight: bold;
      cursor: pointer;">
      Verstanden
    </button>
  `;

  document.body.appendChild(banner);

  document.getElementById("cookie-ok").addEventListener("click", function() {
    localStorage.setItem("cookieConsent", "true");
    banner.remove();
  });
});
