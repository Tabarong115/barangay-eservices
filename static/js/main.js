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

// Birthday validation to warn about obviously wrong dates
document.querySelectorAll("input[name='birthday']").forEach((birthdayInput) => {
  birthdayInput.addEventListener("change", function() {
    const birthdayValue = this.value;
    if (!birthdayValue) return;

    const birthday = new Date(birthdayValue);
    const today = new Date();
    
    // Check if birthday is in the future
    if (birthday > today) {
      const warning = "Warning: The birthday you entered is in the future. This appears to be incorrect. You can proceed, but please verify your birth date before submitting.";
      if (!confirm(warning + "\n\nClick OK to proceed with this date, or Cancel to correct it.")) {
        this.value = "";
      }
      return;
    }

    // Check if birthday is too old (more than 120 years)
    const maxAge = 120;
    const ageInYears = (today - birthday) / (1000 * 60 * 60 * 24 * 365.25);
    
    if (ageInYears > maxAge) {
      const warning = `Warning: The birthday you entered suggests you are over ${maxAge} years old. This appears to be incorrect. You can proceed, but please verify your birth date before submitting.`;
      if (!confirm(warning + "\n\nClick OK to proceed with this date, or Cancel to correct it.")) {
        this.value = "";
      }
      return;
    }

    // Check if birthday is too young (less than 1 year old)
    if (ageInYears < 1) {
      const warning = "Warning: The birthday you entered suggests you are less than 1 year old. This appears to be incorrect. You can proceed, but please verify your birth date before submitting.";
      if (!confirm(warning + "\n\nClick OK to proceed with this date, or Cancel to correct it.")) {
        this.value = "";
      }
      return;
    }
  });
});
