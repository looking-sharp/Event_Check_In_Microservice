const form_id = document.getElementById("form_id").textContent;
const loading = document.getElementById(`loading-${form_id}`);
const content = document.getElementById(`content-${form_id}`);
const error = document.getElementById(`error-${form_id}`);
const form = document.getElementById(`form-holder-${form_id}`)

document.addEventListener("DOMContentLoaded", () => {
    fetch(`/get-form/${form_id}`)
        .then(response => response.json())
        .then(data => { 
            console.log(data);
            if (data.status_code != 200) {
                const response_span = document.getElementById(`response-span-${form_id}`);
                response_span.textContent = data.status_code;
                const className = data.status_code >= 200 && data.status_code < 300? "status-ok" :
                                  data.status_code >= 300 && data.status_code < 400? "status-redirect" :
                                  data.status_code >= 400 && data.status_code < 500? "status-client-error" :
                                  data.status_code >= 500 && data.status_code < 600? "status-server-error" : "status-unknown"
                response_span.classList.add(className)
                const message = document.getElementById(`message-p-${form_id}`);
                message.textContent = `Message: ${data.message}`
                setTimeout(() => {
                    error.style.display = "grid"
                    loading.style.display = "none";
                }, 500);
                return;
            }
            else {
                // Parse Data
                const name = document.getElementById(`form-name-${form_id}`);
                name.textContent = `Check In for: ${data.form_name}`;
                data.fields.forEach(field => {
                    console.log(field)
                    form.innerHTML += `
                    <label for="${field.label}">${field.label}:</label>
                    <input type="${field.field_type}" id="${field.field_id}" name="${field.label}" maxlength="255" ${field.required ? "required" : ""}>
                    `;
                });
                form.innerHTML += `<button type="submit">Check In</button>`;
                setTimeout(() => {
                    content.style.display = "block";
                    loading.style.display = "none";
                }, 500);
            }
        });
});