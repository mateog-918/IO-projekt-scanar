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

    const toggleActivation = async () => {
        if (!selectedId || !employeeData) return;

        // Określamy akcję na podstawie obecnego stanu pracownika
        const action = employeeData.is_active ? 'deactivate' : 'activate';
        const url = `http://localhost:5000/api/manage_employees/${selectedId}/${action}`;

        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (response.ok) {
                // Aktualizujemy dane wyświetlane w podglądzie (prawa strona)
                setEmployeeData(data.employee);

                // Aktualizujemy stan na liście głównej (aby dropdown był spójny)
                setEmployees(prev => prev.map(emp =>
                    emp.id === selectedId ? { ...emp, is_active: data.employee.is_active } : emp
                ));

                Swal.fire({
                    icon: 'success',
                    title: 'Status Updated',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                Swal.fire('Error!', data.message || 'Failed to update status', 'error');
            }
        } catch (error) {
            Swal.fire('Error', 'Connection error to the server.', 'error');
        }
    };

    // 1. Logika edycji danych pracownika
    const handleEdit = async () => {
        if (!selectedId || !employeeData) return;

        const { value: formValues } = await Swal.fire({
            title: 'Edit Employee Details',
            html: `
            <style>
                .swal-form-container {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    padding: 10px 0;
                }
                .swal-field-group {
                    display: flex;
                    flex-direction: column;
                    text-align: left;
                }
                .swal-field-group label {
                    font-weight: 600;
                    font-size: 14px;
                    margin-bottom: 5px;
                    color: #555;
                    margin-left: 3px;
                }
                .swal-field-group input {
                    margin: 0 !important; /* Nadpisujemy marginesy swal2-input */
                    width: 100% !important;
                    box-sizing: border-box;
                    height: 45px;
                }
            </style>
            <div class="swal-form-container">
                <div class="swal-field-group">
                    <label for="swal-name">Full Name</label>
                    <input id="swal-name" class="swal2-input" value="${employeeData.name}" placeholder="Enter name">
                </div>
                <div class="swal-field-group">
                    <label for="swal-position">Position</label>
                    <input id="swal-position" class="swal2-input" value="${employeeData.position}" placeholder="Enter position">
                </div>
                <div class="swal-field-group">
                    <label for="swal-department">Department</label>
                    <input id="swal-department" class="swal2-input" value="${employeeData.department}" placeholder="Enter department">
                </div>
            </div>
        `,
            focusConfirm: false,
            showCancelButton: true,
            confirmButtonColor: '#3498db',
            confirmButtonText: 'Save Changes',
            preConfirm: () => {
                const name = document.getElementById('swal-name').value;
                const position = document.getElementById('swal-position').value;
                const department = document.getElementById('swal-department').value;

                if (!name || !position || !department) {
                    Swal.showValidationMessage('Please fill out all fields');
                    return false;
                }

                return { name, position, department };
            }
        });

        if (formValues) {
            try {
                const response = await fetch(`http://localhost:5000/api/manage_employees/${selectedId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formValues)
                });
                const data = await response.json();

                if (response.ok) {
                    setEmployeeData(data.employee);
                    setEmployees(prev => prev.map(emp => emp.id === selectedId ? { ...emp, ...formValues } : emp));
                    Swal.fire('Updated!', data.message, 'success');
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            } catch (error) {
                Swal.fire('Error', 'Connection failed', 'error');
            }
        }
    };

// 2. Logika usuwania konkretnej twarzy
    const handleDeleteFace = async (faceIndex) => {
        // faceIndex przychodzi z onClick={() => handleDeleteFace(idx)}
        if (faceIndex === undefined || faceIndex === null) return;

        const result = await Swal.fire({
            title: 'Delete this face pattern?',
            text: "This action cannot be undone!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#EF0000',
            confirmButtonText: 'Yes, delete it!'
        });

        if (result.isConfirmed) {
            // Opcjonalnie: pokazujemy loader na czas usuwania
            Swal.fire({
                title: 'Removing...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });
            try {
                const response = await fetch(`http://localhost:5000/api/manage_employees/${selectedId}/faces/${faceIndex+1}`, {
                    method: 'DELETE'
                });
                const data = await response.json();

                if (response.ok) {
                    // Odświeżamy dane pracownika, aby pobrać aktualną listę ścieżek do zdjęć
                    const refreshRes = await fetch(`http://localhost:5000/api/manage_employees/${selectedId}`);
                    const refreshData = await refreshRes.json();
                    setEmployeeData(refreshData.employee);

                    Swal.fire({
                        icon: 'success',
                        title: 'Deleted!',
                        text: data.message,
                        timer: 1500,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire('Error', data.message || 'Could not delete face', 'error');
                }
            } catch (error) {
                Swal.fire('Error', 'Connection failed', 'error');
            }
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
                        style={{backgroundColor: '#EF0000'}}
                        onClick={handleRemove}
                        disabled={!selectedId}
                    >
                        Remove from database
                    </button>
                    <button
                        className={`btn-main ${!selectedId ? 'btn-disabled' : ''}`}
                        style={{
                            backgroundColor: employeeData?.is_active ? '#f39c12' : '#27ae60',
                            marginTop: '10px' // Opcjonalnie, jeśli chcesz je rozdzielić pionowo
                        }}
                        onClick={toggleActivation}
                        disabled={!selectedId}
                    >
                        {employeeData?.is_active ? 'Deactivate Employee' : 'Activate Employee'}
                    </button>
                    <button
                        className={`btn-main ${!selectedId ? 'btn-disabled' : ''}`}
                        style={{backgroundColor: '#3498db', marginTop: '10px'}}
                        onClick={handleEdit}
                        disabled={!selectedId}
                    >
                        Edit Employee Details
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
                            <label>Registered Face Patterns (Click 'X' to remove)</label>
                            <div className="face-images-grid">
                                {employeeData.face_image_paths.map((path, idx) => (
                                    <div key={idx} className="face-thumb-wrapper"
                                         style={{position: 'relative', display: 'inline-block'}}>
                                        <img
                                            src={`http://localhost:5000/${path}`}
                                            alt={`Face pattern ${idx}`}
                                            className="small-face-thumb"
                                        />
                                        <button
                                            className="delete-face-btn"
                                            onClick={() => handleDeleteFace(idx)}
                                        >
                                            &times;
                                        </button>
                                    </div>
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