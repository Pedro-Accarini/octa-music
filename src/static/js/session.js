/**
 * Session Management JavaScript
 * Handles session timeout warnings and checks
 */

// Session timeout configuration (in milliseconds)
const SESSION_TIMEOUT = 80 * 60 * 1000; // 80 minutes
const WARNING_TIME = 70 * 60 * 1000; // 70 minutes (10 min before timeout)
const CHECK_INTERVAL = 5 * 60 * 1000; // Check every 5 minutes

let sessionStartTime = null;
let sessionCheckInterval = null;
let warningShown = false;

// Initialize session monitoring
function initSessionMonitoring() {
  // Check if user is authenticated
  checkSession().then(isAuthenticated => {
    if (isAuthenticated) {
      sessionStartTime = Date.now();
      startSessionChecks();
    }
  });
}

// Check session validity
async function checkSession() {
  try {
    const response = await fetch('/api/auth/session-check', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      return data.authenticated || false;
    }
    return false;
  } catch (error) {
    console.error('Session check error:', error);
    return false;
  }
}

// Start session monitoring intervals
function startSessionChecks() {
  // Check session elapsed time every minute
  setInterval(() => {
    if (!sessionStartTime) return;

    const elapsed = Date.now() - sessionStartTime;
    
    // Show warning at 70 minutes
    if (elapsed >= WARNING_TIME && !warningShown) {
      showSessionWarning();
      warningShown = true;
    }
    
    // Session expired at 80 minutes
    if (elapsed >= SESSION_TIMEOUT) {
      handleSessionExpired();
    }
  }, 60 * 1000); // Check every minute

  // Verify session with server every 5 minutes
  sessionCheckInterval = setInterval(async () => {
    const isAuthenticated = await checkSession();
    
    if (!isAuthenticated && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
      handleSessionExpired();
    }
  }, CHECK_INTERVAL);
}

// Show session warning (10 minutes before timeout)
function showSessionWarning() {
  if (typeof showToast === 'function') {
    showToast('Your session will expire in 10 minutes.', 'warning');
  }
}

// Handle session expiration
function handleSessionExpired() {
  // Clear intervals
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
  }
  
  // Show expiration message
  if (typeof showToast === 'function') {
    showToast('Your session has expired. Please login again.', 'error');
  }
  
  // Redirect to login after a short delay
  setTimeout(() => {
    window.location.href = '/login';
  }, 2000);
}

// Update navbar based on authentication state
async function updateNavbar() {
  const isAuthenticated = await checkSession();
  
  const userMenu = document.querySelector('.user-menu');
  if (!userMenu) return;

  // Get existing menu items
  const homeLink = userMenu.querySelector('a[href="/"]');
  
  // Clear menu except home link
  while (userMenu.children.length > 1) {
    userMenu.removeChild(userMenu.lastChild);
  }

  if (isAuthenticated) {
    // Add Profile link
    const profileLink = document.createElement('a');
    profileLink.href = '/profile';
    profileLink.textContent = 'Profile';
    userMenu.appendChild(profileLink);

    // Add Logout link
    const logoutLink = document.createElement('a');
    logoutLink.href = '#';
    logoutLink.textContent = 'Logout';
    logoutLink.addEventListener('click', handleLogout);
    userMenu.appendChild(logoutLink);
  } else {
    // Add Login link
    const loginLink = document.createElement('a');
    loginLink.href = '/login';
    loginLink.textContent = 'Login';
    userMenu.appendChild(loginLink);

    // Add Register link
    const registerLink = document.createElement('a');
    registerLink.href = '/register';
    registerLink.textContent = 'Register';
    userMenu.appendChild(registerLink);
  }
}

// Handle logout
async function handleLogout(e) {
  if (e) e.preventDefault();
  
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok && data.success) {
      if (typeof showToast === 'function') {
        showToast(data.message || 'Logged out successfully', 'success');
      }
      
      // Clear session monitoring
      if (sessionCheckInterval) {
        clearInterval(sessionCheckInterval);
      }
      sessionStartTime = null;
      warningShown = false;
      
      // Redirect to home
      setTimeout(() => {
        window.location.href = '/';
      }, 1000);
    } else {
      if (typeof showToast === 'function') {
        showToast('Logout failed', 'error');
      }
    }
  } catch (error) {
    console.error('Logout error:', error);
    if (typeof showToast === 'function') {
      showToast('An error occurred', 'error');
    }
  }
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    updateNavbar();
    initSessionMonitoring();
  });
} else {
  updateNavbar();
  initSessionMonitoring();
}
