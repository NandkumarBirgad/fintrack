import { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';
import { Plus, Trash2, TrendingDown, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import './Transactions.css';

interface Transaction {
  id: number;
  amount: string;
  type: string;
  category: string;
  date: string;
  notes?: string;
}

export default function Transactions() {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form state
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('expense');
  const [category, setCategory] = useState('');
  const [date, setDate] = useState('');
  const [notes, setNotes] = useState('');

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const res = await api.get('/transactions');
      setTransactions(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this transaction?')) return;
    try {
      await api.delete(`/transactions/${id}`);
      fetchTransactions();
    } catch (err) {
      alert('Failed to delete transaction.');
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/transactions', {
        amount: parseFloat(amount),
        type, category, date, notes
      });
      setShowModal(false);
      setAmount(''); setCategory(''); setDate(''); setNotes('');
      fetchTransactions();
    } catch (err) {
      alert('Failed to create transaction. Check permissions.');
    }
  };

  return (
    <>
      <header className="top-header">
        <div>
          <h1 className="page-title">Transactions</h1>
          <p className="subtitle">Manage and track your flow of money.</p>
        </div>
        {user?.role === 'admin' && (
          <button className="btn-action" onClick={() => setShowModal(true)}>
            <Plus size={18} /> New Transaction
          </button>
        )}
      </header>

      {showModal && (
        <div className="modal-backdrop">
          <motion.div initial={{opacity:0, scale:0.95}} animate={{opacity:1, scale:1}} className="modal-content glass-panel">
            <h2>Add Transaction</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Type</label>
                <select value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
              <div className="form-group">
                <label>Category</label>
                <input required type="text" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Rent, Salary" />
              </div>
              <div className="form-group">
                <label>Amount</label>
                <input required type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Date</label>
                <input required type="date" value={date} onChange={(e) => setDate(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Notes</label>
                <input type="text" value={notes} onChange={(e) => setNotes(e.target.value)} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-text" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save</button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {loading ? (
        <div className="loader">Loading transactions...</div>
      ) : (
        <div className="glass-panel tx-table-container">
          <table className="tx-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Category</th>
                <th>Date</th>
                <th>Amount</th>
                {user?.role === 'admin' && <th>Action</th>}
              </tr>
            </thead>
            <tbody>
              {transactions.map(txn => (
                <tr key={txn.id}>
                  <td>
                    <span className={`badge ${txn.type}`}>
                      {txn.type === 'income' ? <TrendingUp size={14}/> : <TrendingDown size={14}/>}
                      {txn.type}
                    </span>
                  </td>
                  <td>{txn.category}</td>
                  <td className="text-secondary">{new Date(txn.date).toLocaleDateString()}</td>
                  <td className={`tx-amount ${txn.type}`}>
                    {txn.type === 'income' ? '+' : '-'}${Number(txn.amount).toFixed(2)}
                  </td>
                  {user?.role === 'admin' && (
                    <td>
                      <button onClick={() => handleDelete(txn.id)} className="btn-icon danger">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan={5} className="empty-state">No transactions found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
