# Event_Check_In_Microservice <!-- omit in toc -->
A microservice that generates check in links, QR codes, and forms for even coordinators using the Event Tracker application

- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Run](#run)
- [GET requests](#get-requests)
- [POST requests](#post-requests)


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
      - "5003:5003"
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
All the GET requests our microservice allows

## POST requests
All the POST requests our microservice allows