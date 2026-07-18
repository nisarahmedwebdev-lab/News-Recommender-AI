// Main JavaScript for News Recommender System

// ========== UTILITY FUNCTIONS (Define First) ==========
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== TOAST NOTIFICATION ==========
function showToast(message, type = 'success') {
    // Check if SweetAlert is available
    if (typeof Swal !== 'undefined') {
        const iconMap = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };

        Swal.fire({
            icon: iconMap[type] || 'info',
            title: type === 'success' ? 'Success!' :
                type === 'error' ? 'Error!' :
                    type === 'warning' ? 'Warning!' : 'Info',
            text: message,
            timer: 2500,
            showConfirmButton: false,
            toast: true,
            position: 'top-end',
            timerProgressBar: true
        });
    } else {
        // Fallback to Bootstrap toast
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        const toast = document.createElement('div');
        const bgClass = type === 'success' ? 'bg-success' :
            type === 'error' ? 'bg-danger' :
                type === 'warning' ? 'bg-warning' : 'bg-info';
        const textClass = type === 'warning' ? 'text-dark' : 'text-white';

        toast.className = `toast align-items-center ${bgClass} ${textClass} border-0`;
        toast.role = 'alert';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
        setTimeout(() => toast.remove(), 3500);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// ========== LIKE BUTTON HANDLER ==========
function handleLikeClick(e) {
    e.preventDefault();
    e.stopPropagation();

    const btn = this;
    const url = btn.dataset.url;
    const icon = btn.querySelector('.like-icon');
    const countEl = btn.querySelector('.like-count');
    const csrfToken = btn.dataset.csrf || getCSRFToken();

    // Save original HTML for reset
    const originalHtml = btn.innerHTML;

    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update icon
            if (data.liked) {
                icon.classList.add('text-danger');
                icon.classList.remove('text-muted');
                showToast('You liked this post! ❤️', 'success');
            } else {
                icon.classList.remove('text-danger');
                icon.classList.add('text-muted');
                showToast('You unliked this post', 'info');
            }

            // Update count
            if (countEl) {
                countEl.textContent = data.likes_count;
            }

            // Reset button
            btn.disabled = false;
            btn.innerHTML = originalHtml;

            // Update the count in the reset HTML
            const newCount = btn.querySelector('.like-count');
            if (newCount) {
                newCount.textContent = data.likes_count;
            }
        })
        .catch(error => {
            console.error('Like error:', error);
            showToast('Something went wrong! Please try again.', 'error');
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        });
}

// ========== SAVE BUTTON HANDLER ==========
function handleSaveClick(e) {
    e.preventDefault();
    e.stopPropagation();

    const btn = this;
    const url = btn.dataset.url;
    const icon = btn.querySelector('.save-icon');
    const countEl = btn.querySelector('.save-count');
    const csrfToken = btn.dataset.csrf || getCSRFToken();

    // Save original HTML for reset
    const originalHtml = btn.innerHTML;

    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Update icon
            if (data.saved) {
                icon.classList.add('text-warning');
                icon.classList.remove('text-muted');
                showToast('Post saved! 📌', 'success');
            } else {
                icon.classList.remove('text-warning');
                icon.classList.add('text-muted');
                showToast('Post unsaved', 'info');
            }

            // Update count
            if (countEl) {
                countEl.textContent = data.saves_count;
            }

            // Reset button
            btn.disabled = false;
            btn.innerHTML = originalHtml;

            // Update the count in the reset HTML
            const newCount = btn.querySelector('.save-count');
            if (newCount) {
                newCount.textContent = data.saves_count;
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            showToast('Something went wrong! Please try again.', 'error');
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        });
}

// ========== INITIALIZE LIKE BUTTONS ==========
function initializeLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(function (btn) {
        // Remove existing event listeners to avoid duplicates
        btn.removeEventListener('click', handleLikeClick);
        btn.addEventListener('click', handleLikeClick);
    });
}

// ========== INITIALIZE SAVE BUTTONS ==========
function initializeSaveButtons() {
    document.querySelectorAll('.save-btn').forEach(function (btn) {
        // Remove existing event listeners to avoid duplicates
        btn.removeEventListener('click', handleSaveClick);
        btn.addEventListener('click', handleSaveClick);
    });
}

// ========== RE-INITIALIZE ON DYNAMIC CONTENT ==========
function reinitializeInteractions() {
    initializeLikeButtons();
    initializeSaveButtons();
}

// ========== SWEET ALERT FUNCTIONS (Legacy Support) ==========
function showSuccessAlert(message) {
    showToast(message, 'success');
}

function showErrorAlert(message) {
    showToast(message, 'error');
}

function showWarningAlert(message) {
    showToast(message, 'warning');
}

function showInfoAlert(message) {
    showToast(message, 'info');
}

// ========== CONFIRM DIALOG ==========
function showConfirmDialog(title, message, callback) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                callback();
            }
        });
    } else {
        // Fallback to browser confirm
        if (confirm(`${title}\n\n${message}`)) {
            callback();
        }
    }
}

// ========== DOM CONTENT LOADED ==========
document.addEventListener('DOMContentLoaded', function () {
    // ========== SIDEBAR TOGGLE ==========
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mainContent = document.getElementById('mainContent');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');

    function toggleSidebar() {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
        mainContent.classList.toggle('sidebar-active');

        // Save state to localStorage
        const isActive = sidebar.classList.contains('active');
        localStorage.setItem('sidebarActive', isActive);

        // Adjust body overflow
        if (window.innerWidth <= 991 && isActive) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    // Open sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Close sidebar
    if (sidebarClose) {
        sidebarClose.addEventListener('click', toggleSidebar);
    }

    // Close sidebar on overlay click
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }

    // Close sidebar on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });

    // Restore sidebar state from localStorage
    const savedState = localStorage.getItem('sidebarActive');
    if (savedState === 'true' && window.innerWidth >= 992) {
        sidebar.classList.add('active');
        mainContent.classList.add('sidebar-active');
    }

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            if (window.innerWidth >= 992) {
                document.body.style.overflow = '';
                const isActive = sidebar.classList.contains('active');
                if (isActive) {
                    mainContent.classList.add('sidebar-active');
                } else {
                    mainContent.classList.remove('sidebar-active');
                }
            } else {
                mainContent.classList.remove('sidebar-active');
                if (sidebar.classList.contains('active')) {
                    document.body.style.overflow = 'hidden';
                }
            }
        }, 250);
    });

    // ========== AUTO-DISMISS ALERTS ==========
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // ========== SIDEBAR ACTIVE LINK ==========
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.style.background = '#34495e';
            link.style.color = '#fff';
        }
    });

    // ========== INITIALIZE LIKE AND SAVE BUTTONS ==========
    initializeLikeButtons();
    initializeSaveButtons();
});

// ========== EXPORT FOR OTHER SCRIPTS ==========
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        showSuccessAlert,
        showErrorAlert,
        showWarningAlert,
        showInfoAlert,
        showConfirmDialog,
        getCSRFToken,
        reinitializeInteractions,
        initializeLikeButtons,
        initializeSaveButtons
    };
}