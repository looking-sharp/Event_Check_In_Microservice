const form_id = document.getElementById("form_id").textContent;
const loading = document.getElementById("loading");
const content = document.getElementById("content");
const error = document.getElementById("error");

document.addEventListener("DOMContentLoaded", () => {
    fetch(`/get-form/${form_id}`)
        .then(response => response.json())
        .then(data => { 
            console.log(data);
            if (data.status_code != 200) {
                const response_span = document.getElementById("response-span");
                response_span.textContent = data.status_code;
                const className = data.status_code >= 200 && data.status_code < 300? "status-ok" :
                                  data.status_code >= 300 && data.status_code < 400? "status-redirect" :
                                  data.status_code >= 400 && data.status_code < 500? "status-client-error" :
                                  data.status_code >= 500 && data.status_code < 600? "status-server-error" : "status-unknown"
                response_span.classList.add(className)
                const message = document.getElementById("message-p");
                message.textContent = `Message: ${data.message}`
                setTimeout(() => {
                    error.style.display = "grid"
                    loading.style.display = "none";
                }, 500);
                return;
            }
            else {
                // Parse Data


                setTimeout(() => {
                    content.style.display = "block";
                    loading.style.display = "none";
                }, 500);
            }
        });
});