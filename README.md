# 📚 LibraryOS — Smart Digital Library Automation Platform

A full-stack web application for managing a college/institution library. Built with **Flask**, **MySQL**, and a modern responsive UI.

---

## 🚀 Features

### Admin Portal
- 🔐 Secure admin login
- 📊 Dashboard with real-time stats and charts
- 📚 Book management (add, edit, delete, search, filter by category)
- 👥 Member management (add, edit, delete, search)
- 🔄 Issue & Return books with automatic due date calculation
- 💰 Fine management with overdue tracking (₹5/day)
- 📋 Book request approval/rejection system
- 📈 Reports (issued, returned, fines)
- 🌙 Dark mode support

### Student Portal
- 🎓 Student login via college email
- 📖 Browse all books by category
- 🔍 Search books by title or author
- ✅ See available/out-of-stock status with return dates
- 📬 Request books from the library
- 📅 View borrowed books with due dates and overdue alerts
- 💸 View pending fines

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, Flask 3.0 |
| Database | MySQL 9.x |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login (admin), Flask Session (student) |
| Frontend | HTML5, CSS3, Bootstrap 5, Bootstrap Icons |
| Charts | Chart.js |
| Fonts | Syne, DM Sans (Google Fonts) |

---

## 📁 Project Structure

```
library_management/
├── backend/
│   ├── app.py              # App factory, entry point
│   ├── config.py           # Configuration (DB, secret key)
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # All route handlers
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (not in git)
├── frontend/
│   ├── templates/
│   │   ├── base.html           # Base layout with sidebar
│   │   ├── login.html          # Admin login
│   │   ├── dashboard.html      # Admin dashboard
│   │   ├── books.html          # Book management
│   │   ├── members.html        # Member management
│   │   ├── issue_return.html   # Issue/Return books
│   │   ├── fines.html          # Fine management
│   │   ├── reports.html        # Reports
│   │   ├── requests.html       # Book requests (admin)
│   │   ├── student_login.html  # Student login
│   │   └── student_portal.html # Student dashboard
│   └── static/
│       ├── css/style.css   # Main stylesheet
│       └── js/main.js      # JavaScript
├── database/
│   └── library_db.sql      # Database schema + seed data
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- MySQL Workbench (optional but recommended)
- Git

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/library-management.git
cd library-management
```

---

### Step 2 — Set Up the Database

Open **MySQL Workbench** and run the file:

```
database/library_db.sql
```

Or via terminal:

```bash
"C:\Program Files\MySQL\MySQL Server 9.6\bin\mysql.exe" -u root -p < database/library_db.sql
```

---

### Step 3 — Set Up Python Environment

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

### Step 4 — Configure Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your-mysql-password
```

> ⚠️ Never commit your `.env` file. It's already in `.gitignore`.

---

### Step 5 — Run the Application

```bash
cd backend
python app.py
```

Open your browser and go to:

- **Admin Portal** → `http://127.0.0.1:5000/login`
- **Student Portal** → `http://127.0.0.1:5000/student`

---

## 🔑 Default Login Credentials

### Admin
| Username | Password |
|----------|----------|
| admin | admin123 |

### Student
Students log in using their registered **college email address** (e.g. `arjun@college.edu`)

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `admins` | Admin accounts |
| `categories` | Book categories |
| `books` | Book inventory |
| `members` | Student/member records |
| `issued_books` | Book issue/return tracking |
| `fines` | Fine records |
| `book_requests` | Student book requests |

---

## 📸 Screenshots

### Admin Dashboard
> Dashboard with stats, charts, and recent activity

### Book Management
> Category sidebar + book table with availability status

### Student Portal
> Book browser with request feature and borrowed books tracker

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | Required |
| `DB_PASSWORD` | MySQL root password | Required |
| `FINE_PER_DAY` | Fine amount per overdue day | ₹5 |
| `LOAN_PERIOD_DAYS` | Default loan duration | 14 days |

---

## 📦 Dependencies

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
PyMySQL==1.1.0
Werkzeug==3.0.1
python-dotenv==1.0.0
cryptography
```

---

## 🚀 Deployment Notes

- For production, set `debug=False` in `app.py`
- Use a strong random `SECRET_KEY`
- Consider using **Gunicorn** as the WSGI server
- Use **Nginx** as a reverse proxy
- Store `.env` securely on the server

---

## 👨‍💻 Author

**Satish Malladad**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: Satishmalladad02@gmail.com

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [Google Fonts](https://fonts.google.com/)