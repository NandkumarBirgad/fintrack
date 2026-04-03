import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api';
import { Shield, Trash2, User as UserIcon } from 'lucide-react';
import './Transactions.css'; // Reuse table stylings

export default function Users() {
  const { user } = useAuth();
  const [usersList, setUsersList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  if (user?.role !== 'admin') return <Navigate to="/dashboard" />;

  const fetchUsers = () => {
    setLoading(true);
    api.get('/users')
      .then(res => setUsersList(res.data.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (targetId: number, currentRole: string) => {
    const roles = ['viewer', 'analyst', 'admin'];
    const nextRole = roles[(roles.indexOf(currentRole) + 1) % roles.length];
    try {
      await api.put(`/users/${targetId}`, { role: nextRole });
      fetchUsers();
    } catch (err) {
      alert("Failed to update role");
    }
  };

  const handleDelete = async (id: number) => {
    if(!confirm("Permenantly delete this user?")) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err) {
      alert("Cannot delete self or failed");
    }
  };

  return (
    <>
      <header className="top-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="subtitle">Administrate workspace members and roles.</p>
        </div>
      </header>

      {loading ? (
        <div className="loader">Fetching users...</div>
      ) : (
        <div className="glass-panel tx-table-container">
          <table className="tx-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Member Since</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {usersList.map(u => (
                <tr key={u.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="avatar" style={{width: 32, height: 32}}><UserIcon size={16}/></div>
                      <span style={{fontWeight: 500}}>{u.name}</span>
                    </div>
                  </td>
                  <td className="text-secondary">{u.email}</td>
                  <td>
                    <button 
                      onClick={() => handleRoleChange(u.id, u.role)}
                      className={`badge ${u.role === 'admin' ? 'income' : 'expense'}`}
                      style={{ cursor: 'pointer', border: 'none' }}
                      title="Click to cycle role"
                    >
                      <Shield size={12}/> {u.role}
                    </button>
                  </td>
                  <td className="text-tertiary">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    {u.id !== user.id && (
                      <button onClick={() => handleDelete(u.id)} className="btn-icon danger">
                        <Trash2 size={16} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
