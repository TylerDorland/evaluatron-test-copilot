import React, { useState, useEffect } from 'react';
import { scheduledTestsAPI, topicsAPI } from '../services/api';

function ScheduledTests() {
  const [tests, setTests] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    prompt_template: '',
    llm_providers: ['openai'],
    topic_id: '',
    cron_expression: '0 9 * * *',
    evaluation_types: ['sentiment', 'clarity'],
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [testsRes, topicsRes] = await Promise.all([
        scheduledTestsAPI.list(),
        topicsAPI.list(),
      ]);
      setTests(testsRes.data);
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
      await scheduledTestsAPI.create(data);
      setShowForm(false);
      setFormData({
        name: '',
        prompt_template: '',
        llm_providers: ['openai'],
        topic_id: '',
        cron_expression: '0 9 * * *',
        evaluation_types: ['sentiment', 'clarity'],
      });
      loadData();
    } catch (error) {
      console.error('Error creating scheduled test:', error);
      alert('Failed to create scheduled test');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (testId, currentStatus) => {
    try {
      await scheduledTestsAPI.update(testId, !currentStatus);
      loadData();
    } catch (error) {
      console.error('Error toggling test status:', error);
      alert('Failed to update test status');
    }
  };

  const handleProviderChange = (provider) => {
    const providers = formData.llm_providers.includes(provider)
      ? formData.llm_providers.filter(p => p !== provider)
      : [...formData.llm_providers, provider];
    setFormData({ ...formData, llm_providers: providers });
  };

  const handleEvaluationTypeChange = (type) => {
    const types = formData.evaluation_types.includes(type)
      ? formData.evaluation_types.filter(t => t !== type)
      : [...formData.evaluation_types, type];
    setFormData({ ...formData, evaluation_types: types });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Scheduled Tests</h2>
        <button className="button" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Scheduled Test'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3>Create Scheduled Test</h3>
          <form onSubmit={handleSubmit}>
            <div>
              <label className="label">Test Name</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="label">Prompt Template</label>
              <textarea
                className="textarea"
                value={formData.prompt_template}
                onChange={(e) => setFormData({ ...formData, prompt_template: e.target.value })}
                placeholder="Enter your prompt template..."
                required
              />
            </div>

            <div>
              <label className="label">LLM Providers</label>
              <div>
                {['openai', 'anthropic', 'google'].map(provider => (
                  <label key={provider} style={{ display: 'block', marginBottom: '5px' }}>
                    <input
                      type="checkbox"
                      checked={formData.llm_providers.includes(provider)}
                      onChange={() => handleProviderChange(provider)}
                    />
                    {' ' + provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="label">Evaluation Types</label>
              <div>
                {['sentiment', 'clarity', 'accuracy'].map(type => (
                  <label key={type} style={{ display: 'block', marginBottom: '5px' }}>
                    <input
                      type="checkbox"
                      checked={formData.evaluation_types.includes(type)}
                      onChange={() => handleEvaluationTypeChange(type)}
                    />
                    {' ' + type.charAt(0).toUpperCase() + type.slice(1)}
                  </label>
                ))}
              </div>
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

            <div>
              <label className="label">Cron Expression</label>
              <input
                type="text"
                className="input"
                value={formData.cron_expression}
                onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
                placeholder="0 9 * * * (Daily at 9 AM)"
                required
              />
              <small style={{ color: '#666' }}>
                Examples: "0 9 * * *" (daily at 9 AM), "0 */6 * * *" (every 6 hours)
              </small>
            </div>

            <button type="submit" className="button" disabled={loading}>
              {loading ? 'Creating...' : 'Create Scheduled Test'}
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3>Scheduled Tests</h3>
        {tests.length === 0 ? (
          <p>No scheduled tests yet.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Providers</th>
                <th>Schedule</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tests.map((test) => (
                <tr key={test.id}>
                  <td>{test.name}</td>
                  <td>{test.llm_providers.join(', ')}</td>
                  <td>{test.cron_expression}</td>
                  <td>
                    <span className={`badge badge-${test.is_active ? 'success' : 'danger'}`}>
                      {test.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="button button-secondary"
                      style={{ fontSize: '12px', padding: '5px 10px' }}
                      onClick={() => handleToggleActive(test.id, test.is_active)}
                    >
                      {test.is_active ? 'Deactivate' : 'Activate'}
                    </button>
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

export default ScheduledTests;
