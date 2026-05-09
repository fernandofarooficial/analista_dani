'use strict';

// Register service worker for PWA (URL injetada pelo template via DANIAPP_SW_URL)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    const swUrl = window.DANIAPP_SW_URL || '/sw.js';
    navigator.serviceWorker.register(swUrl, { scope: './' }).catch(() => {});
  });
}

// Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(el => {
    setTimeout(() => {
      const alert = bootstrap.Alert.getOrCreateInstance(el);
      if (alert) alert.close();
    }, 4000);
  });

  // CPF mask
  const cpfInput = document.querySelector('input[name="cpf"]');
  if (cpfInput) {
    cpfInput.addEventListener('input', e => {
      let v = e.target.value.replace(/\D/g, '').slice(0, 11);
      if (v.length > 9) v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4');
      else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d{0,3})/, '$1.$2.$3');
      else if (v.length > 3) v = v.replace(/(\d{3})(\d{0,3})/, '$1.$2');
      e.target.value = v;
    });
  }

  // CEP mask
  const cepInput = document.querySelector('input[name="cep"]');
  if (cepInput) {
    cepInput.addEventListener('input', e => {
      let v = e.target.value.replace(/\D/g, '').slice(0, 8);
      if (v.length > 5) v = v.replace(/(\d{5})(\d{0,3})/, '$1-$2');
      e.target.value = v;
    });
  }
});
