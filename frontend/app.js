// Main application code
import MessageList from './components/MessageList.js';
import MessageInput from './components/MessageInput.js';
import ChatWindow from './components/ChatWindow.js';

// Initialize the chat components
document.addEventListener('DOMContentLoaded', () => {
    // Create the chat components
    const chatWindow = new ChatWindow({
        messageListSelector: '#messages-container',
        messageInputSelector: '#user-input',
        sendButtonSelector: '#send-button'
    });

    // Handle send button click
    document.getElementById('send-button').addEventListener('click', () => {
        chatWindow.sendMessage();
    });

    // Handle Enter key for sending message
    document.getElementById('user-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatWindow.sendMessage();
        }
    });

    // Handle input field auto-resize
    const userInput = document.getElementById('user-input');
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });
});