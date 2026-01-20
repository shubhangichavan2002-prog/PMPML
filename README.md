# PMPML TICKET VALIDATION SYSTEM

---

## 1. Introduction
Public transport systems require fast, secure, and reliable ticket validation.  
The **PMPML Ticket Validation System** is a **web-based application** developed using **Flask (Python)** that simulates a real-world bus ticketing system like **PMPML**.

This system allows users to:
- Generate route-based tickets
- Validate tickets using GPS location
- Detect invalid travel beyond destination
- Handle daily bus passes
- Detect network loss and GPS freezing

The project focuses on **route-wise stop validation**, not just destination matching.

---

## 2. Problem Statement
Traditional bus ticketing systems face several problems:
- Manual ticket checking
- No real-time validation
- Tickets reused beyond destination
- No detection of GPS or network failure

There is a need for a **smart ticket validation system** that can:
- Validate tickets automatically
- Restrict travel beyond destination
- Handle GPS freeze and network loss

---

## 3. Objectives
- Develop a smart bus ticketing system
- Validate tickets using **route + GPS**
- Allow travel only between source and destination stops
- Detect GPS freezing
- Detect network disconnection
- Implement daily bus pass functionality
- Simulate real-time bus movement for testing

---

## 4. Scope of the Project
- Web-based system using Flask
- Supports multiple routes and stops
- Route-order-based ticket validation
- Daily pass with expiry handling
- Suitable for **academic projects and demonstrations**

---

## 5. Technologies Used

### Backend
- Python
- Flask
- MySQL
- MySQL Connector

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Template Engine

### Concepts Used
- REST APIs
- Session management
- GPS-based validation
- Route-stop mapping
- Client–server communication

---

## 6. System Architecture
1. User logs in or accesses the system
2. User selects route, source, and destination
3. Ticket is generated and stored in session
4. GPS location is continuously validated
5. Ticket status updates dynamically (VALID / INVALID)
6. Daily pass expiry is checked before validation

---

## 7. Database Design

### Database Name
`userdb`

### Tables Used
| Table Name       | Description |
|-----------------|-------------|
| `users`         | User login details |
| `route`         | Route information |
| `stop`          | Stop details with latitude and longitude |
| `route_stop`    | Mapping of routes and stops with order |
| `ticket`        | Ticket details |
| `validation`    | Ticket validation logs |
| `payment`       | Payment details |
| `schedule`      | Route schedule information |
| `schedule_stop` | Schedule and stop mapping |

---

## 8. Daily Pass Functionality
- Users can generate a **Daily Bus Pass**
- Pass contains:
  - Pass ID
  - Expiry time
- System validation:
  - Active pass → **VALID**
  - Expired pass → **INVALID**
- Expired passes are shown but cannot be used

---

## 9. GPS and Network Failure Detection

### GPS Freeze Detection
- If GPS location is not updated for a fixed time
- Ticket status becomes **GPS NOT RESPONDING**

### Network Loss Detection
- If internet connection is lost
- Ticket status shows **NETWORK LOST**

---

## 10. Project Structure
PMPML/
│
├── app.py
├── README.md
├── templates/
│ ├── login.html
│ ├── register.html
│ ├── home.html
│ ├── ticket_form.html
│ ├── ticket.html
│ └── pass.html
│
├── static/
│ ├── css/
│ └── js/
│
└── database.sql


---

## 11. How to Run the Project

### Step 1: Install Dependencies
```bash
pip install flask mysql-connector-python

### Step 2: Create Database
1. Open MySQL Command Line or MySQL Workbench  
2. Create a database named **userdb**:

```sql
CREATE DATABASE userdb;

`USE userdb;`

### Step 3: Configure Database

``` host="localhost"
user="your_mysql_username"
password="your_mysql_password"
database="userdb"
```
### Step 4: Run Application
python app.py

### Step 5: Open in Browser
http://127.0.0.1:5000


### Project Purpose

This project is created for:

- Academic learning

- Web development practice

- Understanding GPS-based validation systems

Real-world public transport system simulation

### Author

- Name: Shubhangi Chavan
- Project Type: Academic / Learning Project
- Technology: Flask (Python)


