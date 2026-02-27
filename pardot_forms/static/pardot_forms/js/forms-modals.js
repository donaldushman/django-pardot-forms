// Contact form AJAX handler
// URLs should be configured via window.PARDOT_FORMS_URLS
// Include pardot_forms/includes/forms_urls.html in your template
if (!window.PARDOT_FORMS_URLS) {
    console.error('PARDOT_FORMS_URLS not configured. Include pardot_forms/includes/forms_urls.html in your template.');
}

const URLS = window.PARDOT_FORMS_URLS || {};

(() => {
  const contactModal = document.getElementById('contactModal');
  if (!contactModal) return;

  const formContainer = document.getElementById('contactFormContainer');
  if (!formContainer) return;

  // Load form when modal opens
  contactModal.addEventListener('show.bs.modal', () => {
    // Reset to loading state
    formContainer.setAttribute('aria-busy', 'true');
    formContainer.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    `;

    fetch(URLS.contact, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error(`Failed to load form: ${response.status} ${response.statusText}`);
        }
        return response.text();
      })
      .then(html => {
        console.log('Received HTML length:', html.length);
        formContainer.innerHTML = html;
        formContainer.setAttribute('aria-busy', 'false');

        // Focus first form field for keyboard users
        const firstInput = formContainer.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput) {
          setTimeout(() => firstInput.focus(), 100);
        }

        attachFormHandler();
      })
      .catch(error => {
        console.error('Error loading contact form:', error);
        formContainer.innerHTML = `
          <div class="alert alert-danger" role="alert">
            Error loading form. Please try again or contact us directly.
            <br><small>${error.message}</small>
          </div>
        `;
        formContainer.setAttribute('aria-busy', 'false');
      });
  });

  function attachFormHandler() {
    const form = formContainer.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      // Disable submit button to prevent double-submission
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn) return;

      const originalBtnText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sending...';
      submitBtn.setAttribute('aria-busy', 'true');

      const formData = new FormData(form);

      fetch(URLS.contact, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(response => {
          if (!response.ok) throw new Error('Network response was not ok');
          return response.json();
        })
        .then(data => {
          if (data.success) {
            formContainer.innerHTML = `
              <div class="alert alert-success" role="alert" aria-live="assertive">
                <h4 class="alert-heading">Thank you!</h4>
                <p>${data.message || 'Your message has been sent successfully.'}</p>
              </div>
            `;

            // Focus the success message for screen readers
            const successMsg = formContainer.querySelector('.alert');
            if (successMsg) {
              successMsg.setAttribute('tabindex', '-1');
              successMsg.focus();
            }

            // Optionally close modal after a delay
            setTimeout(() => {
              const modalInstance = bootstrap.Modal.getInstance(contactModal);
              if (modalInstance) {
                modalInstance.hide();
              }
            }, 3000);
          } else {
            // Show form with errors
            formContainer.innerHTML = data.html;

            // Focus first error or first field
            const firstError = formContainer.querySelector('.invalid-feedback, .errorlist, .alert-danger');
            if (firstError) {
              firstError.setAttribute('role', 'alert');
              firstError.setAttribute('aria-live', 'assertive');
              const firstInvalidInput = formContainer.querySelector('.is-invalid, input, textarea, select');
              if (firstInvalidInput) {
                setTimeout(() => firstInvalidInput.focus(), 100);
              }
            }

            attachFormHandler();
          }
        })
        .catch(error => {
          console.error('Error submitting form:', error);
          // Re-enable submit button on error
          submitBtn.disabled = false;
          submitBtn.textContent = originalBtnText;
          submitBtn.setAttribute('aria-busy', 'false');

          // Show error message
          const errorDiv = document.createElement('div');
          errorDiv.className = 'alert alert-danger mt-3';
          errorDiv.setAttribute('role', 'alert');
          errorDiv.setAttribute('aria-live', 'assertive');
          errorDiv.textContent = 'Error submitting form. Please try again.';
          
          // Remove existing error messages
          const existingError = form.querySelector('.alert-danger');
          if (existingError) {
            existingError.remove();
          }
          
          form.insertBefore(errorDiv, form.firstChild);
        });
    });
  }
})();

// Subscribe form AJAX handler
(() => {
  const footerForm = document.getElementById('footerEmailForm');
  if (!footerForm) return;

  const subscribeModal = document.getElementById('subscribeModal');
  if (!subscribeModal) return;

  const subscribeFormContainer = document.getElementById('subscribeFormContainer');
  if (!subscribeFormContainer) return;

  // Handle footer email form submission
  footerForm.addEventListener('submit', (e) => {
    e.preventDefault();

    // Disable submit button to prevent double-submission
    const submitBtn = footerForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';

    const formData = new FormData(footerForm);

    fetch(URLS.optIn, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Email saved, now open modal with full form
          loadFullForm();
          const modal = new bootstrap.Modal(subscribeModal);
          modal.show();
          footerForm.reset();
          
          // Re-enable button
          submitBtn.disabled = false;
          submitBtn.textContent = originalBtnText;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.textContent = originalBtnText;
        // Fallback to regular form submission
        footerForm.submit();
      });
  });

  function loadFullForm() {
    subscribeFormContainer.setAttribute('aria-busy', 'true');
    subscribeFormContainer.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    `;

    fetch(URLS.subscribe, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to load form: ${response.status} ${response.statusText}`);
        }
        return response.text();
      })
      .then(html => {
        subscribeFormContainer.innerHTML = html;
        subscribeFormContainer.setAttribute('aria-busy', 'false');

        // Focus first form field for keyboard users
        const firstInput = subscribeFormContainer.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput) {
          setTimeout(() => firstInput.focus(), 100);
        }

        // Setup T&C collapse toggle
        const toggleLink = document.getElementById('tandcToggle');
        const collapseEl = document.getElementById('tandcCollapse');
        
        if (toggleLink && collapseEl) {
          collapseEl.addEventListener('show.bs.collapse', function() {
            toggleLink.textContent = 'Show less';
          });
          collapseEl.addEventListener('hide.bs.collapse', function() {
            toggleLink.textContent = 'Show more';
          });
        }

        attachSubscribeFormHandler();
      })
      .catch(error => {
        console.error('Error loading form:', error);
        subscribeFormContainer.innerHTML = `
          <div class="alert alert-danger" role="alert">
            Error loading form. Please try again or <a href="/subscribe/">visit the subscription page</a>.
            <br><small>${error.message}</small>
          </div>
        `;
        subscribeFormContainer.setAttribute('aria-busy', 'false');
      });
  }

  function attachSubscribeFormHandler() {
    const form = subscribeFormContainer.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      // Disable submit button to prevent double-submission
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn) return;

      const originalBtnText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Subscribing...';
      submitBtn.setAttribute('aria-busy', 'true');

      const formData = new FormData(form);

      fetch(URLS.subscribe, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(response => {
          if (!response.ok) throw new Error('Network response was not ok');
          return response.json();
        })
        .then(data => {
          if (data.success) {
            subscribeFormContainer.innerHTML = `
              <div class="alert alert-success" role="alert" aria-live="assertive">
                <h4 class="alert-heading">Thank you for subscribing!</h4>
                <p>${data.message || 'We will keep you updated on training and resources.'}</p>
              </div>
            `;

            // Focus the success message for screen readers
            const successMsg = subscribeFormContainer.querySelector('.alert');
            if (successMsg) {
              successMsg.setAttribute('tabindex', '-1');
              successMsg.focus();
            }

            // Close modal after a delay
            setTimeout(() => {
              const modalInstance = bootstrap.Modal.getInstance(subscribeModal);
              if (modalInstance) {
                modalInstance.hide();
              }
            }, 3000);
          } else {
            // Show form with errors
            subscribeFormContainer.innerHTML = data.html;

            // Focus first error or first field
            const firstError = subscribeFormContainer.querySelector('.invalid-feedback, .errorlist, .alert-danger');
            if (firstError) {
              firstError.setAttribute('role', 'alert');
              firstError.setAttribute('aria-live', 'assertive');
              const firstInvalidInput = subscribeFormContainer.querySelector('.is-invalid, input, textarea, select');
              if (firstInvalidInput) {
                setTimeout(() => firstInvalidInput.focus(), 100);
              }
            }

            attachSubscribeFormHandler();
          }
        })
        .catch(error => {
          console.error('Error submitting form:', error);
          // Re-enable submit button on error
          submitBtn.disabled = false;
          submitBtn.textContent = originalBtnText;
          submitBtn.setAttribute('aria-busy', 'false');

          // Show error message
          const errorDiv = document.createElement('div');
          errorDiv.className = 'alert alert-danger mt-3';
          errorDiv.setAttribute('role', 'alert');
          errorDiv.setAttribute('aria-live', 'assertive');
          errorDiv.textContent = 'Error submitting form. Please try again.';
          
          // Remove existing error messages
          const existingError = form.querySelector('.alert-danger');
          if (existingError) {
            existingError.remove();
          }
          
          form.insertBefore(errorDiv, form.firstChild);
        });
    });
  }
})();
