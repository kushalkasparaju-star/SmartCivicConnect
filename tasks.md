# Neighborhood Complaint & Feedback System – Project Tasks

This tasks.md will guide the entire development process. Follow each step in order. Place your **cursor** where indicated to build the full project.

---

## 1. Project Overview

* Build a Python Desktop Application using **Tkinter (GUI)** and **SQLite (DB)**.
* Purpose: Citizens can report local issues (roads, street lights, sanitation, etc.), view progress, and administrators can manage and resolve complaints.
* Impact: Improves civic engagement and accountability.

---

## 2. Folder Structure (to be created)

```
project_root/
│-- gui/
│   ├── login_gui.py
│   ├── register_gui.py
│   ├── user_dashboard.py
│   ├── complaint_form.py
│   └── admin_dashboard.py
│
│-- database/
│   ├── db_connection.py
│   └── create_tables.py
│
│-- logic/
│   ├── auth.py
│   └── complaint_manager.py
│
│-- assets/
│   └── icons, images, etc.
│
│-- utils/
│   └── helper_functions.py
│
│-- main.py
│-- tasks.md (this file)
│-- requirements.txt
```

---

## 3. Step-by-Step Development Tasks

### ✅ Step 1: Initialize Project

* Create folder structure.
* Create `requirements.txt` with Tkinter (built-in), sqlite3 (built-in), PIL (optional), customtkinter (optional).
* ✅ Cursor: After folder structure is created.

### ✅ Step 2: Database Setup

* Write `db_connection.py` → function to connect to DB.
* Write `create_tables.py` → tables:

  * users(id, name, email, password, role)
  * complaints(id, user_id, category, description, location, status, date)
* ✅ Cursor: After tables are created, test connection.

### ✅ Step 3: Authentication Logic

* In `logic/auth.py`, write:

  * register_user()
  * login_user()
* Hash passwords (optional).
* ✅ Cursor: After writing functions.

### ✅ Step 4: GUI – Login & Register

* `login_gui.py`: GUI form + call login_user().
* `register_gui.py`: GUI form + call register_user().
* ✅ Cursor: Place GUI widgets.

### ✅ Step 5: User Dashboard

* `user_dashboard.py`:

  * Show menu: Log Complaint, View My Complaints, Logout.
* ✅ Cursor: Build layout.

### ✅ Step 6: Complaint Form

* `complaint_form.py`:

  * Fields: Category (dropdown), Description (textbox), Location (entry).
  * Submit -> store in DB.
* ✅ Cursor: Write save function.

### ✅ Step 7: View Complaints (User)

* List complaints by user.
* Display status (Pending / In Progress / Resolved).
* ✅ Cursor: Implement table/list.

### ✅ Step 8: Admin Dashboard

* `admin_dashboard.py`:

  * Show all complaints.
  * Filter by status.
  * Update status.
* ✅ Cursor: Implement update function.

### ✅ Step 9: Complaint Management Logic

* In `logic/complaint_manager.py`:

  * add_complaint()
  * get_user_complaints()
  * get_all_complaints()
  * update_status()
* ✅ Cursor: Integrate with GUI.

### ✅ Step 10: Utility Functions

* In `utils/helper_functions.py`:

  * validate inputs
  * show message popups
* ✅ Cursor: Use in GUI.

### ✅ Step 11: main.py Entry Point

* Open Login screen first.
* After login: if role=user → user_dashboard; else → admin_dashboard.
* ✅ Cursor: Control flow.

### ✅ Step 12: Testing

* Test registration/login.
* Test complaint creation.
* Test status update.
* ✅ Cursor: Write small test cases.

### ✅ Step 13: Polishing

* Add icons/images.
* Improve layout.
* Add scrollbars.

### ✅ Step 14: Documentation

* Add README.md with overview, setup, usage.

### ✅ Step 15: Optional Expansion

* Export reports (CSV/PDF).
* Email/SMS notifications.
* Web dashboard in future.

---

## ✅ Final Goal

By following each step and placing the cursor where instructed, the ENTIRE project will be fully built from scratch.

✅ Ready to start coding! Let me know and I will generate each file step-by-step.
