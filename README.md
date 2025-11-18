# Event_Check_In_Microservice <!-- omit in toc -->
A microservice that generates check in links, QR codes, and forms for even coordinators using the Event Tracker application

- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Run](#run)
- [GET requests](#get-requests)
  - [`GET /health`](#get-health)
  - [`GET /get-check-in-front-page`](#get-get-check-in-front-page)
  - [`GET /get-form/<form_id>`](#get-get-formform_id)
  - [`GET /check-submissions`](#get-check-submissions)
  - [`GET /check-in/<form_id>`](#get-check-inform_id)
- [POST requests](#post-requests)
  - [`POST /create-check-in-form`](#post-create-check-in-form)
  - [`POST /delete-form`](#post-delete-form)


## Quick Start

### Prerequisites

- Python 3.9+
- Docker Desktop Installed

### Installation
```bash
# Clone repository into your main project
git clone https://github.com/yourusername/event-check-in-microservice.git

# Make data directory for database storage
mkdir data

# create .env file
cd Event-Check-In-Microservice
touch .env
```
Outside the created repository in your main project folder:
```bash
# Created a docker compose file
touch docker-compose.yml
```
And add the following into your compose file:
```yml
services:
  event-check-in-microservice:
    build: ./Event_Check_In_Microservice
    image: event-check-in-microservice
    ports:
      - "500X:500X"
    environment:
      FLASK_APP: app.py
      FLASK_ENV: development
      DATABASE_URL: sqlite:////app_parent/data/checkin.db
    volumes:
      - ./Event_Check_In_Microservice/..:/app_parent
```

If your set up is correct, your file tree will look something like this:
```bash
YOUR_PROJECT
├── data
├── Event_Check_In_Microservice
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├──  ...
│   ├── static
│   │   ├── scripts
│   │   │   └── checkin.js
│   │   └── styles
│   │       ├── checkin.css
│   │       └──  ...
│   └── template
│       ├── checkin.html
│       └──  ...
└── docker-compose.yml
```

> [!IMPORTANT]
> You must have a data directory in the directory of YOUR_PROJECT

### Run
If you haven't built it yet, in your main project directory (the one with `docker-compose.yml` in it) run:
```bash
docker-compose up --build event-check-in-microservice
```
Or if you have built it,
``` bash
docker-compose up --no-build event-check-in-microservice
```

## GET requests
All the public GET requests our microservice allows

### `GET /health`
This pings the microservice to ensure it is running and ready to recieve requests

**Response (200):**
```json
{
  "message": "Event Check In Microservice Online"
}
```

**Example Code (Python)**
``` python
import requests

def checkIsOnline() -> bool:
    try:
        response = requests.get("http://127.0.0.1:500X/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False
```
---

### `GET /get-check-in-front-page`
This displays the front page for the check in form for your event. Has both a QR code, and link to the check in form.

**Args**
```bash
# the ID / Token given on form initilization
formID: abcdefg-123456-xxxxxxxxxxxxx
```

**Response (200)**
Renders a html file with the information related to formID

**Example Code (Python)**
``` python
from flask import redirect

form_id = "abcdefg-123456-xxxxxxxxxxxxx"

def go_to_front_page():
    # Redirect to the front page for the check-in form
    return redirect(f"http://localhost:500X/get-check-in-front-page?formID={form_id}")
```
---

### `GET /get-form/<form_id>`
Returns the json version of the form where the form's url_id = form_id

**Response (200)**
```json
"id": "form_id",
"event_id": "event_id",
"url_id": "url_id",
"form_name": "form_name",
"submissions": "submissions",
"fields": [
    {
        "id": "id",
        "field_id": "fld_X"
        "field_type": "field_type",
        "field_name": "field_name",
        "label": "label",
        "value": "value",
        "required": "required",
        "options": "options"
    }
],
"status_code": 200
```

**Example Code (Python)**
``` python
import requests

form_id = "abcdefg-123456-xxxxxxxxxxxxx"
    
def get_form_json():
    url = f"http://localhost:500X/get-form/{form_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        form_data = response.json()
        return form_data
    else:
        print(f"Failed to get form: {response.status_code}")
        return None
```
---

### `GET /check-submissions`

**Args**
```bash
# the ID / Token given on form initilization
formID: abcdefg-123456-xxxxxxxxxxxxx
# if you want the submissions as a html string
asString: True or False
```

**Response (200) (asString=False)**
Renders a html file with the information related to form's submissions

**Response (200) (asString=True)**
```json
{
    "html": "<table>...HTML string with embedded CSS...</table>"
}
```

**Example Code (Python)**
```python
import requests

form_id = "abcdefg-123456-xxxxxxxxxxxxx"

def get_submissions(as_string=False):
    url = "http://localhost:500X/check-submissions"
    params = {
        "formID": form_id,
        "asString": as_string
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        if as_string:
            return response.json().get("html")
        else:
            return response.text
```
---

### `GET /check-in/<form_id>`
Renders the check in form for the form's id = form_id

**Example Code (Python)**
```python
from flask import redirect

form_id = "abcdefg-123456-xxxxxxxxxxxxx"

def go_to_check_in_form():
    return redirect(f"http://localhost:500X/check-in/{form_id}")
```

## POST requests
All the public POST requests our microservice allows

### `POST /create-check-in-form`
This takes a JSON payload and creates a custom HTML form based on the given input.

**Request**
```json
"event_id": "string",
"event_name": "string",
"event_date": "DateTime",
"fields": [
    {
        "field_id": "fld_X"
        "field_type": "field_type",
        "field_name": "field_name",
        "label": "label",
        "value": "value",
        "required": "required",
        "options": ["option1", "option2", "..."]
    }
],
```

|Field|Required|Notes|
|-----|--------|-----|
|event_id|yes|the id to your event you want to connect this form to|
|event_name|yes|the name of your event|
|event_date|yes|the date your event happens|

**For Fields:**

|Field|Required|Notes|
|-----|--------|-----|
|field_id|no|will be asigned automatically if not provided|
|field_type|no|will be assigned "text" if not provided|
|field_name|yes|the name that will show up with the responses|
|label|yes|what the user will see next to the input|
|value|no|assigned a default value to the input|
|required|yes|if the field is required|
|options|no|For fields like radio and checkbox, you can create them with multiple values|

**Response (200):**
```json
{
    "message": "form created successfully",
    "form_id": "id",
    "form_url_id": "url_id",
    "form_expires_on": "delete_on date"
}
```

**Example Code (Python)**
```python
import requests

payload = {
  "event_id": "evt_12346",
  "event_name": "TEST SUBMIT",
  "event_date": datetime.now(timezone.utc).isoformat(),
  "fields": [
    {
      "field_id": "fld_1",
      "field_type": "text",
      "field_name": "full_name",
      "label": "Full Name",
      "required": True
    },
    {
      "field_id": "fld_2",
      "field_type": "email",
      "field_name": "email",
      "label": "Email",
      "required": False
    },
    {
      "field_id": "fld_17",
      "field_type": "checkbox",
      "field_name": "food_items",
      "label": "Food Items:",
      "options": ["Chicken", "Donuts", "Beans", "Cake", "Cupcakes"],
      "required": False
    }]
}

response = requests.post("http://localhost:500X/create-check-in-form", json=payload)
print(response)

```
---

### `POST /delete-form`
This deletes a form given an appropiate form id

**Request Args**
```bash
# the ID / Token given on form initilization
formID: abcdefg-123456-xxxxxxxxxxxxx
```

**Response (200)**
```json 
{
    "message": "Form sucessfully deleted"
}
```

**Example Code (Python)**
```python
import requests

form_id = "abcdefg-123456-xxxxxxxxxxxxx"

def delete_form():
    url = "http://localhost:500X/delete-form"
    params = {"formID": form_id}
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print(f"Failed to delete form: {response.status_code}")
```
---