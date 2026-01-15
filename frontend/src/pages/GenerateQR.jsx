import React, { useState, useEffect, useRef } from 'react';
import { QRCodeCanvas } from 'qrcode.react';
import Swal from 'sweetalert2';

const GenerateQR = () => {
  const [formData, setFormData] = useState({ fullName: '' });
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [qrValue, setQrValue] = useState('');

  const qrRef = useRef(null); // Ref do pobrania obrazka z Canvas

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/manage_employees/');
      const data = await response.json();
      setEmployees(Array.isArray(data) ? data : data.employees || []);
    } catch (error) {
      console.error("Błąd pobierania:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!formData.fullName) {
      Swal.fire('Info', 'Proszę wybrać pracownika.', 'info');
      return;
    }

    try {
      // Find employee ID by name
      const selectedEmployee = employees.find(emp => emp.name === formData.fullName);
      
      if (!selectedEmployee) {
        Swal.fire('Błąd', 'Nie znaleziono pracownika.', 'error');
        return;
      }

      // API call to generate a new hash for this employee
      const response = await fetch(`http://localhost:5000/api/manage_employees/${selectedEmployee.id}/qr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Failed to generate hash');
      }

      const data = await response.json();
      const newHash = data.qr_code_hash;

      setQrValue(newHash);

      // Musimy poczekać chwilę, aż React wyrenderuje Canvas z nową wartością
      setTimeout(() => {
        saveQRToServer(formData.fullName, selectedEmployee.id);
      }, 500);

    } catch (error) {
      console.error("Błąd generowania hasha:", error);
      Swal.fire('Błąd', 'Nie udało się wygenerować kodu QR.', 'error');
    }
  };

  const saveQRToServer = async (fileName, employeeID) => {
    const canvas = document.querySelector('canvas'); // Pobieramy canvas wygenerowany przez bibliotekę
    if (!canvas) return;

    const imageData = canvas.toDataURL("image/png"); // Zamiana na Base64

    try {
      const response = await fetch('http://localhost:5000/api/verification/save_qr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: imageData,
          name: fileName,
          id: employeeID
        }),
      });

      if (response.ok) {
        Swal.fire('Sukces', `Kod QR dla ${fileName} został zapisany na serwerze.`, 'success');
      }
    } catch (error) {
      console.error("Błąd zapisu na serwerze:", error);
      Swal.fire('Błąd', 'Nie udało się zapisać pliku na serwerze.', 'error');
    }
  };

  return (
    <div className="form-container">
      <div className="input-group-row">
        <div className="input-field">
          <label>Select Employee</label>
          <select
            className="custom-select"
            value={formData.fullName}
            onChange={(e) => {
                setFormData({ ...formData, fullName: e.target.value });
                setQrValue(''); // Czyścimy stary kod przy zmianie osoby
            }}
            disabled={loading}
          >
            <option value="">Choose an employee...</option>
            {employees.map((emp, index) => (
              <option key={index} value={emp.name}>{emp.name}</option>
            ))}
          </select>
        </div>
        <button className="btn-main" onClick={handleGenerate}>
          Generate & Save QR
        </button>
      </div>

      <div className="qr-code-display">
        <label>Generated QR Code:</label>
        <div className="qr-canvas-wrapper">
          {qrValue ? (
            <QRCodeCanvas
              value={qrValue}
              size={200}
              level={"H"}
              includeMargin={true}
            />
          ) : (
            <div className="qr-placeholder">Select employee and click Generate</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerateQR;