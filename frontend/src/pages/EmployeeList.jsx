import React, { useEffect, useState } from 'react';
import { QRCodeCanvas } from 'qrcode.react'; // Wymaga: npm install qrcode.react
import Swal from 'sweetalert2';

const EmployeeList = () => {
    const [employees, setEmployees] = useState([]);
    const [searchTerm, setSearchTerm] = useState(''); // Stan wyszukiwania
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

    // Logika filtrowania pracowników
    const filteredEmployees = employees.filter(emp =>
        emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.position.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return <div className="loading-spinner">Loading employees...</div>;
    }

    return (
        <div className="employee-list-page">
            <div className="list-header-sticky">
                <h2>Employee Directory ({filteredEmployees.length})</h2>
                <div className="search-container">
                    <input
                        type="text"
                        placeholder="Search by name, department or position..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </div>
            </div>

            <div className="employees-scroll-area">
                {filteredEmployees.length === 0 ? (
                    <div className="placeholder-info">
                        <p>{searchTerm ? "No matches found." : "No employees in database."}</p>
                    </div>
                ) : (
                    <div className="employees-vertical-stack">
                        {filteredEmployees.map((emp) => (
                            <div key={emp.id} className="information-display-card">
                                <div className="employee-details-view">
                                    <div className="details-header">
                                        <h3>{emp.name}</h3>
                                        <span className={`status-badge ${emp.is_active ? 'active' : 'inactive'}`}>
                                            {emp.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>

                                    <div className="details-grid">
                                        <div className="info-section">
                                            <p><strong>Department:</strong> {emp.department}</p>
                                            <p><strong>Position:</strong> {emp.position}</p>
                                            <p>
                                                <strong>Joined:</strong> {new Date(emp.created_at).toLocaleDateString()}
                                            </p>
                                            <p><strong>Database ID:</strong> {emp.id}</p>
                                        </div>

                                        <div className="qr-section">
                                            <label>QR Security Code</label>
                                            <div className="qr-box">
                                                {emp.qr_code_hash ? (
                                                    /* Jeśli hash istnieje, renderujemy kod QR */
                                                    <QRCodeCanvas value={emp.qr_code_hash} size={120}/>
                                                ) : (
                                                    /* Jeśli hash jest pusty "", wyświetlamy komunikat */
                                                    <div className="no-qr-info">
                                                        <p>Ten pracownik nie ma przypisanego kodu QR</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {emp.face_image_paths?.length > 0 && (
                                        <div className="images-section">
                                            <label>Registered Face Patterns</label>
                                            <div className="face-images-grid">
                                                {emp.face_image_paths.map((path, idx) => (
                                                    <img
                                                        key={idx}
                                                        src={`http://localhost:5000/${path}`}
                                                        alt="Face sample"
                                                        className="small-face-thumb"
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmployeeList;
