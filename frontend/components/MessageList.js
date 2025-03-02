class MessageList {
    constructor(selector) {
        this.container = document.querySelector(selector);
        this.typingIndicator = null;
    }

    addMessage(text, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Process text to maintain formatting
        text.split('\n').forEach(line => {
            const paragraph = document.createElement('p');
            paragraph.textContent = line;
            messageContent.appendChild(paragraph);
        });
        
        messageElement.appendChild(messageContent);
        this.container.appendChild(messageElement);
        
        // Scroll to the bottom
        this.scrollToBottom();
    }

    showTypingIndicator() {
        // Create typing indicator
        this.typingIndicator = document.createElement('div');
        this.typingIndicator.className = 'typing-indicator';
        
        // Add the dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            this.typingIndicator.appendChild(dot);
        }
        
        this.container.appendChild(this.typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        if (this.typingIndicator && this.typingIndicator.parentNode) {
            this.typingIndicator.parentNode.removeChild(this.typingIndicator);
            this.typingIndicator = null;
        }
    }

    scrollToBottom() {
        this.container.scrollTop = this.container.scrollHeight;
    }
}

export default MessageList;