function validateSignup() {
    var firstName = document.getElementById('new-first-name').value.trim();
    var lastName = document.getElementById('new-last-name').value.trim();
    var email = document.getElementById('new-email').value.trim();
    var phone = document.getElementById('new-phone').value.trim();
    var password = document.getElementById('new-password').value.trim();
    var confirmPassword = document.getElementById('confirm-password').value.trim();

    // Check if fields are empty
    if (firstName === '' || lastName === '' || email === '' || phone === '' || password === '' || confirmPassword === '') {
        alert('Please fill in all fields.');
        return false;
    }

    // Regular expression for email validation
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Check email format
    if (!emailRegex.test(email)) {
        alert('Invalid email format.');
        return false;
    }

    // Check password length
    if (password.length < 8) {
        alert('Password must be at least 8 characters long.');
        return false;
    }

    // Check if passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return false;
    }

    // Form is valid, allow submission
    return true;
}

function validateLogin(){
    email = document.getElementById('email');
    password = document.getElementById('password');

    if(email == "" || password == ""){
        alert("Please fill in all fields");
        return false;
    }

    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Check email format
    if (!emailRegex.test(email)) {
        alert('Invalid email format.');
        return false;
    }
}