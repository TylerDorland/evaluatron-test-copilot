import React, { useState, useEffect } from 'react';
import { queriesAPI, evaluationsAPI } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Analytics() {
  const [queries, setQueries] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const queriesRes = await queriesAPI.list();
      const queriesData = queriesRes.data;
      setQueries(queriesData);

      // Load evaluations for completed queries
      const evaluationPromises = queriesData
        .filter(q => q.status === 'completed')
        .map(q => evaluationsAPI.getForQuery(q.id).catch(() => ({ data: [] })));
      
      const evaluationResults = await Promise.all(evaluationPromises);
      const allEvaluations = evaluationResults.flatMap(r => r.data);
      setEvaluations(allEvaluations);

      // Prepare chart data
      const dataByDate = {};
      queriesData.forEach(query => {
        const date = new Date(query.created_at).toLocaleDateString();
        if (!dataByDate[date]) {
          dataByDate[date] = { date, queries: 0, avgLatency: 0, latencies: [] };
        }
        dataByDate[date].queries += 1;
        if (query.latency_ms) {
          dataByDate[date].latencies.push(query.latency_ms);
        }
      });

      // Calculate average latency
      Object.values(dataByDate).forEach(data => {
        if (data.latencies.length > 0) {
          data.avgLatency = Math.round(
            data.latencies.reduce((a, b) => a + b, 0) / data.latencies.length
          );
        }
        delete data.latencies;
      });

      setChartData(Object.values(dataByDate));
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const completedQueries = queries.filter(q => q.status === 'completed');
    const avgLatency = completedQueries.length > 0
      ? Math.round(completedQueries.reduce((sum, q) => sum + (q.latency_ms || 0), 0) / completedQueries.length)
      : 0;

    const sentimentEvals = evaluations.filter(e => e.evaluation_type === 'sentiment');
    const avgSentiment = sentimentEvals.length > 0
      ? (sentimentEvals.reduce((sum, e) => sum + (e.score || 0), 0) / sentimentEvals.length).toFixed(2)
      : 0;

    const clarityEvals = evaluations.filter(e => e.evaluation_type === 'clarity');
    const avgClarity = clarityEvals.length > 0
      ? (clarityEvals.reduce((sum, e) => sum + (e.score || 0), 0) / clarityEvals.length).toFixed(2)
      : 0;

    return { avgLatency, avgSentiment, avgClarity };
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  const stats = calculateStats();

  return (
    <div>
      <h2>Analytics</h2>

      <div className="grid">
        <div className="stat-card">
          <h3>Average Latency</h3>
          <p className="value">{stats.avgLatency}ms</p>
        </div>
        <div className="stat-card">
          <h3>Average Sentiment</h3>
          <p className="value">{stats.avgSentiment}</p>
        </div>
        <div className="stat-card">
          <h3>Average Clarity</h3>
          <p className="value">{stats.avgClarity}</p>
        </div>
      </div>

      <div className="card">
        <h3>Queries Over Time</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="queries" stroke="#8884d8" name="Queries" />
              <Line type="monotone" dataKey="avgLatency" stroke="#82ca9d" name="Avg Latency (ms)" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p>No data available for visualization.</p>
        )}
      </div>

      <div className="card">
        <h3>Provider Performance</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Provider</th>
              <th>Total Queries</th>
              <th>Success Rate</th>
              <th>Avg Latency</th>
            </tr>
          </thead>
          <tbody>
            {['openai', 'anthropic', 'google'].map(provider => {
              const providerQueries = queries.filter(q => q.llm_provider === provider);
              const completed = providerQueries.filter(q => q.status === 'completed');
              const successRate = providerQueries.length > 0
                ? ((completed.length / providerQueries.length) * 100).toFixed(1)
                : 0;
              const avgLatency = completed.length > 0
                ? Math.round(completed.reduce((sum, q) => sum + (q.latency_ms || 0), 0) / completed.length)
                : 0;

              return (
                <tr key={provider}>
                  <td style={{ textTransform: 'capitalize' }}>{provider}</td>
                  <td>{providerQueries.length}</td>
                  <td>{successRate}%</td>
                  <td>{avgLatency}ms</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Analytics;
