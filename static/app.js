const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

let conversationHistory = [];

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter (Ctrl+Enter for multiline)
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function formatTime(date) {
    return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
}

function addMessageToUI(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'Usuario' ? 'user' : 'assistant'}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    // Render Markdown safely: convert -> sanitize -> insert HTML
    if (window.marked && window.DOMPurify) {
        try {
            const rawHtml = marked.parse(text || '');
            bubbleDiv.innerHTML = DOMPurify.sanitize(rawHtml);
            // apply syntax highlighting if available
            if (window.hljs) {
                bubbleDiv.querySelectorAll('pre code').forEach((el) => hljs.highlightElement(el));
            }
        } catch (e) {
            bubbleDiv.textContent = text;
        }
    } else {
        bubbleDiv.textContent = text;
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = formatTime(new Date());
    
    messageDiv.appendChild(bubbleDiv);
    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showThinkingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'thinking-indicator';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble thinking';
    bubbleDiv.innerHTML = '<span></span><span></span><span></span> Pensando…';
    
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeThinkingIndicator() {
    const thinkingDiv = document.getElementById('thinking-indicator');
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to UI and history
    addMessageToUI(message, 'Usuario');
    conversationHistory.push({
        sender: 'Usuario',
        text: message,
        timestamp: new Date()
    });
    
    // Clear input and disable button
    messageInput.value = '';
    sendBtn.disabled = true;
    
    // Show thinking indicator
    showThinkingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });
        
        const data = await response.json();
        removeThinkingIndicator();
        
        if (data.success) {
            const assistantMessage = data.response;
            addMessageToUI(assistantMessage, 'Asistente SENA');
            conversationHistory.push({
                sender: 'Asistente SENA',
                text: assistantMessage,
                timestamp: new Date()
            });
        } else {
            const errorMessage = data.error || 'Error desconocido';
            addMessageToUI(errorMessage, 'Asistente SENA');
            conversationHistory.push({
                sender: 'Asistente SENA',
                text: errorMessage,
                timestamp: new Date()
            });
        }
    } catch (error) {
        removeThinkingIndicator();
        const errorMessage = 'Error al conectar con el servidor. Intenta nuevamente.';
        addMessageToUI(errorMessage, 'Asistente SENA');
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}