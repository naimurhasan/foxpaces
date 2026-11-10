const showConsentBanner = () => {
  const banner = document.createElement("div");
  banner.id = "consent";
  banner.style.cssText =
    "position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center";
  banner.innerHTML = `
    <div style="background:#fff;padding:24px;max-width:320px">
      <p>We use cookies to improve your experience. Please accept to continue reading.</p>
      <button id="accept">Accept cookies</button>
    </div>`;
  document.body.appendChild(banner);
  document.getElementById("accept").addEventListener("click", () => banner.remove());
};
