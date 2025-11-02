/**
 * Authentication JavaScript
 * Handles login, register, password reset forms with validation
 */

// Utility function to calculate password strength
function calculatePasswordStrength(password) {
  let score = 0;
  const feedback = [];

  // Length check
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (password.length >= 16) score += 1;

  // Character variety checks
  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add lowercase letters');
  }

  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add uppercase letters');
  }

  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add numbers');
  }

  if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add special characters');
  }

  // Determine strength level
  let strength = 'weak';
  if (score <= 2) strength = 'weak';
  else if (score <= 4) strength = 'fair';
  else if (score <= 6) strength = 'good';
  else strength = 'strong';

  return {
    score: score,
    max_score: 7,
    strength: strength,
    feedback: feedback
  };
}

// Update password strength indicator
function updatePasswordStrength(password, strengthContainer, strengthBar, strengthText) {
  if (!password) {
    strengthContainer.style.display = 'none';
    return;
  }

  strengthContainer.style.display = 'block';
  const result = calculatePasswordStrength(password);
  
  // Update progress bar
  const percentage = (result.score / result.max_score) * 100;
  strengthBar.style.width = percentage + '%';
  strengthBar.className = 'password-strength-progress ' + result.strength;
  
  // Update text
  let text = 'Password strength: ' + result.strength.charAt(0).toUpperCase() + result.strength.slice(1);
  if (result.feedback.length > 0) {
    text += ' (' + result.feedback.join(', ') + ')';
  }
  strengthText.textContent = text;
  strengthText.className = 'password-strength-text ' + result.strength;
}

// Setup password toggle buttons
function setupPasswordToggle(toggleButton, passwordInput) {
  if (!toggleButton || !passwordInput) return;
  
  toggleButton.addEventListener('click', function() {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    toggleButton.textContent = type === 'password' ? '👁️' : '🙈';
  });
}

// Show field error
function showFieldError(fieldId, message) {
  const errorElement = document.getElementById(fieldId + '-error');
  const inputElement = document.getElementById(fieldId);
  
  if (errorElement) {
    errorElement.textContent = message;
  }
  if (inputElement) {
    inputElement.classList.add('error');
  }
}

// Clear field error
function clearFieldError(fieldId) {
  const errorElement = document.getElementById(fieldId + '-error');
  const inputElement = document.getElementById(fieldId);
  
  if (errorElement) {
    errorElement.textContent = '';
  }
  if (inputElement) {
    inputElement.classList.remove('error');
  }
}

// Clear all field errors
function clearAllFieldErrors() {
  const errorElements = document.querySelectorAll('.field-error');
  errorElements.forEach(el => el.textContent = '');
  
  const inputElements = document.querySelectorAll('.auth-input.error');
  inputElements.forEach(el => el.classList.remove('error'));
}

// Initialize login form
function initLoginForm() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const loginInput = document.getElementById('login');
  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById('togglePassword');
  const submitButton = document.getElementById('loginButton');
  const buttonText = document.getElementById('loginButtonText');
  const buttonSpinner = document.getElementById('loginButtonSpinner');

  // Setup password toggle
  setupPasswordToggle(togglePassword, passwordInput);

  // Form submission
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearAllFieldErrors();

    const login = loginInput.value.trim();
    const password = passwordInput.value;
    const rememberMe = document.getElementById('remember_me')?.checked || false;

    // Basic validation
    if (!login) {
      showFieldError('login', 'Email or username is required');
      return;
    }
    if (!password) {
      showFieldError('password', 'Password is required');
      return;
    }

    // Disable submit button and show loading
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          login: login,
          password: password,
          remember_me: rememberMe
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Show success message
        if (typeof showToast === 'function') {
          showToast(data.message || 'Login successful!', 'success');
        }
        
        // Redirect to home page
        setTimeout(() => {
          window.location.href = '/';
        }, 1000);
      } else {
        // Show error
        if (typeof showToast === 'function') {
          showToast(data.message || 'Login failed. Please try again.', 'error');
        }
        
        // Re-enable submit button
        submitButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonSpinner.style.display = 'none';
      }
    } catch (error) {
      console.error('Login error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred. Please try again.', 'error');
      }
      
      // Re-enable submit button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize register form
