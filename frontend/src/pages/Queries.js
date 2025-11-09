import React, { useState, useEffect } from 'react';
import { queriesAPI, topicsAPI, evaluationsAPI } from '../services/api';

function Queries() {
  const [queries, setQueries] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    prompt: '',
    llm_provider: 'openai',
    model_name: '',
    topic_id: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [queriesRes, topicsRes] = await Promise.all([
        queriesAPI.list(),
        topicsAPI.list(),
      ]);
      setQueries(queriesRes.data);
      setTopics(topicsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = {
        ...formData,
        topic_id: formData.topic_id ? parseInt(formData.topic_id) : null,
      };
      await queriesAPI.create(data);
      setShowForm(false);
      setFormData({ prompt: '', llm_provider: 'openai', model_name: '', topic_id: '' });
      loadData();
    } catch (error) {
      console.error('Error creating query:', error);
      alert('Failed to create query: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async (queryId, evaluationType) => {
    try {
      await evaluationsAPI.create({
        llm_query_id: queryId,
        evaluation_type: evaluationType,
      });
      alert(`${evaluationType} evaluation completed!`);
    } catch (error) {
      console.error('Error running evaluation:', error);
      alert('Failed to run evaluation');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>LLM Queries</h2>
        <button className="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Query'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3>Create New Query</h3>
          <form onSubmit={handleSubmit}>
            <div>
              <label className="label">Prompt</label>
              <textarea
                className="textarea"
                value={formData.prompt}
                onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                placeholder="Enter your prompt here..."
                required
              />
            </div>

            <div>
              <label className="label">LLM Provider</label>
              <select
                className="select"
                value={formData.llm_provider}
                onChange={(e) => setFormData({ ...formData, llm_provider: e.target.value })}
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
              </select>
            </div>

            <div>
              <label className="label">Model Name (Optional)</label>
              <input
                type="text"
                className="input"
                value={formData.model_name}
                onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                placeholder="e.g., gpt-3.5-turbo"
              />
            </div>

            <div>
              <label className="label">Topic (Optional)</label>
              <select
                className="select"
                value={formData.topic_id}
                onChange={(e) => setFormData({ ...formData, topic_id: e.target.value })}
              >
                <option value="">No topic</option>
                {topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="button" disabled={loading}>
              {loading ? 'Creating...' : 'Create Query'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3>Query History</h3>
        {queries.length === 0 ? (
          <p>No queries yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Prompt</th>
                <th>Provider</th>
                <th>Status</th>
                <th>Latency</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {queries.map((query) => (
                <tr key={query.id}>
                  <td>{query.id}</td>
                  <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {query.prompt}
                  </td>
                  <td>{query.llm_provider}</td>
                  <td>
                    <span className={`badge badge-${query.status === 'completed' ? 'success' : query.status === 'failed' ? 'danger' : 'warning'}`}>
                      {query.status}
                    </span>
                  </td>
                  <td>{query.latency_ms ? `${query.latency_ms}ms` : '-'}</td>
                  <td>
                    {query.status === 'completed' && (
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button
                          className="button button-secondary"
                          style={{ fontSize: '12px', padding: '5px 10px' }}
                          onClick={() => handleEvaluate(query.id, 'sentiment')}
                        >
                          Sentiment
                        </button>
                        <button
                          className="button button-secondary"
                          style={{ fontSize: '12px', padding: '5px 10px' }}
                          onClick={() => handleEvaluate(query.id, 'clarity')}
                        >
                          Clarity
                        </button>
                        <button
                          className="button button-secondary"
                          style={{ fontSize: '12px', padding: '5px 10px' }}
                          onClick={() => handleEvaluate(query.id, 'accuracy')}
                        >
                          Accuracy
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Queries;
