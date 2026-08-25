/**
 * Central API Client & UI Helper for Career DNA AI
 * Handles JWT authentication, request headers, error handling,
 * Bootstrap toast notifications, and AI loading modal states.
 */

const API_BASE = '/api';

class ApiClient {
    constructor() {
        this.tokenKey = 'career_dna_token';
        this.userKey = 'career_dna_user';
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    setAuth(token, user) {
        localStorage.setItem(this.tokenKey, token);
        if (user) {
            localStorage.setItem(this.userKey, JSON.stringify(user));
        }
    }

    getUser() {
        const data = localStorage.getItem(this.userKey);
        try {
            return data ? JSON.parse(data) : null;
        } catch {
            return null;
        }
    }

    clearAuth() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    isAdmin() {
        const user = this.getUser();
        return user && user.role === 'admin';
    }

    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            
            // Handle binary/blob responses (e.g. PDF download)
            if (options.responseType === 'blob') {
                if (!response.ok) {
                    throw new Error('Failed to download file');
                }
                return await response.blob();
            }

            const data = await response.json().catch(() => ({
                success: false,
                message: `Server returned status ${response.status}`
            }));

            if (response.status === 401) {
                // If token expired and on a protected page
                const isAuthPage = window.location.pathname.includes('/login') || window.location.pathname.includes('/register') || window.location.pathname === '/';
                if (!isAuthPage) {
                    this.clearAuth();
                    this.showToast('Session expired. Please log in again.', 'warning');
                    setTimeout(() => {
                        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
                    }, 1200);
                }
            }

            if (!response.ok || data.success === false) {
                const errorMsg = data.message || 'An unexpected error occurred.';
                if (!options.silent) {
                    this.showToast(errorMsg, 'danger');
                }
                throw new Error(errorMsg);
            }

            return data;
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            throw err;
        }
    }

    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    post(endpoint, body = {}, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
    }

    put(endpoint, body = {}, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
    }

    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    // ==========================================
    // UI Feedback Helpers (Toasts & AI Modal)
    // ==========================================
    showToast(message, type = 'info', title = '') {
        const toastEl = document.getElementById('liveAppToast');
        if (!toastEl) return;

        const titleEl = document.getElementById('appToastTitle');
        const bodyEl = document.getElementById('appToastBody');
        const iconEl = document.getElementById('appToastIcon');

        const typeMap = {
            success: { title: 'Success', icon: 'bi-check-circle-fill text-success', bg: 'border-success' },
            danger: { title: 'Error', icon: 'bi-exclamation-triangle-fill text-danger', bg: 'border-danger' },
            warning: { title: 'Notice', icon: 'bi-exclamation-circle-fill text-warning', bg: 'border-warning' },
            info: { title: 'Notification', icon: 'bi-info-circle-fill text-info', bg: 'border-info' }
        };

        const config = typeMap[type] || typeMap.info;
        if (titleEl) titleEl.textContent = title || config.title;
        if (bodyEl) bodyEl.textContent = message;
        if (iconEl) iconEl.className = `bi ${config.icon} me-2`;

        toastEl.className = `toast align-items-center bg-surface-elevated text-light border ${config.bg}`;

        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    }

    showAILoader(message = 'AI is analyzing your profile & generating insights...') {
        const modalEl = document.getElementById('aiLoadingModal');
        const textEl = document.getElementById('aiLoadingMessage');
        const dismissBtn = document.getElementById('aiModalDismissBtn');
        if (textEl) textEl.textContent = message;
        if (dismissBtn) {
            dismissBtn.style.display = 'none';
            // Fail-safe: Reveal dismiss button after 6 seconds
            clearTimeout(this._aiModalTimeout);
            this._aiModalTimeout = setTimeout(() => {
                if (dismissBtn) dismissBtn.style.display = 'inline-block';
            }, 6000);
        }

        if (modalEl && typeof bootstrap !== 'undefined') {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl, {
                backdrop: 'static',
                keyboard: false
            });
            modal.show();
        }
    }

    hideAILoader() {
        clearTimeout(this._aiModalTimeout);
        const modalEl = document.getElementById('aiLoadingModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
            const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
            if (modal) {
                try {
                    modal.hide();
                } catch (e) {}
            }
        }

        // Defensive cleanup of any remaining backdrops
        setTimeout(() => {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('overflow');
            document.body.style.removeProperty('padding-right');
        }, 300);
    }
}

// Global API instance
window.api = new ApiClient();

// Auto-populate auth state across header/navbar on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const user = window.api.getUser();
    const authNav = document.getElementById('navbarAuthSection');
    const guestNav = document.getElementById('navbarGuestSection');
    const userNameEl = document.getElementById('navbarUserName');
    const userRoleBadge = document.getElementById('navbarUserRole');
    const adminLink = document.getElementById('navbarAdminLink');

    if (user && window.api.isAuthenticated()) {
        if (authNav) authNav.classList.remove('d-none');
        if (guestNav) guestNav.classList.add('d-none');
        if (userNameEl) userNameEl.textContent = user.full_name || user.email.split('@')[0];
        if (userRoleBadge) {
            userRoleBadge.textContent = user.role.toUpperCase();
            userRoleBadge.className = `badge ${user.role === 'admin' ? 'bg-danger' : 'bg-primary'}`;
        }
        
        const studentLinks = document.getElementById('navbarAuthLinks');
        const adminLinks = document.getElementById('navbarAdminAuthLinks');
        const studentMenuItems = document.querySelectorAll('.student-menu-item');
        const adminMenuItems = document.querySelectorAll('.admin-menu-item');

        if (user.role === 'admin') {
            if (studentLinks) studentLinks.classList.add('d-none');
            if (adminLinks) adminLinks.classList.remove('d-none');
            studentMenuItems.forEach(el => el.classList.add('d-none'));
            adminMenuItems.forEach(el => el.classList.remove('d-none'));
        } else {
            if (studentLinks) studentLinks.classList.remove('d-none');
            if (adminLinks) adminLinks.classList.add('d-none');
            studentMenuItems.forEach(el => el.classList.remove('d-none'));
            adminMenuItems.forEach(el => el.classList.add('d-none'));
        }
    } else {
        if (authNav) authNav.classList.add('d-none');
        if (guestNav) guestNav.classList.remove('d-none');
    }

    // Attach logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await window.api.post('/auth/logout', {}, { silent: true });
            } catch (err) {}
            window.api.clearAuth();
            window.api.showToast('You have been logged out.', 'info');
            setTimeout(() => {
                window.location.href = '/login';
            }, 800);
        });
    }
});
