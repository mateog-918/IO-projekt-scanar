import React, { useEffect, useState } from 'react';
import { QRCodeCanvas } from 'qrcode.react'; // Wymaga: npm install qrcode.react
import Swal from 'sweetalert2';

const RemoveEmployee = () => {
    const [employees, setEmployees] = useState([]);
    const [selectedId, setSelectedId] = useState('');
    const [employeeData, setEmployeeData] = useState(null);
    const [loading, setLoading] = useState(false);


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
    // 1. Pobierz listę wszystkich pracowników do dropdowna
    useEffect(() => {
        fetchEmployees();
    }, []);

    // 2. Pobierz szczegóły po zmianie w select
    const handleSelectChange = async (e) => {
        const id = e.target.value;
        setSelectedId(id);

        if (!id) {
            setEmployeeData(null);
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/api/manage_employees/${id}`);
            const data = await response.json();
            setEmployeeData(data.employee);
        } catch (err) {
            Swal.fire('Błąd', 'Nie udało się pobrać danych pracownika', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleRemove = async () => {
        if (!selectedId) return;

        // 1. Wyświetlenie okna potwierdzenia
        const result = await Swal.fire({
            title: 'Are you sure?',
            text: `You are about to remove ${employeeData?.name} from database!`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#EF0000',
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel'
        });

        // 2. Jeśli użytkownik kliknął "Yes, delete it!"
        if (result.isConfirmed) {
            try {
                // Przygotowanie URL z parametrem confirm=true
                const url = `http://localhost:5000/api/manage_employees/${selectedId}?confirm=true`;

                const response = await fetch(url, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // Jeśli backend wymaga employee_id również w body, odkomentuj poniższe:
                    // body: JSON.stringify({ employee_id: selectedId })
                });

                const data = await response.json();

                if (response.ok) {
                    // 1. AKTUALIZACJA LISTY W STANIE (KLUCZOWY KROK)
                    // Zakładamy, że Twoja lista pracowników nazywa się 'employees'
                    const list_response = await fetch('http://localhost:5000/api/manage_employees/');
                    const list_data = await list_response.json();
                    setEmployees(Array.isArray(list_data) ? list_data : list_data.employees || []);

                    // Czyszczenie stanu po poprawnym usunięciu
                    setEmployeeData(null);
                    setSelectedId('');

                    // Sukces
                    Swal.fire(
                        'Deleted!',
                        data.message || 'Employee has been removed.',
                        'success'
                    );

                } else {
                    // Błąd zwrócony przez serwer (np. 404 lub 500)
                    Swal.fire(
                        'Error!',
                        data.message || 'Something went wrong while deleting.',
                        'error'
                    );
                }
            } catch (error) {
                // Błąd połączenia
                console.error("Delete error:", error);
                Swal.fire(
                    'Connection Error',
                    'Could not connect to the server.',
                    'error'
                );
            }
        }
    };

    return (
        <div className="remove-page-container">
            {/* Lewa strona - Wybór */}
            <div className="form-container" style={{ flex: 1 }}>
                <div className="input-group-row">
                    <div className="input-field">
                        <label>Select Employee</label>
                        <select
                            className="custom-select"
                            value={selectedId}
                            onChange={handleSelectChange}
                        >
                            <option value="">Choose an employee...</option>
                            {Array.isArray(employees) ? (
                                employees.map((emp) => (
                                    <option key={emp.id} value={emp.id}>
                                        {emp.name}
                                    </option>
                                ))
                            ) : (
                              <option disabled>Błąd ładowania pracowników...</option>
                            )}
                        </select>
                    </div>
                    <button
                        className={`btn-main ${!selectedId ? 'btn-disabled' : ''}`}
                        style={{ backgroundColor: '#EF0000' }}
                        onClick={handleRemove}
                        disabled={!selectedId}
                    >
                        Remove from database
                    </button>
                </div>
            </div>

            {/* Prawa strona - Wyświetlanie informacji */}
            <div className="information-display-card">
                {!employeeData ? (
                    <div className="placeholder-info">
                        <p>{loading ? "Loading..." : "Select an employee to see details"}</p>
                    </div>
                ) : (
                    <div className="employee-details-view">
                        <div className="details-header">
                            <h3>{employeeData.name}</h3>
                            <span className={`status-badge ${employeeData.is_active ? 'active' : 'inactive'}`}>
                                {employeeData.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>

                        <div className="details-grid">
                            <div className="info-section">
                                <p><strong>Department:</strong> {employeeData.department}</p>
                                <p><strong>Position:</strong> {employeeData.position}</p>
                                <p><strong>Joined:</strong> {new Date(employeeData.created_at).toLocaleDateString()}</p>
                                <p><strong>Database ID:</strong> {employeeData.id}</p>
                            </div>

                            <div className="qr-section">
                                <label>QR Security Code</label>
                                <div className="qr-box">
                                    {employeeData.qr_code_hash ? (
                                        /* Jeśli hash istnieje, renderujemy kod QR */
                                        <QRCodeCanvas value={employeeData.qr_code_hash} size={120}/>
                                    ) : (
                                        /* Jeśli hash jest pusty "", wyświetlamy komunikat */
                                        <div className="no-qr-info">
                                            <p>Ten pracownik nie ma przypisanego kodu QR</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="images-section">
                            <label>Registered Face Patterns</label>
                            <div className="face-images-grid">
                                {employeeData.face_image_paths.map((path, idx) => (
                                    <img
                                        key={idx}
                                        src={`http://localhost:5000/${path}`}
                                        alt="Face sample"
                                        className="small-face-thumb"
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RemoveEmployee;