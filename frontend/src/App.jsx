import { useEffect, useState } from 'react';
import { fetchModels, sendChatMessage } from './api/agents';

const commandHelp = [
  '/clear — Clear the chat',
  '/help — List available commands',
  '/imin — Activate black and green hacker mode',
];

const defaultMessages = [
  { role: 'system', content: 'Use /help for available commands.' },
];

export default function App() {
  const [theme, setTheme] = useState('light');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [messages, setMessages] = useState(defaultMessages);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('Loading available models…');

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const modelList = await fetchModels();
        if (!active) return;
        setModels(modelList);
        if (modelList.length > 0) {
          setSelectedModel(modelList[0]);
          setStatus(`Ready. Selected model: ${modelList[0]}`);
        } else {
          setStatus('No Ollama models found.');
        }
      } catch (error) {
        if (!active) return;
        setStatus('Unable to contact Ollama. Check the backend service.');
      }
    })();

    return () => {
      active = false;
    };
  }, []);

  const addMessage = (role, content) => {
    setMessages((current) => [...current, { role, content }]);
  };

  const handleCommand = (rawInput) => {
    const command = rawInput.trim();
    if (!command) return;

    if (command === '/clear') {
      setMessages([{ role: 'system', content: 'Chat cleared. Start a new conversation anytime.' }]);
      setStatus('Chat cleared.');
      return;
    }

    if (command === '/help') {
      addMessage('assistant', commandHelp.join('\n'));
      setStatus('Command help displayed.');
      return;
    }

    if (command === '/imin') {
      setTheme('hacker');
      addMessage('assistant', 'Hacker mode enabled. Welcome to the black and green terminal aesthetic.');
      setStatus('Theme switched to hacker mode.');
      return;
    }

    addMessage('assistant', 'Unrecognised command. Type /help to see available commands.');
    setStatus('Unrecognised command.');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    if (trimmed.startsWith('/')) {
      handleCommand(trimmed);
      setInput('');
      return;
    }

    if (!selectedModel) {
      setStatus('No model selected.');
      return;
    }

    const nextMessages = [...messages, { role: 'user', content: trimmed }];
    addMessage('user', trimmed);
    setInput('');
    setStatus(`Waiting for ${selectedModel}…`);

    try {
      const response = await sendChatMessage(selectedModel, nextMessages);
      addMessage('assistant', response);
      setStatus(`Received response from ${selectedModel}`);
    } catch (error) {
      addMessage('assistant', `Error: ${error.message}`);
      setStatus('Model request failed.');
    }
  };

  return (
    <div className={`app ${theme}`}>
      <header className="topbar">
        <div>
          <p className="eyebrow">Parallax</p>
          <h1>Ollama Chat</h1>
        </div>

        <div className="toolbar">
          <label className="select-wrap" htmlFor="modelSelect">
            Model
            <select id="modelSelect" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
              {models.length === 0 ? (
                <option value="">No models found</option>
              ) : (
                models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))
              )}
            </select>
          </label>
          <button type="button" className="secondary-btn" onClick={() => setSettingsOpen(true)}>
            Settings
          </button>
        </div>
      </header>

      <main className="chat-shell">
        <p className="status-bar">{status}</p>

        <div className="chat-feed" aria-live="polite">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
              {message.content}
            </div>
          ))}
        </div>

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            className="message-input"
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type a message or command…"
            aria-label="Message input"
          />
          <button type="submit" className="primary-btn">
            Send
          </button>
        </form>
      </main>

      <aside className={`settings-panel ${settingsOpen ? 'open' : ''}`} aria-label="Settings panel">
        <div className="settings-header">
          <div>
            <p className="eyebrow">Settings</p>
            <h2>Appearance</h2>
          </div>
          <button type="button" className="close-btn" onClick={() => setSettingsOpen(false)}>
            ×
          </button>
        </div>

        <div className="settings-card">
          <div className="radio-row">
            <label>
              <input
                type="radio"
                name="theme"
                checked={theme === 'light'}
                onChange={() => setTheme('light')}
              />
              Light
            </label>
            <label>
              <input
                type="radio"
                name="theme"
                checked={theme === 'dark'}
                onChange={() => setTheme('dark')}
              />
              Dark
            </label>
          </div>
        </div>

        <div className="settings-card">
          <p className="eyebrow">Commands</p>
          <ul className="command-box">
            {commandHelp.map((command) => (
              <li key={command}>
                <code>{command.split(' — ')[0]}</code> — {command.split(' — ')[1]}
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
}
