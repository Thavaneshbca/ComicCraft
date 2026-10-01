/**
 * ComicCraft Interactive Client-side Script
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Quick-Start Preset Configurations
  const presets = {
    fox: {
      prompt: "A brave red fox exploring an ancient enchanted forest uncovers a glowing crystalline relic that awakens mystical forest guardians.",
      character: "Free the Red Fox",
      setting: "Enchanted Forest",
      tone: "Dramatic",
      artStyle: "Comic Book",
    },
    cyber: {
      prompt: "A street-smart cybernetic detective navigates neon-lit alleyways searching for an encrypted data chip stolen by corporate rogue drones.",
      character: "Detective Jax",
      setting: "Cyberpunk Metropolis",
      tone: "Adventure",
      artStyle: "Anime",
    },
    space: {
      prompt: "A lone interstellar explorer on a distant icy moon encounters a mysterious sentient monolith pulsing with harmonic frequencies.",
      character: "Captain Lyra Vance",
      setting: "Space",
      tone: "Poetic",
      artStyle: "Realistic",
    },
    kingdom: {
      prompt: "A witty young apprentice jester accidentally triggers an ancient royal enchantment turning castle guards into talking frogs.",
      character: "Barnaby the Apprentice",
      setting: "Fantasy Kingdom",
      tone: "Funny",
      artStyle: "Comic Book",
    },
  };

  // Wire Preset Buttons
  document.querySelectorAll(".preset-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const presetKey = btn.getAttribute("data-preset");
      const data = presets[presetKey];
      if (!data) return;

      const promptInput = document.getElementById("story_prompt");
      const charInput = document.getElementById("character_name");
      const settingInput = document.getElementById("setting");
      const toneInput = document.getElementById("tone");
      const artStyleInput = document.getElementById("art_style");

      if (promptInput) promptInput.value = data.prompt;
      if (charInput) charInput.value = data.character;
      if (settingInput) settingInput.value = data.setting;
      if (toneInput) toneInput.value = data.tone;
      if (artStyleInput) artStyleInput.value = data.artStyle;

      // Visual feedback on button
      btn.style.borderColor = "var(--accent-yellow)";
      setTimeout(() => {
        btn.style.borderColor = "";
      }, 600);
    });
  });

  // 2. Form Submission & Step-by-Step Progress Overlay
  const comicForm = document.getElementById("comic-generator-form");
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingStep = document.getElementById("loading-step");
  const progressFill = document.getElementById("progress-fill");

  if (comicForm && loadingOverlay) {
    comicForm.addEventListener("submit", (e) => {
      const promptVal = document.getElementById("story_prompt")?.value?.trim();
      const charVal = document.getElementById("character_name")?.value?.trim();
      const settingVal = document.getElementById("setting")?.value?.trim();

      if (!promptVal || !charVal || !settingVal) {
        alert("Please fill in the Story Prompt, Character Name, and Setting.");
        e.preventDefault();
        return;
      }

      // Show animated loading overlay
      loadingOverlay.style.display = "flex";

      const submitBtn = comicForm.querySelector("button[type='submit']");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.7";
      }

      // Step sequence simulator for user feedback
      const steps = [
        { text: "Planning 5-panel arc with Gemini Flash...", width: "25%", delay: 600 },
        { text: "Writing narration & dialogues with Gemini Pro...", width: "50%", delay: 2000 },
        { text: "Illustrating 5 comic panels with Diffusion AI...", width: "75%", delay: 3800 },
        { text: "Assembling comic layout & compiling PDF...", width: "92%", delay: 5600 },
      ];

      steps.forEach((step) => {
        setTimeout(() => {
          if (loadingStep) loadingStep.textContent = step.text;
          if (progressFill) progressFill.style.width = step.width;
        }, step.delay);
      });
    });
  }

  // 3. Download Button Handler on comic_preview.html
  const downloadBtn = document.getElementById("download-pdf-btn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", (e) => {
      e.preventDefault();
      const pdfUrl = downloadBtn.getAttribute("data-pdf-path");
      if (!pdfUrl) return;

      // Trigger file download via invisible link
      const link = document.createElement("a");
      link.href = pdfUrl;
      link.download = pdfUrl.split("/").pop() || "comic.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Redirect user to export-success page as described in PDF
      setTimeout(() => {
        window.location.href = `/export-success?pdf_path=${encodeURIComponent(pdfUrl)}`;
      }, 700);
    });
  }
});
