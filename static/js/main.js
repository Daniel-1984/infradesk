/* InfraDesk — Main JS */

document.addEventListener('DOMContentLoaded', function () {

  // Sidebar toggle for mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('show');
      }
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // Confirm dialogs for destructive actions
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
  });

  // Priority select visual feedback
  const prioritySelect = document.getElementById('id_priority');
  if (prioritySelect) {
    function updatePriorityStyle() {
      const colors = { low: '#198754', medium: '#ffc107', high: '#dc3545', critical: '#212529' };
      const val = prioritySelect.value;
      prioritySelect.style.borderLeftColor = colors[val] || '#dee2e6';
      prioritySelect.style.borderLeftWidth = '4px';
    }
    prioritySelect.addEventListener('change', updatePriorityStyle);
    updatePriorityStyle();
  }

  // Status select color feedback
  const statusSelect = document.getElementById('id_status');
  if (statusSelect) {
    function updateStatusStyle() {
      const colors = {
        open: '#0d6efd', in_progress: '#0dcaf0',
        waiting: '#ffc107', resolved: '#198754', closed: '#6c757d'
      };
      statusSelect.style.borderLeftColor = colors[statusSelect.value] || '#dee2e6';
      statusSelect.style.borderLeftWidth = '4px';
    }
    statusSelect.addEventListener('change', updateStatusStyle);
    updateStatusStyle();
  }

  // Character counter for textareas
  document.querySelectorAll('textarea[maxlength]').forEach(ta => {
    const counter = document.createElement('div');
    counter.className = 'form-text text-end';
    ta.parentNode.appendChild(counter);
    function updateCounter() {
      const remaining = ta.maxLength - ta.value.length;
      counter.textContent = `${remaining} caracteres restantes`;
      counter.className = remaining < 20 ? 'form-text text-danger text-end' : 'form-text text-muted text-end';
    }
    ta.addEventListener('input', updateCounter);
    updateCounter();
  });

  // Tooltip initialization
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // Table row click navigation
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => {
      window.location.href = row.dataset.href;
    });
  });

  // Smooth scroll to anchors
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
});
