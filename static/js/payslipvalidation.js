document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("invoice-form");
    const submitButton = document.getElementById("submit-button");

    submitButton.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent default submission

        let formIsValid = true;
        const fields = form.querySelectorAll("input, textarea, select");

        // Validate all fields
        fields.forEach((field) => {
            if (!validateField(field)) {
                formIsValid = false;
            }
        });

        if (!formIsValid) {
            alert("Please fix the errors in the form before submitting.");
            return; // Stop submission if form is invalid
        }

        form.submit(); // Submit the form if valid
    });

    // Field validation function
    function validateField(field) {
        const errorMessage = getErrorMessageElement(field);
        let valid = true;

        const validators = {
            company_name: () => field.value.trim() !== "",
            company_address: () => field.value.trim() !== "",
            company_contact: () => /^[0-9]{10}$/.test(field.value),
            invoice_date: () => validateDate(field.value),
            gstn: () =>
                /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$/.test(field.value),
            pan: () => /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(field.value),
            invoice_number: () => field.value.trim() !== "",
            total_amount_before_task: () => !isNaN(field.value) && field.value.trim() !== "",
            cgst: () => validateTaxAmount(field.value),
            sgst: () => validateTaxAmount(field.value),
            igst: () => validateTaxAmount(field.value),
            ifsc: () => /^[A-Z]{4}0[A-Z0-9]{6}$/.test(field.value),
            bank_account: () => /^[0-9]{9,18}$/.test(field.value),
            total_in_words: () => field.value.trim().length > 0,
            footer_content: () => field.value.trim().length <= 500,
        };

        if (validators[field.id]) {
            valid = validators[field.id]();
            errorMessage.textContent = valid ? "" : getErrorText(field.id);
        } else if (field.type === "file") {
            const existingFile = field.getAttribute("data-existing-file");
            const isFileUploaded = field.files && field.files.length > 0;
        
            valid = isFileUploaded || (existingFile && existingFile.trim() !== "");
            errorMessage.textContent = valid ? "" : "This field is required.";
        } else {
            // General validation for other fields
            valid = field.value.trim() !== "";
            errorMessage.textContent = valid ? "" : "This field is required.";
        }

        errorMessage.style.display = valid ? "none" : "block";
        field.classList.toggle("is-invalid", !valid);

        return valid;
    }

    // Get or create error message element for a field
    function getErrorMessageElement(field) {
        let errorMessage = field.parentNode.querySelector(".error-message");
        if (!errorMessage) {
            errorMessage = document.createElement("div");
            errorMessage.className = "error-message text-danger";
            field.parentNode.appendChild(errorMessage);
        }
        return errorMessage;
    }

    // Helper function to validate dates
    function validateDate(dateString) {
        const date = new Date(dateString);
        return !isNaN(date.getTime());
    }

    // Helper function to validate tax amounts
    function validateTaxAmount(value) {
        return !isNaN(value) && value >= 0;
    }

    // Get error text based on field ID
    function getErrorText(fieldId) {
        const messages = {
            company_name: "Company name is required.",
            company_address: "Company address is required.",
            company_contact: "Please enter a valid 10-digit phone number.",
            invoice_date: "Please enter a valid date.",
            gstn: "Please enter a valid GST number.",
            pan: "Please enter a valid PAN number.",
            invoice_number: "Invoice number is required.",
            total_amount_before_task: "Please enter a valid amount.",
            cgst: "Please enter a valid tax amount.",
            sgst: "Please enter a valid tax amount.",
            igst: "Please enter a valid tax amount.",
            ifsc: "Please enter a valid IFSC code.",
            bank_account: "Please enter a valid bank account number.",
            total_in_words: "Please enter the total amount in words.",
            footer_content: "Footer content must be 500 characters or fewer.",
        };

        return messages[fieldId] || "Invalid input.";
    }
});
