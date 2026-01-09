import React, { useState, useEffect } from 'react';
import Swal from 'sweetalert2';

const Reports = () => {
    const [formData, setFormData] = useState({ employeeId: '', eventType: '', startDate: '', endDate: '' });
    const [employees, setEmployees] = useState([]);
    const [eventTypes, setEventTypes] = useState([]);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [limit, setLimit] = useState(100);
    const [offset, setOffset] = useState(0);
    const [statistics, setStatistics] = useState({});

    useEffect(() => {
        fetchEmployees();
        fetchEventTypes();
    }, []);

    const fetchEmployees = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/manage_employees/');
            const data = await res.json();
            if (res.ok && data.employees) {
                setEmployees(data.employees);
            } else {
                console.error('Failed to load employees', data);
            }
        } catch (err) {
            console.error(err);
            Swal.fire('Błąd', 'Nie udało się pobrać listy pracowników.', 'error');
        }
    };

    const fetchEventTypes = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/logs/event-types');
            const data = await res.json();
            if (res.ok && data.event_types) setEventTypes(data.event_types);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchStatistics = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/logs/statistics');
            const data = await res.json();
            if (res.ok && data.statistics) {
                setStatistics(data.statistics);
            }
        } catch (err) {
            console.error('Failed to fetch statistics:', err);
        }
    };

    const calculateStatisticsFromLogs = (logsArray) => {
        const stats = {};
        logsArray.forEach(log => {
            const eventType = log.event_type;
            stats[eventType] = (stats[eventType] || 0) + 1;
        });
        stats.total = logsArray.length;
        return stats;
    };

    const fetchLogs = async (pageOffset = 0) => {
        setLoading(true);
        setLogs([]);

        try {
            const { employeeId, eventType, startDate, endDate } = formData;

            let res;

            // If date range provided, use date-range endpoint and then client-filter
            if (startDate && endDate) {
                const startIso = new Date(startDate).toISOString();
                const endIso = new Date(endDate).toISOString();
                res = await fetch(`http://localhost:5000/api/logs/date-range?start_date=${encodeURIComponent(startIso)}&end_date=${encodeURIComponent(endIso)}&limit=${limit}&offset=${pageOffset}`);
            } else if (employeeId) {
                res = await fetch(`http://localhost:5000/api/logs/employee/${employeeId}?limit=${limit}&offset=${pageOffset}`);
            } else if (eventType) {
                res = await fetch(`http://localhost:5000/api/logs/type/${encodeURIComponent(eventType)}?limit=${limit}&offset=${pageOffset}`);
            } else {
                res = await fetch(`http://localhost:5000/api/logs/?limit=${limit}&offset=${pageOffset}`);
            }

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to fetch logs');

            let fetchedLogs = data.logs || [];

            // Client-side filtering if combination of filters chosen
            if (!startDate && employeeId && eventType) {
                fetchedLogs = fetchedLogs.filter(l => String(l.employee_id) === String(employeeId) && String(l.event_type) === String(eventType));
            } else if (!startDate && employeeId) {
                fetchedLogs = fetchedLogs.filter(l => String(l.employee_id) === String(employeeId));
            } else if (!startDate && eventType) {
                fetchedLogs = fetchedLogs.filter(l => String(l.event_type) === String(eventType));
            }

            setLogs(fetchedLogs);
            setOffset(pageOffset);
            
            // Calculate statistics from currently displayed logs only
            const stats = calculateStatisticsFromLogs(fetchedLogs);
            setStatistics(stats);
        } catch (err) {
            console.error(err);
            Swal.fire('Błąd', 'Nie udało się pobrać logów.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const formatTimestamp = (isoString) => {
        if (!isoString) return '-';
        try {
            // Display in user's timezone (UTC+1). Using Europe/Warsaw to handle DST automatically.
            const dt = new Date(isoString);
            const opts = {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
                timeZone: 'Europe/Warsaw'
            };
            // Format like: DD.MM.YYYY, HH:MM:SS (24h)
            const parts = new Intl.DateTimeFormat('en-GB', opts).formatToParts(dt);
            const map = {};
            parts.forEach(p => { if (p.type !== 'literal') map[p.type] = p.value; });
            return `${map.day}.${map.month}.${map.year} ${map.hour}:${map.minute}:${map.second}`;
        } catch (e) {
            return isoString;
        }
    };

    const formatPreview = (localInputValue) => {
        if (!localInputValue) return '';
        try {
            // localInputValue is like '2024-01-09T13:45' (no seconds)
            const dt = new Date(localInputValue);
            return formatTimestamp(dt.toISOString());
        } catch (e) {
            return '';
        }
    };

    const handleSearch = () => fetchLogs(0);

    const handlePrev = () => {
        const newOffset = Math.max(0, offset - limit);
        fetchLogs(newOffset);
    };

    const handleNext = () => {
        const newOffset = offset + limit;
        fetchLogs(newOffset);
    };

    return (
        <div className="form-container">
            <div className="input-group-row">
                <div className="input-field">
                    <label>Employee</label>
                    <select
                        className="custom-select"
                        value={formData.employeeId}
                        onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
                    >
                        <option value="">All employees</option>
                        {employees.map(emp => (
                            <option key={emp.id} value={emp.id}>{emp.name}</option>
                        ))}
                    </select>
                </div>

                <div className="input-field">
                    <label>Event Type</label>
                    <select
                        className="custom-select"
                        value={formData.eventType}
                        onChange={(e) => setFormData({ ...formData, eventType: e.target.value })}
                    >
                        <option value="">All types</option>
                        {eventTypes.map((et, i) => (
                            <option key={i} value={et}>{et}</option>
                        ))}
                    </select>
                </div>

                <div className="input-field">
                    <label>Start (local)</label>
                    <input type="datetime-local" value={formData.startDate} onChange={e => setFormData({ ...formData, startDate: e.target.value })} />
                </div>

                <div className="input-field">
                    <label>End (local)</label>
                    <input type="datetime-local" value={formData.endDate} onChange={e => setFormData({ ...formData, endDate: e.target.value })} />
                </div>

                <div className="input-field">
                    <label>Limit</label>
                    <input type="number" value={limit} onChange={e => setLimit(Number(e.target.value) || 100)} />
                </div>

                <button className="btn-main" onClick={handleSearch} disabled={loading}>
                    {loading ? 'Loading...' : 'Check report'}
                </button>
            </div>

            <div className="qr-code-display">
                <label>Report of events:</label>

                <div style={{ marginTop: 12, maxHeight: '60vh', overflowY: 'auto' }}>
                    <table className="table" style={{ borderCollapse: 'collapse', width: '100%' }}>
                        <thead>
                            <tr>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>ID</th>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>Timestamp</th>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>Event Type</th>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>Employee</th>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>Message</th>
                                <th style={{ border: '1px solid #ccc', padding: 8 }}>Image</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.length === 0 && (
                                <tr><td colSpan={6} style={{ border: '1px solid #ccc', padding: 8 }}>{loading ? 'Loading...' : 'No logs found'}</td></tr>
                            )}
                            {logs.map(log => (
                                <tr key={log.id}>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{log.id}</td>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{formatTimestamp(log.timestamp)}</td>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{log.event_type}</td>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{log.employee_name || log.employee_id || '-'}</td>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{log.message || '-'}</td>
                                    <td style={{ border: '1px solid #ccc', padding: 8 }}>{log.image_path ? <a href={`http://localhost:5000/${log.image_path}`} target="_blank" rel="noreferrer">View</a> : '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <div style={{ marginTop: 8 }}>
                        <button onClick={handlePrev} disabled={offset === 0 || loading}>Prev</button>
                        <span style={{ margin: '0 8px' }}>Offset: {offset}</span>
                        <button onClick={handleNext} disabled={loading}>Next</button>
                    </div>

                    <div style={{ marginTop: 20, padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                        <label style={{ fontSize: '16px', fontWeight: 'bold' }}>Event Statistics:</label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', marginTop: 12 }}>
                            {Object.entries(statistics).filter(([k]) => k !== 'total').map(([eventType, count]) => (
                                <div key={eventType} style={{ border: '1px solid #ddd', padding: 12, borderRadius: 4, backgroundColor: '#fff' }}>
                                    <div style={{ fontSize: '12px', color: '#666' }}>{eventType}</div>
                                    <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#333' }}>{count}</div>
                                </div>
                            ))}
                        </div>
                        <div style={{ marginTop: 12, fontSize: '14px', fontWeight: 'bold' }}>
                            Total Events: <span style={{ color: '#0066cc' }}>{statistics.total || 0}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Reports;