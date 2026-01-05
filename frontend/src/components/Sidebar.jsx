import { NavLink } from 'react-router-dom';


const Sidebar = () => {
  const menuItems = [
    { name: 'Login', path: '/login' },
    { name: 'Add an employee', path: '/add-employee' },
    { name: 'Generate QR Code', path: '/generate-qr' },
    { name: 'Add face pictures', path: '/add-face' },
    { name: 'Remove an employee', path: '/remove-employee' },
    { name: 'Reports', path: '/reports' },
  ];

  return (
    <div className="sidebar">
      {menuItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}
        >
          {item.name}
        </NavLink>
      ))}
    </div>
  );
};

export default Sidebar;