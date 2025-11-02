/**
 * Profile Page JavaScript
 * Handles profile information display and updates
 */

// Load and display user profile
async function loadUserProfile() {
  try {
    const response = await fetch('/api/profile/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const result = await response.json();
      if (result.success && result.data) {
        displayProfileInfo(result.data);
      } else {
        if (typeof showToast === 'function') {
          showToast('Failed to load profile', 'error');
        }
      }
    } else if (response.status === 401) {
      // Not authenticated - redirect to login
      window.location.href = '/login';
    } else {
      if (typeof showToast === 'function') {
        showToast('Failed to load profile', 'error');
      }
    }
  } catch (error) {
    console.error('Profile load error:', error);
    if (typeof showToast === 'function') {
      showToast('An error occurred loading profile', 'error');
    }
  }
}

// Display profile information
function displayProfileInfo(profile) {
  const usernameEl = document.getElementById('displayUsername');
  const emailEl = document.getElementById('displayEmail');
  const emailStatusEl = document.getElementById('displayEmailStatus');
  const createdAtEl = document.getElementById('displayCreatedAt');
  const lastLoginEl = document.getElementById('displayLastLogin');

  if (usernameEl) usernameEl.textContent = profile.username || 'N/A';
  if (emailEl) emailEl.textContent = profile.email || 'N/A';
  
  if (emailStatusEl) {
    if (profile.email_verified) {
      emailStatusEl.textContent = '✓ Verified';
      emailStatusEl.style.color = 'var(--color-success)';
    } else {
      emailStatusEl.textContent = '✗ Not Verified';
      emailStatusEl.style.color = 'var(--color-error)';
    }
  }

  if (createdAtEl) {
    const createdDate = profile.created_at ? new Date(profile.created_at) : null;
    createdAtEl.textContent = createdDate ? createdDate.toLocaleDateString() : 'N/A';
  }

  if (lastLoginEl) {
    const lastLoginDate = profile.last_login ? new Date(profile.last_login) : null;
    lastLoginEl.textContent = lastLoginDate ? lastLoginDate.toLocaleString() : 'Never';
  }
}

// Initialize update username form
function initUpdateUsernameForm() {
  const form = document.getElementById('updateUsernameForm');
  if (!form) return;

  const usernameInput = document.getElementById('newUsername');
  const submitButton = document.getElementById('updateUsernameButton');
  const buttonText = document.getElementById('updateUsernameButtonText');
  const buttonSpinner = document.getElementById('updateUsernameButtonSpinner');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = usernameInput.value.trim();
    
    if (!username) {
      if (typeof showToast === 'function') {
        showToast('Username is required', 'error');
      }
      return;
    }

    // Disable button
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/profile/username', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Username updated successfully', 'success');
        }
        
        // Reload profile
        await loadUserProfile();
        
        // Clear form
        form.reset();
      } else {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Failed to update username', 'error');
        }
      }
    } catch (error) {
      console.error('Update username error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred', 'error');
      }
    } finally {
      // Re-enable button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize update email form
function initUpdateEmailForm() {
  const form = document.getElementById('updateEmailForm');
  if (!form) return;

  const emailInput = document.getElementById('newEmail');
  const submitButton = document.getElementById('updateEmailButton');
  const buttonText = document.getElementById('updateEmailButtonText');
  const buttonSpinner = document.getElementById('updateEmailButtonSpinner');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    
    if (!email) {
      if (typeof showToast === 'function') {
        showToast('Email is required', 'error');
      }
      return;
    }

    // Disable button
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/profile/email', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Email updated. Please check your new email to verify it.', 'success');
        }
        
        // Reload profile
        await loadUserProfile();
        
        // Clear form
        form.reset();
      } else {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Failed to update email', 'error');
        }
      }
    } catch (error) {
      console.error('Update email error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred', 'error');
      }
    } finally {
      // Re-enable button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize change password form
function initChangePasswordForm() {
  const form = document.getElementById('changePasswordForm');
  if (!form) return;

  const currentPasswordInput = document.getElementById('currentPassword');
  const newPasswordInput = document.getElementById('newPassword');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  const submitButton = document.getElementById('changePasswordButton');
  const buttonText = document.getElementById('changePasswordButtonText');
  const buttonSpinner = document.getElementById('changePasswordButtonSpinner');
  
  const strengthContainer = document.getElementById('passwordStrength');
  const strengthBar = document.getElementById('strengthBar');
  const strengthText = document.getElementById('strengthText');

  // Setup password toggles
  const toggleCurrent = document.getElementById('toggleCurrentPassword');
  const toggleNew = document.getElementById('toggleNewPassword');
  const toggleConfirm = document.getElementById('toggleConfirmPassword');
  
  if (toggleCurrent && currentPasswordInput) {
    toggleCurrent.addEventListener('click', function() {
      const type = currentPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      currentPasswordInput.setAttribute('type', type);
      toggleCurrent.textContent = type === 'password' ? '👁️' : '🙈';
    });
  }
  
  if (toggleNew && newPasswordInput) {
    toggleNew.addEventListener('click', function() {
      const type = newPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      newPasswordInput.setAttribute('type', type);
      toggleNew.textContent = type === 'password' ? '👁️' : '🙈';
    });
  }
  
  if (toggleConfirm && confirmPasswordInput) {
    toggleConfirm.addEventListener('click', function() {
      const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      confirmPasswordInput.setAttribute('type', type);
      toggleConfirm.textContent = type === 'password' ? '👁️' : '🙈';
    });
  }

  // Password strength indicator (reuse from auth.js if available)
  if (newPasswordInput && strengthContainer && strengthBar && strengthText && typeof updatePasswordStrength === 'function') {
    newPasswordInput.addEventListener('input', function() {
      updatePasswordStrength(newPasswordInput.value, strengthContainer, strengthBar, strengthText);
    });
  }

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const currentPassword = currentPasswordInput.value;
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    if (!currentPassword || !newPassword || !confirmPassword) {
      if (typeof showToast === 'function') {
        showToast('All fields are required', 'error');
      }
      return;
    }

    if (newPassword !== confirmPassword) {
      if (typeof showToast === 'function') {
        showToast('New passwords do not match', 'error');
      }
      return;
    }

    // Disable button
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    try {
      const response = await fetch('/api/profile/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Password changed successfully', 'success');
        }
        
        // Clear form
        form.reset();
        if (strengthContainer) {
          strengthContainer.style.display = 'none';
        }
      } else {
        if (typeof showToast === 'function') {
          showToast(data.message || 'Failed to change password', 'error');
        }
      }
    } catch (error) {
      console.error('Change password error:', error);
      if (typeof showToast === 'function') {
        showToast('An error occurred', 'error');
      }
    } finally {
      // Re-enable button
      submitButton.disabled = false;
      buttonText.style.display = 'inline';
      buttonSpinner.style.display = 'none';
    }
  });
}

// Initialize profile page
function initProfilePage() {
  // Load user profile
  loadUserProfile();

  // Initialize forms
  initUpdateUsernameForm();
  initUpdateEmailForm();
  initChangePasswordForm();
}
