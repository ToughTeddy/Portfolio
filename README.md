# Portfolio

A few small projects that showcase my Python skills, automation, and cloud deployment.

## Projects

### ISS_Tracker
Checks once a minute whether the International Space Station is within ±5° lat/long of my location **and** it’s dark outside. If both are true, it emails me an alert.

- **Highlights:** API polling, time/zonal logic (sunrise/sunset), email notifications
- **Tech:** Python, `requests`, `smtplib`, `datetime`
- **Run it:**

---

### Password_Manager
Stores website, email, and passwords in a JSON file. Autofills email, can autogenerate strong passwords, uses a **binary search tree** for lookups, and copies saved passwords to the clipboard for quick pasting.

- **Highlights:** GUI app, BST-backed storage, password generation, clipboard integration
- **Tech:** Python, Tkinter, JSON

---

### LinkedIn_Daily_Quiz
Posts a Python question to LinkedIn every day using **Azure Functions**. Reads questions from storage and publishes via LinkedIn’s UGC API.

- **Highlights:** Cloud automation/scheduling, API integration, secure config via app settings
- **Tech:** Python, Azure Functions, Azure Blob Storage, LinkedIn API

---

## Repo Structure
