import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Login from './pages/Login.jsx';
import AddEmployee from './pages/AddEmployee.jsx';
import Verify from './pages/Verify.jsx';
import VerifyFace from "./pages/VerifyFace.jsx";
import GenerateQR from './pages/GenerateQR.jsx';
import AddFace from './pages/AddFace.jsx';
import RemoveEmployee from './pages/RemoveEmployee.jsx';
import Reports from './pages/Reports.jsx';
import './App.css';
import logo from './assets/Logo.png';

// Tworzymy pomocniczy komponent, aby móc użyć useLocation()
function AppContent() {
  const location = useLocation();

  // Sidebar ma znikać na "/" (Verify) oraz opcjonalnie na "/login"
  const hideSidebar = location.pathname === "/" || location.pathname === "/verify-face";

  return (
    <div className="app-layout">
      <div className="app-header">
        <img src={logo} alt="SCANAR Logo" className="logo" />
      </div>

      {/* Dynamiczna klasa: jeśli hideSidebar jest true, dodajemy 'no-sidebar' */}
      <div className={`app-container ${hideSidebar ? 'no-sidebar' : ''}`}>

        {!hideSidebar && <Sidebar />}

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Verify />} />
            <Route path="/login" element={<Login />} />
            <Route path="/generate-qr" element={<GenerateQR />} />
            <Route path="/add-employee" element={<AddEmployee />} />
            <Route path="/add-face" element={<AddFace />} />
            <Route path="/remove-employee" element={<RemoveEmployee />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/verify-face" element={<VerifyFace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

// Główny komponent tylko renderuje Router
function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;