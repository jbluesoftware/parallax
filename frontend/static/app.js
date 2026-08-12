const modelSelect = document.getElementById('modelSelect');
const chatFeed = document.getElementById('chatFeed');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const statusText = document.getElementById('statusText');
const settingsToggle = document.getElementById('settingsToggle');
const settingsPanel = document.getElementById('settingsPanel');
const closeSettings = document.getElementById('closeSettings');
const themeRadios = document.querySelectorAll('input[name="theme"]');

let conversation = [{ role: 'system', content: 'Use /help for available commands.' }];

function addMessage(role, content) {
  const node = document.createElement('div');
  node.className = `message ${role}`;
  node.textContent = content;
  chatFeed.appendChild(node);
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

function setTheme(themeName) {
  document.body.classList.remove('light', 'dark', 'hacker');
  document.body.classList.add(themeName);
  themeRadios.forEach((input) => {
    input.checked = input.value === themeName;
  });
}

function setStatus(text) {
  statusText.textContent = text;
}

async function fetchModels() {
  try {
    const response = await fetch('/api/models');
    const payload = await response.json();
    const models = Array.isArray(payload.models) ? payload.models : [];
    modelSelect.innerHTML = '';
    if (!models.length) {
      modelSelect.innerHTML = '<option value="">No models found</option>';
      setStatus('No Ollama models are available.');
      return;
    }

    models.forEach((model) => {
      const option = document.createElement('option');
      option.value = model;
      option.textContent = model;
      modelSelect.appendChild(option);
    });
    modelSelect.value = models[0];
    setStatus(`Ready. Selected model: ${models[0]}`);
  } catch (error) {
    modelSelect.innerHTML = '<option value="">Unavailable</option>';
    setStatus('Unable to contact Ollama. Check the backend service.');
  }
}

function handleCommand(command) {
  const trimmed = command.trim();

  if (trimmed === '/clear') {
    conversation = [{ role: 'system', content: 'Chat cleared. Start a new conversation at any time.' }];
    chatFeed.innerHTML = '';
    addMessage('system', 'Chat cleared. Start a new conversation at any time.');
    setStatus('Chat cleared.');
    return;
  }

  if (trimmed === '/help') {
    addMessage('assistant', '/clear — Clear the chat\n/help — List available commands\n/imin — Activate hacker mode');
    setStatus('Command help displayed.');
    return;
  }

  if (trimmed === '/imin') {
    setTheme('hacker');
    addMessage('assistant', 'Hacker mode enabled. Welcome to the black and green terminal aesthetic.');
    setStatus('Theme switched to hacker mode.');
    return;
  }

  addMessage('assistant', 'Unrecognised command. Type /help to see available commands.');
  setStatus('Unrecognised command.');
}

async function sendChat(text) {
  const model = modelSelect.value;
  if (!model) {
    setStatus('No model selected.');
    return;
  }

  const nextMessages = [...conversation, { role: 'user', content: text }];
  addMessage('user', text);
  setStatus(`Waiting for ${model}…`);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, messages: nextMessages }),
    });

    const payload = await response.json();
    if (!response.ok) {
      addMessage('assistant', `Error: ${payload.detail || 'Request failed'}`);
      setStatus('Model request failed.');
      return;
    }

    const answer = payload.response || '';
    addMessage('assistant', answer);
    conversation = nextMessages.concat({ role: 'assistant', content: answer });
    setStatus(`Received response from ${model}`);
  } catch (error) {
    addMessage('assistant', 'Unable to reach the backend service.');
    setStatus('Connection failed.');
  }
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = messageInput.value.trim();
  if (!value) return;

  if (value.startsWith('/')) {
    handleCommand(value);
    messageInput.value = '';
    return;
  }

  messageInput.value = '';
  await sendChat(value);
});

settingsToggle.addEventListener('click', () => {
  settingsPanel.classList.add('open');
  settingsPanel.setAttribute('aria-hidden', 'false');
});

closeSettings.addEventListener('click', () => {
  settingsPanel.classList.remove('open');
  settingsPanel.setAttribute('aria-hidden', 'true');
});

themeRadios.forEach((radio) => {
  radio.addEventListener('change', (event) => {
    if (event.target.checked) {
      setTheme(event.target.value);
    }
  });
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    settingsPanel.classList.remove('open');
    settingsPanel.setAttribute('aria-hidden', 'true');
  }
});

setTheme('light');
addMessage('system', 'Use /help for available commands.');
fetchModels();
