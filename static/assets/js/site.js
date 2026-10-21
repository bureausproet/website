// Zet de licht verborgen e-mailadressen (naam [at] domein) om in klikbare mailto-links.
// Zonder JavaScript blijft het adres leesbaar als "naam [at] bureausproet.nl".
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("a.mail[data-u][data-d]").forEach(function (link) {
    var address = link.dataset.u + "@" + link.dataset.d;
    var subject = link.dataset.s ? "?subject=" + encodeURIComponent(link.dataset.s) : "";
    link.href = "mailto:" + address + subject;
    link.textContent = address;
  });
});
