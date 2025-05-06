document.addEventListener("DOMContentLoaded", function () {
    var form = document.querySelector('.php-email-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission behavior
        let thisForm = this;

        let action = thisForm.getAttribute('action');

        if( ! action ) {
          displayError(thisForm, 'The form action property is not set!')
          return;
        }
        thisForm.querySelector('.loading').classList.add('d-block');
        thisForm.querySelector('.error-message').classList.remove('d-block');
        thisForm.querySelector('.sent-message').classList.remove('d-block');

        var formData = new FormData(form);
  
        fetch(form.action, { // Send an AJAX request to the form's action URL
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}, // Set a custom header to identify the request as AJAX
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server responded with an error');
            }

            return response.json();
        })
        .then(data => {
            form.querySelector('.loading').classList.remove('d-block');
            if (data && data.msg === 'OK') {
                form.querySelector('.sent-message').classList.add('d-block');
                form.reset();
            } else {
                throw new Error(data ? data.error : 'Form submission failed');
            }
        })
        .catch((error) => {
            form.querySelector('.error-message').textContent = error;
        });
    });
  });
  
   
  document.addEventListener('DOMContentLoaded', function() {

    // Function to validate name
    function validateName() {
      var nameInput = document.getElementById('name');
      if (!/^[a-zA-Z\s]*$/.test(nameInput.value)) {
        document.querySelector('.validate_name').textContent = 'Name should contain alphabets and spaces only.';
        nameInput.value = '';
      } else {
        document.querySelector('.validate_name').textContent = '';
      }
    }
  
    // Event listener for name input change
    document.getElementById('name').addEventListener('input', validateName);
  
  });
  

document.addEventListener('DOMContentLoaded', function() {
  // Function to validate mobile number length
  function validateMobileNumber() {
    var mobileInput = document.getElementById('contact');
    var mobileNumber = mobileInput.value.replace(/\D/g, '');
    if (mobileNumber.length !== 10) {
      document.querySelector('.validate_number').textContent = 'Mobile number should be 10 digits.';
      mobileInput.value = ''; 
    } else {
      document.querySelector('.validate_number').textContent = '';
    }
  }
  // Event listener for mobile number input change
  document.getElementById('contact').addEventListener('blur', validateMobileNumber);

});


  