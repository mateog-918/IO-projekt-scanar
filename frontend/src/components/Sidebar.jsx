import { NavLink } from 'react-router-dom';

const Sidebar = ({ isLoggedIn }) => {
  const menuItems = [
    { name: 'Login', path: '/login', public: true },
    { name: 'Add an employee', path: '/add-employee', public: false },
    { name: 'Generate QR Code', path: '/generate-qr', public: false },
    { name: 'Add face pictures', path: '/add-face', public: false },
    { name: 'Manage an employee', path: '/remove-employee', public: false },
    { name: 'Reports', path: '/reports', public: false },
    { name: 'Employee List', path: '/employee-list', public: false },
  ];

  return (
      <div className="sidebar">
        {menuItems.map((item) => {
          // Sprawdzamy, czy link powinien być wyłączony
          const isDisabled = !isLoggedIn && !item.public;

          return (
              <NavLink
                  key={item.path}
                  to={isDisabled ? "#" : item.path} // Jeśli wyłączony, nie zmieniaj adresu
                  className={({ isActive }) => {
                    let classes = "nav-item";
                    if (isActive) classes += " active";
                    if (isDisabled) classes += " disabled-link"; // Klasa do wyszarzenia
                    return classes;
                  }}
                  onClick={(e) => {
                    if (isDisabled) e.preventDefault(); // Blokada kliknięcia
                  }}
              >
                {item.name}
              </NavLink>
          );
        })}
      </div>
  );
};

export default Sidebar;