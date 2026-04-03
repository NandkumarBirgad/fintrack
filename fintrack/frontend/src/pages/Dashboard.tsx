import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import { Wallet, TrendingUp, TrendingDown, Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import './Dashboard.css';

interface Summary {
  total_income: number;
  total_expenses: number;
  net_balance: number;
  savings_percentage: string;
}

interface Alert {
  type: string;
  message: string;
}

interface Transaction {
  id: number;
  amount: string;
  type: string;
  category: string;
  date: string;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [recent, setRecent] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumRes, recRes, alertsRes] = await Promise.all([
          api.get('/analytics/summary'),
          api.get('/analytics/recent?limit=5'),
          api.get('/analytics/alerts')
        ]);
        setSummary(sumRes.data.data);
        setRecent(recRes.data.data);
        setAlerts(alertsRes.data.data || []);
      } catch (err) {
        console.error("Error fetching dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    if (user) fetchData();
  }, [user]);

  return (
    <>
      <header className="top-header">
        <div>
          <h1 className="page-title">Overview</h1>
          <p className="subtitle">Welcome back, here's your financial summary.</p>
        </div>
      </header>

      {loading ? (
        <div className="loader">Loading your workspace...</div>
      ) : (
        <>
          {alerts.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
              {alerts.map((alert, idx) => (
                <div key={idx} style={{
                  background: alert.type === 'warning' ? 'var(--status-danger-bg)' : 'rgba(56, 189, 248, 0.1)',
                  color: alert.type === 'warning' ? 'var(--status-danger)' : '#38bdf8',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: `1px solid ${alert.type === 'warning' ? 'rgba(239,68,68,0.2)' : 'rgba(56,189,248,0.2)'}`,
                  fontSize: '14px',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>{alert.type === 'warning' ? '⚠️' : '💡'}</span>
                  {alert.message}
                </div>
              ))}
            </div>
          )}

          <div className="stats-grid">
            <motion.div initial={{opacity:0, y:20}} animate={{opacity:1,y:0}} transition={{delay: 0.1}} className="stat-card glass-panel">
              <div className="stat-header">
                <span className="text-secondary">Net Balance</span>
                <div className="icon-badge primary"><Wallet size={18}/></div>
              </div>
              <h3>${summary?.net_balance !== undefined ? Number(summary.net_balance).toFixed(2) : '0.00'}</h3>
              <p style={{marginTop: '8px', fontSize: '13px', color: 'var(--status-success)'}}>
                {summary?.savings_percentage}% Savings Rate
              </p>
            </motion.div>

            <motion.div initial={{opacity:0, y:20}} animate={{opacity:1,y:0}} transition={{delay: 0.2}} className="stat-card glass-panel">
              <div className="stat-header">
                <span className="text-secondary">Total Income</span>
                <div className="icon-badge success"><TrendingUp size={18}/></div>
              </div>
              <h3>${summary?.total_income !== undefined ? Number(summary.total_income).toFixed(2) : '0.00'}</h3>
            </motion.div>

            <motion.div initial={{opacity:0, y:20}} animate={{opacity:1,y:0}} transition={{delay: 0.3}} className="stat-card glass-panel">
              <div className="stat-header">
                <span className="text-secondary">Total Expenses</span>
                <div className="icon-badge danger"><TrendingDown size={18}/></div>
              </div>
              <h3>${summary?.total_expenses !== undefined ? Number(summary.total_expenses).toFixed(2) : '0.00'}</h3>
            </motion.div>
          </div>

          <motion.div initial={{opacity:0, y:20}} animate={{opacity:1,y:0}} transition={{delay: 0.4}} className="recent-section glass-panel">
            <div className="section-header">
              <h2>Recent Activity</h2>
            </div>
            <div className="transaction-list">
              {recent.length === 0 ? (
                <p className="empty-state">No recent transactions found.</p>
              ) : (
                recent.map(txn => (
                  <div key={txn.id} className="transaction-item">
                    <div className="txn-info">
                      <div className={`txn-icon ${txn.type}`}>
                        {txn.type === 'income' ? <TrendingUp size={16}/> : <TrendingDown size={16}/>}
                      </div>
                      <div>
                        <h4>{txn.category}</h4>
                        <span className="txn-date">{new Date(txn.date).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className={`txn-amount ${txn.type}`}>
                      {txn.type === 'income' ? '+' : '-'}${Number(txn.amount).toFixed(2)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        </>
      )}
    </>
  );
}
