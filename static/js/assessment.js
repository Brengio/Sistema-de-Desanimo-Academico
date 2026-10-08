(() => {
  const form = document.getElementById('assessment-form');
  const textarea = document.getElementById('text_response');
  const counter = document.getElementById('character-count');
  const overlay = document.getElementById('processing-overlay');
  const submitButton = document.getElementById('analysis-submit');

  if (textarea && counter) {
    const updateCounter = () => { counter.textContent = String(textarea.value.length); };
    textarea.addEventListener('input', updateCounter);
    updateCounter();
  }

  if (form && overlay && submitButton) {
    form.addEventListener('submit', () => {
      if (!form.checkValidity()) return;
      submitButton.disabled = true;
      overlay.setAttribute('aria-hidden', 'false');
      overlay.classList.add('is-visible');
    });
  }
})();
