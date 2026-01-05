import React, { useState, useEffect } from 'react';
import { QRCodeCanvas } from 'qrcode.react'; // Importujemy komponent kodu QR
import Swal from 'sweetalert2';

const GenerateQR = () => {
  const [formData, setFormData] = useState({ fullName: '' });
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  // Stan przechowujący hash, dla którego generujemy kod QR
  const [qrValue, setQrValue] = useState('');

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/manage_employees/');
        const data = await response.json();

        // Obsługa różnych struktur danych (tablica lub obiekt z kluczem employees)
        if (Array.isArray(data)) {
          setEmployees(data);
        } else if (data.employees && Array.isArray(data.employees)) {
          setEmployees(data.employees);
        }
      } catch (error) {
        console.error("Błąd pobierania:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  const handleGenerate = () => {
    if (!formData.fullName) {
      Swal.fire('Info', 'Proszę najpierw wybrać pracownika z listy.', 'info');
      return;
    }

    // Szukamy wybranego pracownika w pobranej liście, aby wyciągnąć jego hash
    const selectedEmployee = employees.find(emp => emp.name === formData.fullName);

    if (selectedEmployee && selectedEmployee.qr_code_hash) {
      setQrValue(selectedEmployee.qr_code_hash);
    } else {
      Swal.fire('Błąd', 'Ten pracownik nie posiada przypisanego kodu QR w bazie.', 'error');
      setQrValue('');
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
            onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
            disabled={loading}
          >
            <option value="">Choose an employee...</option>
            {employees.map((emp, index) => (
              <option key={index} value={emp.name}>
                {emp.name}
              </option>
            ))}
          </select>
        </div>
        <button className="btn-main" onClick={handleGenerate}>
          Generate QR Code
        </button>
      </div>

      <div className="qr-code-display">
        <label>Generated QR Code:</label>
        <div className="qr-canvas-wrapper">
          {qrValue ? (
            <div className="qr-result">
              <QRCodeCanvas
                value={qrValue}
                size={200}
                level={"H"} // Wysoki poziom korekcji błędów
                includeMargin={true}
              />
            </div>
          ) : (
            <div className="qr-placeholder">
              Select an employee and click "Generate"
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GenerateQR;