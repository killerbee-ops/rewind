const API = {
  async getStats() {
    const res = await fetch('/api/stats');
    return res.json();
  },

  async getRegrets(tag = 'All', search = '') {
    const params = new URLSearchParams();
    if (tag && tag !== 'All') params.append('tag', tag);
    if (search) params.append('search', search);
    const res = await fetch(`/api/regrets?${params.toString()}`);
    return res.json();
  },

  async addRegret(data) {
    const res = await fetch('/api/regrets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async deleteRegret(id) {
    const res = await fetch(`/api/regrets/${id}`, { method: 'DELETE' });
    return res.json();
  },

  async getTodos(status = 'All') {
    const params = new URLSearchParams();
    if (status && status !== 'All') params.append('status', status);
    const res = await fetch(`/api/todos?${params.toString()}`);
    return res.json();
  },

  async evaluateTask(data) {
    const res = await fetch('/api/todos/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async createTodo(data) {
    const res = await fetch('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async updateTodo(id, status) {
    const res = await fetch(`/api/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return res.json();
  },

  async deleteTodo(id) {
    const res = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
    return res.json();
  },

  async getPatterns() {
    const res = await fetch('/api/patterns');
    return res.json();
  },

  async seedData() {
    const res = await fetch('/api/seed', { method: 'POST' });
    return res.json();
  },

  async resetData() {
    const res = await fetch('/api/reset', { method: 'POST' });
    return res.json();
  }
};
