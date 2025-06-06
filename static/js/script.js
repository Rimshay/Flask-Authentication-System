document.addEventListener('DOMContentLoaded', () => {

  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById("togglePassword");
  const message = document.getElementById('passwordMessage');

  const usernameInput = document.getElementById('username');
  const usernameMessage = document.getElementById('usernameMessage');

  if (passwordInput && message) {
    if (!passwordInput || !message) {
        console.warn("Password input or message element not found!");
        return;
    }
  }

  if (togglePassword) {
    togglePassword.addEventListener("click", function () {
      console.log("Eye icon clicked!");
      const isPassword = passwordInput.type === "password";
      passwordInput.type = isPassword ? "text" : "password";
      this.classList.toggle("fa-eye");
      this.classList.toggle("fa-eye-slash");
    });

  }

  
  if (passwordInput && message) {
    passwordInput.addEventListener('input', () => {
    const password = passwordInput.value;
    const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    if (!password) {
      message.textContent = '';
      message.style.color = '';
    } else if (!pattern.test(password)) {
      message.textContent = '❌ Weak Password';
      message.style.color = 'red';
    } else {
      message.textContent = '✅ Strong Password';
      message.style.color = 'green';
    }
    });  // <-- ✅ This was missing

  }


  if (usernameInput && usernameMessage) {
    usernameInput.addEventListener('input', () => {
      const username = usernameInput.value;

      // Allow only alphabets
      const isValid = /^[A-Za-z]+$/.test(username);

      if (!username) {
        usernameMessage.textContent = '';
        usernameMessage.style.color = '';
      } else if (!isValid) {
        usernameMessage.textContent = '❌ Username should only contain letters. No numbers or special characters.';
        usernameMessage.style.color = 'red';
      } else {
        usernameMessage.textContent = '✅ Valid username';
        usernameMessage.style.color = 'green';
      }
    });
  }

  const emailInput = document.getElementById('email');
  const emailMessage = document.getElementById('emailMessage');

  if (emailInput && emailMessage) {
    emailInput.addEventListener('input', () => {
    const email = emailInput.value;

      // Basic email format check before server call
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(email)) {
        emailMessage.textContent = 'Invalid email format';
        emailMessage.style.color = 'red';
        return;
      }

      // Clear message if format valid, check server
      fetch('/check_email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      })
      .then(response => response.json())
      .then(data => {
        if (data.exists) {
          emailMessage.textContent = 'Email already registered';
          emailMessage.style.color = 'red';
        } else {
          emailMessage.textContent = 'Email available';
          emailMessage.style.color = 'green';
        }
      })
      .catch(() => {
        emailMessage.textContent = 'Error checking email';
        emailMessage.style.color = 'orange';
      });
    });
  }

});

