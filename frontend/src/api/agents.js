export async function fetchModels() {
  const response = await fetch('/api/models');
  if (!response.ok) {
    throw new Error('Unable to fetch Ollama models');
  }
  const payload = await response.json();
  return payload.models || [];
}

export async function sendChatMessage(model, messages) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || 'Chat request failed');
  }

  return payload.response || '';
}
