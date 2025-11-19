const url_id = document.getElementById("url_id").textContent;
const loading = document.getElementById(`loading-${url_id}`);
const content = document.getElementById(`content-${url_id}`);
const error = document.getElementById(`error-${url_id}`);
const form = document.getElementById(`form-holder-${url_id}`)

const side_by_side_elements = ["checkbox", "number", "color", "radio", "date", "time", "datetime-local", "datetime"];

function addField(field) {
    if(field.options != null) {
        const options = field.options.split(",");
        if(field.field_type != "select") {
            var newInnerHtml = "";
            var optionNum = 0;
            newInnerHtml += `<fieldset><legend>${field.label}<span class="required">${field.required ? " *" : ""}</span></legend>`;
            options.forEach(option => {
                optionNum++;
                newInnerHtml += `
                <div class="side-by-side-div">
                <label for="${option}">${option}</label>
                <input type="${field.field_type}" id="${field.field_id}" value="${option}" name="${field.field_name}" ${field.required && optionNum==1 ? "required" : ""}>
                </div>`;
            });
            newInnerHtml += `</fieldset>`;
            form.innerHTML += newInnerHtml;
        }
        else {
            var newInnerHtml = "";
            newInnerHtml += 
            `<div class="side-by-side-div"><label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
             <select id="${field.field_id}" name="${field.field_name}">`;
            options.forEach(option => {
                newInnerHtml += `
                <option value="${option}">${option}</option>`;
            });
            newInnerHtml += `</select></div>`
            form.innerHTML += newInnerHtml;
        }
    }
    else if (field.field_type == "hidden") {
        form.innerHTML += `
        <label style="display: none;" for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
        <input type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""}>`;
    }
    else if (field.field_type == "textarea") {
        form.innerHTML += `
        <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
        <textarea id="${field.field_id}" name="${field.field_name}" ${field.required ? "required" : ""} rows="5" cols="50"></textarea>`;
    }
    else if(side_by_side_elements.includes(field.field_type)) {
        form.innerHTML += `
        <div class="side-by-side-div">
        <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
        <input type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>
        </div>`;
    }
    else {
        form.innerHTML += `
        <label for="${field.label}">${field.label}:<span class="required">${field.required ? "*" : ""}</span></label>
        <input type="${field.field_type}" id="${field.field_id}" name="${field.field_name}" maxlength="255" ${field.required ? "required" : ""}>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetch(`/get-form/${url_id}`)
        .then(response => response.json())
        .then(data => { 
            console.log(data);
            if (data.status_code != 200) {
                const response_span = document.getElementById(`response-span-${url_id}`);
                response_span.textContent = data.status_code;
                const className = data.status_code >= 200 && data.status_code < 300? "status-ok" :
                                  data.status_code >= 300 && data.status_code < 400? "status-redirect" :
                                  data.status_code >= 400 && data.status_code < 500? "status-client-error" :
                                  data.status_code >= 500 && data.status_code < 600? "status-server-error" : "status-unknown"
                response_span.classList.add(className)
                const message = document.getElementById(`message-p-${url_id}`);
                message.textContent = `Message: ${data.message}`
                setTimeout(() => {
                    error.style.display = "grid"
                    loading.style.display = "none";
                }, 500);
                return;
            }
            else {
                // Parse Data
                const name = document.getElementById(`form-name-${url_id}`);
                name.textContent = `Check In for: ${data.form_name}`;
                data.fields.forEach(field => {
                    console.log(field);
                    addField(field);
                });
                form.innerHTML += `<button type="submit">Check In</button>`;
                setTimeout(() => {
                    content.style.display = "block";
                    loading.style.display = "none";
                }, 500);
            }
        });
});