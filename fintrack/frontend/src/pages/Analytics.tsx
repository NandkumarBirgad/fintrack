import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import api from '../api';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  Legend
} from 'recharts';
import './Analytics.css';

interface MonthlyData {
  month: number;
  income: string;
  expenses: string;
}

interface CategoryData {
  category: string;
  total: string;
}

export default function Analytics() {
  const { user } = useAuth();
  const [data, setData] = useState<MonthlyData[]>([]);
  const [categories, setCategories] = useState<CategoryData[]>([]);
  const [loading, setLoading] = useState(true);

  if (user?.role === 'viewer') return <Navigate to="/dashboard" />;

  useEffect(() => {
    Promise.all([
      api.get('/analytics/monthly?year=2024'),
      api.get('/analytics/categories?type=expense')
    ]).then(([monthlyRes, catRes]) => {
      setData(monthlyRes.data.data);
      setCategories(catRes.data.data);
    }).finally(() => setLoading(false));
  }, []);

  const chartData = data.map(d => ({
    name: new Date(2024, d.month - 1, 1).toLocaleString('default', { month: 'short' }),
    Income: parseFloat(d.income),
    Expense: parseFloat(d.expenses)
  }));

  const expenseData = categories.map(c => ({
    name: c.category,
    Amount: parseFloat(c.total)
  }));

  return (
    <>
      <header className="top-header">
        <div>
          <h1 className="page-title">Simple Analytics</h1>
          <p className="subtitle">Clear, easy to read charts tracking your money.</p>
        </div>
      </header>

      {loading ? (
        <div className="loader">Crunching numbers...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* Monthly Income vs Expense Bar Chart */}
          <div className="glass-panel" style={{ padding: '32px', height: '400px' }}>
            <h3 style={{ marginBottom: '8px' }}>Month-by-Month: Income vs Expense</h3>
            <p className="text-secondary" style={{ marginBottom: '24px' }}>See exactly how much you earned and spent each month.</p>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" tickFormatter={(val) => `$${val}`} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1E1E26', borderColor: '#333', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                  formatter={(value) => `$${value}`}
                />
                <Legend iconType="circle" />
                <Bar dataKey="Income" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Expense" fill="#EF4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Expenses by Category Bar Chart */}
          <div className="glass-panel" style={{ padding: '32px', height: '400px' }}>
            <h3 style={{ marginBottom: '8px' }}>Where did your money go? (By Category)</h3>
            <p className="text-secondary" style={{ marginBottom: '24px' }}>A clear list showing which category cost you the most.</p>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={expenseData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(val) => `$${val}`} />
                <YAxis dataKey="name" type="category" stroke="#94A3B8" />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1E1E26', borderColor: '#333', borderRadius: '8px' }}
                  itemStyle={{ color: '#EF4444' }}
                  formatter={(value) => `$${value}`}
                />
                <Bar dataKey="Amount" fill="#F59E0B" radius={[0, 4, 4, 0]} barSize={30} label={{ position: 'right', fill: '#fff', formatter: (val: any) => `$${val}` }} />
              </BarChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}
    </>
  );
}
