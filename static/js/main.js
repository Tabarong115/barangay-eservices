document.querySelectorAll("[data-coming-soon]").forEach((button) => {
  button.addEventListener("click", () => {
    window.alert(`${button.dataset.comingSoon} is not available online yet. Please visit the Barangay Hall for service.`);
  });
});

document.querySelectorAll("[data-copy-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const trackingNumber = target.textContent.trim();
    try {
      await navigator.clipboard.writeText(trackingNumber);
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = "Copy number"; }, 1800);
    } catch {
      window.prompt("Copy your tracking number:", trackingNumber);
    }
  });
});
