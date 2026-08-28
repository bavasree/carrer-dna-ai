/**
 * Authentication Module: Login, Registration & Demo Fillers
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Login Form Handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';

                const response = await window.api.post('/auth/login', { email, password });
                window.api.setAuth(response.data.token, response.data.user);
                window.api.showToast('Login successful! Redirecting...', 'success');

                const urlParams = new URLSearchParams(window.location.search);
                const redirect = urlParams.get('redirect');

                setTimeout(() => {
                    if (redirect) {
                        window.location.href = redirect;
                    } else if (response.data.user.role === 'admin') {
                        window.location.href = '/admin/dashboard';
                    } else {
                        window.location.href = '/dashboard';
                    }
                }, 800);
            } catch (err) {
                // Toast already shown by api.js
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });

        // Quick Demo Fillers
        const demoStudentBtn = document.getElementById('demoStudentBtn');
        if (demoStudentBtn) {
            demoStudentBtn.addEventListener('click', () => {
                document.getElementById('loginEmail').value = 'student@careerdna.ai';
                document.getElementById('loginPassword').value = 'Student@123';
            });
        }

        const demoAdminBtn = document.getElementById('demoAdminBtn');
        if (demoAdminBtn) {
            demoAdminBtn.addEventListener('click', () => {
                document.getElementById('loginEmail').value = 'admin@careerdna.ai';
                document.getElementById('loginPassword').value = 'Admin@123';
            });
        }
    }

    // 2. Registration Role Toggle (Student vs Admin)
    const careerGoalGroup = document.getElementById('careerGoalGroup');
    const roleRadios = document.querySelectorAll('input[name="regRole"]');
    const btnRegisterSubmit = document.getElementById('btnRegisterSubmit');

    if (roleRadios.length > 0) {
        roleRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                if (radio.checked) {
                    if (radio.value === 'admin') {
                        if (careerGoalGroup) careerGoalGroup.style.display = 'none';
                        if (btnRegisterSubmit) {
                            btnRegisterSubmit.innerHTML = 'Create Admin Account <i class="bi bi-shield-lock ms-1"></i>';
                        }
                    } else {
                        if (careerGoalGroup) careerGoalGroup.style.display = 'block';
                        if (btnRegisterSubmit) {
                            btnRegisterSubmit.innerHTML = 'Create Account & Begin Onboarding <i class="bi bi-arrow-right ms-1"></i>';
                        }
                    }
                }
            });
        });
    }

    // 3. Registration Form Handler
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            const fullName = document.getElementById('regFullName').value.trim();
            const email = document.getElementById('regEmail').value.trim();
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            const role = document.querySelector('input[name="regRole"]:checked')?.value || 'student';
            const careerGoal = document.getElementById('regCareerGoal')?.value.trim() || '';

            if (password !== confirmPassword) {
                window.api.showToast('Passwords do not match.', 'danger');
                return;
            }

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...';

                const response = await window.api.post('/auth/register', {
                    full_name: fullName,
                    email,
                    password,
                    role,
                    career_goal: careerGoal
                });

                window.api.setAuth(response.data.token, response.data.user);
                window.api.showToast('Account created successfully!', 'success');

                setTimeout(() => {
                    if (role === 'admin') {
                        window.location.href = '/admin/dashboard';
                    } else {
                        window.location.href = '/onboarding';
                    }
                }, 1000);
            } catch (err) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
});
