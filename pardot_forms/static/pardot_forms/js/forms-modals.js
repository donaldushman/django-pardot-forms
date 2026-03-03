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
