import React, { useState, useEffect } from 'react';
import { queriesAPI, topicsAPI, evaluationsAPI } from '../services/api';

function Dashboard() {
  const [queries, setQueries] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalQueries: 0,
    completedQueries: 0,
    failedQueries: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [queriesRes, topicsRes] = await Promise.all([
        queriesAPI.list({ limit: 10 }),
        topicsAPI.list(),
      ]);

      const queriesData = queriesRes.data;
      setQueries(queriesData);
      setTopics(topicsRes.data);

      // Calculate stats
      setStats({
        totalQueries: queriesData.length,
        completedQueries: queriesData.filter(q => q.status === 'completed').length,
        failedQueries: queriesData.filter(q => q.status === 'failed').length,
      });
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="grid">
        <div className="stat-card">
          <h3>Total Queries</h3>
          <p className="value">{stats.totalQueries}</p>
        </div>
        <div className="stat-card">
          <h3>Completed</h3>
          <p className="value">{stats.completedQueries}</p>
        </div>
        <div className="stat-card">
          <h3>Failed</h3>
          <p className="value">{stats.failedQueries}</p>
        </div>
      </div>

      <div className="card">
        <h3>Recent Queries</h3>
        {queries.length === 0 ? (
          <p>No queries yet. Start by creating a new query!</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Provider</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {queries.map((query) => (
                <tr key={query.id}>
                  <td>{query.id}</td>
                  <td>{query.llm_provider}</td>
                  <td>
                    <span className={`badge badge-${query.status === 'completed' ? 'success' : query.status === 'failed' ? 'danger' : 'warning'}`}>
                      {query.status}
                    </span>
                  </td>
                  <td>{new Date(query.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>Topics</h3>
        {topics.length === 0 ? (
          <p>No topics yet. Create a topic to organize your queries!</p>
        ) : (
          <div className="grid">
            {topics.map((topic) => (
              <div key={topic.id} className="card">
                <h4>{topic.name}</h4>
                <p>{topic.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
