import MessageList from './MessageList.js';
import MessageInput from './MessageInput.js';

class ChatWindow {
    constructor(options) {
        this.apiUrl = 'http://localhost:5000/chat';
        this.messageList = new MessageList(options.messageListSelector);
        this.messageInput = new MessageInput(options.messageInputSelector, options.sendButtonSelector);
        this.isWaitingForResponse = false;
    }

    async sendMessage() {
        const message = this.messageInput.getValue().trim();
        
        if (message === '' || this.isWaitingForResponse) {
            return;
        }

        // Add user message to the UI
        this.messageList.addMessage(message, 'user');
        
        // Clear the input field
        this.messageInput.clear();
        
        // Disable input while waiting for response
        this.isWaitingForResponse = true;
        this.messageInput.setDisabled(true);
        
        // Show typing indicator
        this.messageList.showTypingIndicator();
        
        try {
            // Send the message to the API
            const response = await this.queryAPI(message);
            
            // Remove typing indicator
            this.messageList.hideTypingIndicator();
            
            // Add bot response to the UI
            if (response && response.answer) {
                this.messageList.addMessage(response.answer, 'bot');
            } else {
                this.messageList.addMessage("Sorry, I couldn't process your request. Please try again.", 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            this.messageList.hideTypingIndicator();
            this.messageList.addMessage("There was an error processing your request. Please try again later.", 'bot');
        } finally {
            // Re-enable input
            this.isWaitingForResponse = false;
            this.messageInput.setDisabled(false);
            this.messageInput.focus();
        }
    }

    async queryAPI(question) {
        const response = await fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return await response.json();
    }
}

export default ChatWindow;