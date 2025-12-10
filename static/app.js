class Chat {
    constructor() {
        this.container = document.getElementById('messagesContainer');
        this.input = document.getElementById('messageInput');
        this.form = document.getElementById('chatForm');
        this.history = [];

        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.send();
        });
    }

    send() {
        const text = this.input.value.trim();
        if (!text) return;

        this.addMessage(text, 'user');
        this.input.value = '';

        this.fetch(text);
    }

    addMessage(text, sender) {
        const msg = document.createElement('div');
        msg.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'Tú' : 'IA';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;

        msg.appendChild(avatar);
        msg.appendChild(content);
        this.container.appendChild(msg);

        this.container.scrollTop = this.container.scrollHeight;

        if (sender === 'user') {
            this.history.push({ sender: 'Usuario', text });
        } else {
            this.history.push({ sender: 'Asistente', text });
        }
    }

    async fetch(text) {
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, history: this.history })
            });

            const data = await res.json();

            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Error: ' + (data.error || 'No se pudo procesar'), 'bot');
            }
        } catch (e) {
            console.error(e);
            this.addMessage('Error de conexión', 'bot');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Chat();
});