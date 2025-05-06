       // Get modal element
       const modal = document.getElementById('forgotPasswordModal');

       // Get the link that opens the modal
       const forgotPasswordLink = document.getElementById('forgotPasswordLink');

       // Get the <span> element that closes the modal
       const closeModal = document.getElementById('closeModal');

       // Get the submit button
       const submitForgotPassword = document.getElementById('submitForgotPassword');

       // Get the error message element
       const errorMessage = document.getElementById('errorMessage');

       // When the user clicks on the link, open the modal
       forgotPasswordLink.onclick = function(event) {
           event.preventDefault(); // Prevent default link behavior
           modal.style.display = 'block'; // Show the modal
       }

       // When the user clicks on <span> (x), close the modal
       closeModal.onclick = function() {
           modal.style.display = 'none';
       }

       // When the user clicks anywhere outside of the modal, close it
       window.onclick = function(event) {
           if (event.target === modal) {
               modal.style.display = 'none';
           }
       }