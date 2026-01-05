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

    const handleRemove = () => {
        if (!selectedId) return;

        Swal.fire({
            title: 'Are you sure?',
            text: `You are about to remove ${employeeData?.name} from database!`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#EF0000',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                // Tutaj dodałbyś fetch(..., { method: 'DELETE' })
                Swal.fire('Deleted!', 'Employee has been removed.', 'success');
                setEmployeeData(null);
                setSelectedId('');
            }
        });
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
                                    <QRCodeCanvas value={employeeData.qr_code_hash} size={120} />
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