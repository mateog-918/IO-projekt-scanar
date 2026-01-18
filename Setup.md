# Running the Scanar Application - Windows

## Requirements
- Python 3.11
- Node.js 16+
- npm or yarn
- Camera (for face recognition features)

---

## Backend Setup

### 1. Clone and Navigate
```bash
git clone https://github.com/mateog-918/IO-projekt-scanar.git
cd IO-projekt-scanar
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
.\venv\Scripts\activate
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Run Backend Server
```bash
python app.py
```

Backend should be running at **http://127.0.0.1:5000**

Swagger API documentation: **http://127.0.0.1:5000/apidocs/**

---

## Frontend Setup

### 1. Open New Terminal
Keep the backend terminal running and open a new terminal window.

### 2. Navigate to Frontend Directory
```bash
cd IO-projekt-scanar/frontend
```

### 3. Install Dependencies
```bash
npm install
```

### 4. Run Development Server
```bash
npm run dev
```

Frontend should be running at **http://localhost:5173**

---

## Application URLs

After successful setup, access:

- **Main Page (Employees)**: http://localhost:5173
- **Admin Panel**: http://localhost:5173/login
- **Backend API**: http://127.0.0.1:5000
- **API Documentation**: http://127.0.0.1:5000/apidocs/

---

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`


---

## Troubleshooting

### Backend Issues

**Port 5000 already in use:**
```bash
# Kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Missing dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**
- Vite will automatically try the next available port (5174, 5175, etc.)

**Node modules issues:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Camera not working:**
- Ensure browser has camera permissions
- Check if another application is using the camera
- Try using HTTPS (camera API requires secure context)

---

## Stopping the Application

### Backend
Press `Ctrl+C` in the backend terminal

### Frontend
Press `Ctrl+C` in the frontend terminal

### Deactivate Virtual Environment
```bash
deactivate
```