function initRegisterForm() {
  const form = document.getElementById('registerForm');
  if (!form) return;

  const usernameInput = document.getElementById('username');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm_password');
  const togglePassword = document.getElementById('togglePassword');
  const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
  const submitButton = document.getElementById('registerButton');
  const buttonText = document.getElementById('registerButtonText');
  const buttonSpinner = document.getElementById('registerButtonSpinner');
  
  const strengthContainer = document.getElementById('passwordStrength');
  const strengthBar = document.getElementById('strengthBar');
  const strengthText = document.getElementById('strengthText');

  // Setup password toggles
  setupPasswordToggle(togglePassword, passwordInput);
  setupPasswordToggle(toggleConfirmPassword, confirmPasswordInput);

  // Password strength indicator
  if (passwordInput && strengthContainer && strengthBar && strengthText) {
    passwordInput.addEventListener('input', function() {
      updatePasswordStrength(passwordInput.value, strengthContainer, strengthBar, strengthText);
    });
  }

  // Form submission
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearAllFieldErrors();

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Basic validation
    let hasError = false;

    if (!username) {
      showFieldError('username', 'Username is required');
      hasError = true;
    } else if (username.length < 3 || username.length > 30) {
      showFieldError('username', 'Username must be 3-30 characters');
      hasError = true;
    } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      showFieldError('username', 'Username can only contain letters, numbers, underscores, and dashes');
      hasError = true;
    }

    if (!email) {
      showFieldError('email', 'Email is required');
      hasError = true;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showFieldError('email', 'Please enter a valid email address');
      hasError = true;
    }

    if (!password) {
      showFieldError('password', 'Password is required');
      hasError = true;
    } else if (password.length < 8) {
      showFieldError('password', 'Password must be at least 8 characters');
      hasError = true;
    }

    if (!confirmPassword) {
      showFieldError('confirm_password', 'Please confirm your password');
      hasError = true;
    } else if (password !== confirmPassword) {
      showFieldError('confirm_password', 'Passwords do not match');
      hasError = true;
    }

    if (hasError) return;

    // Disable submit button and show loading
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Show success message
        if (typeof showToast === 'function') {
          showToast(data.message || 'Registration successful! Please check your email.', 'success');
        }
        
        // Redirect to login page
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        // Show error
        if (typeof showToast === 'function') {
          showToast(data.message || 'Registration failed. Please try again.', 'error');
        }
        
        // Re-enable submit button
        submitButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonSpinner.style.display = 'none';
      }
    } catch (error) {
      console.error('Registration error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred. Please try again.', 'error');
      }
      
      // Re-enable submit button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize reset request form
function initResetRequestForm() {
  const form = document.getElementById('resetRequestForm');
  if (!form) return;

  const emailInput = document.getElementById('email');
  const submitButton = document.getElementById('resetButton');
  const buttonText = document.getElementById('resetButtonText');
  const buttonSpinner = document.getElementById('resetButtonSpinner');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearAllFieldErrors();

    const email = emailInput.value.trim();

    if (!email) {
      showFieldError('email', 'Email is required');
      return;
    }

    // Disable submit button and show loading
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/auth/reset-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
      });

      const data = await response.json();

      // Always show generic success message for security
      if (typeof showToast === 'function') {
        showToast(data.message || 'If the email exists, a reset link has been sent.', 'success');
      }
      
      // Clear form
      form.reset();
      
      // Re-enable submit button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    } catch (error) {
      console.error('Reset request error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred. Please try again.', 'error');
      }
      
      // Re-enable submit button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize reset password form
function initResetPasswordForm() {
  const form = document.getElementById('resetPasswordForm');
  if (!form) return;

  const tokenInput = document.getElementById('token');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm_password');
  const togglePassword = document.getElementById('togglePassword');
  const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
  const submitButton = document.getElementById('resetPasswordButton');
  const buttonText = document.getElementById('resetPasswordButtonText');
  const buttonSpinner = document.getElementById('resetPasswordButtonSpinner');
  
  const strengthContainer = document.getElementById('passwordStrength');
  const strengthBar = document.getElementById('strengthBar');
  const strengthText = document.getElementById('strengthText');

  // Setup password toggles
  setupPasswordToggle(togglePassword, passwordInput);
  setupPasswordToggle(toggleConfirmPassword, confirmPasswordInput);

  // Password strength indicator
  if (passwordInput && strengthContainer && strengthBar && strengthText) {
    passwordInput.addEventListener('input', function() {
      updatePasswordStrength(passwordInput.value, strengthContainer, strengthBar, strengthText);
    });
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    clearAllFieldErrors();

    const token = tokenInput.value;
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    let hasError = false;

    if (!password) {
      showFieldError('password', 'Password is required');
      hasError = true;
    } else if (password.length < 8) {
      showFieldError('password', 'Password must be at least 8 characters');
      hasError = true;
    }

    if (!confirmPassword) {
      showFieldError('confirm_password', 'Please confirm your password');
      hasError = true;
    } else if (password !== confirmPassword) {
      showFieldError('confirm_password', 'Passwords do not match');
      hasError = true;
    }

    if (hasError) return;

    // Disable submit button and show loading
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch(`/api/auth/reset-password/${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          password: password,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Password changed successfully!', 'success');
        }
        
        // Redirect to login
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      } else {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Password reset failed. Please try again.', 'error');
        }
        
        // Re-enable submit button
        submitButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonSpinner.style.display = 'none';
      }
    } catch (error) {
      console.error('Reset password error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred. Please try again.', 'error');
      }
      
      // Re-enable submit button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}
