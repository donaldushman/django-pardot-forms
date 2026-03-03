// Open subscribe modal if ?subscribe=1 is in the URL (after footer email form submit)
(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('subscribe') === '1') {
    const modalEl = document.getElementById('subscribeModal');
    if (modalEl && typeof bootstrap !== 'undefined') {
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    }
    // Clean the param from the URL without reloading
    params.delete('subscribe');
    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    history.replaceState(null, '', newUrl);
  }
})();

// T&C collapse toggle for subscribe form
(() => {
  function initTandCToggle() {
    const toggleLink = document.getElementById('tandcToggle');
    const collapseEl = document.getElementById('tandcCollapse');

    if (toggleLink && collapseEl) {
      collapseEl.addEventListener('show.bs.collapse', function () {
        toggleLink.textContent = 'Show less';
      });
      collapseEl.addEventListener('hide.bs.collapse', function () {
        toggleLink.textContent = 'Show more';
      });
    }
  }

  // Init on DOMContentLoaded (full form page)
  document.addEventListener('DOMContentLoaded', initTandCToggle);
})();
