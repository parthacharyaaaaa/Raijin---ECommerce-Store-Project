function validateForm() {
    var name = document.getElementById('nameInput').value.trim();
    var phone = document.getElementById('phoneInput').value.trim();
    var email = document.getElementById('emailInput').value.trim();
    var comment = document.getElementById('comment').value.trim();


    
    if (name === '' || phone === '' || email === '' || comment === '') {
        alert('Please fill in all fields.');
        return false;
    }
    
    // Check name length
    if (name.length > 50) {
        alert('Name is too long. Maximum length is 50 characters.');
        return false;
    }
    
    // Check phone number length
    if (phone.length !== 10) {
        alert('Invalid phone number. Please enter a 10-digit phone number.');
        return false;
    }
    
    // Check email format
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Invalid email format.');
        return false;
    }

    // Check comment length
    if (comment.length > 500) {
        alert('Comment is too long. Maximum length is 500 characters.');
        return false;
    }

    // Form is valid, allow submission
    return true;
}
