// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const themeToggle = document.getElementById('themeToggle');
const clearChat = document.getElementById('clearChat');

// API Configuration
const API_URL = 'https://college-enquiry-chatbot-1-enxg.onrender.com';

// State
let isDarkMode = false;
let messageHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadChatHistory();
    autoResizeTextarea();
});

function setupEventListeners() {
    userInput.addEventListener('input', handleInput);
    userInput.addEventListener('keydown', handleKeyDown);
    sendButton.addEventListener('click', sendMessage);
    themeToggle.addEventListener('click', toggleTheme);
    clearChat.addEventListener('click', clearChatHistory);
    
    document.querySelectorAll('.quick-question').forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.textContent;
            sendMessage();
        });
    });
}

function handleInput() {
    const hasText = userInput.value.trim().length > 0;
    sendButton.disabled = !hasText;
    autoResizeTextarea();
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendButton.disabled) {
            sendMessage();
        }
    }
}

function autoResizeTextarea() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 100) + 'px';
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    userInput.value = '';
    handleInput();
    
    typingIndicator.classList.add('active');
    
    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        typingIndicator.classList.remove('active');
        
        setTimeout(() => {
            addMessage(data.response, 'bot', data);
        }, 300);
        
    } catch (error) {
        console.error('Error:', error);
        typingIndicator.classList.remove('active');
        addMessage('Sorry, I am having trouble connecting to the server.', 'bot');
    }
}

function addMessage(text, sender, data = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const time = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    
    // Convert markdown-style formatting to HTML
    let formattedText = text
        // Convert **bold** to <strong>
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Convert newlines to <br>
        .replace(/\n/g, '<br>')
        // Add spacing for bullet points
        .replace(/•/g, '•')
        // Handle numbered emojis
        .replace(/(\d+️⃣)/g, '<strong>$1</strong>');
    
    // Handle indentation (spaces)
    formattedText = formattedText.replace(/ {2,}/g, match => {
        return '&nbsp;'.repeat(match.length);
    });
    
    // Ensure proper spacing between sections
    formattedText = formattedText.replace(/<br><br>/g, '<br><br>');
    
    const messageContent = `<div class="message-text">${formattedText}</div>`;
    
    messageDiv.innerHTML = `
        <div class="avatar">
            <i class="fas fa-${sender === 'bot' ? 'robot' : 'user'}"></i>
        </div>
        <div class="message-content">
            ${messageContent}
        </div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    messageHistory.push({ text, sender, time });
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/api/history`);
        const history = await response.json();
        
        if (history && history.length > 0) {
            chatMessages.innerHTML = '';
            history.forEach(item => {
                addMessage(item.question, 'user');
                addMessage(item.answer, 'bot');
            });
        }
    } catch (error) {
        console.log('No history loaded');
    }
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode', isDarkMode);
    themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    localStorage.setItem('darkMode', isDarkMode);
}

function loadThemePreference() {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        isDarkMode = true;
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

function clearChatHistory() {
    if (confirm('Clear chat history?')) {
        chatMessages.innerHTML = `
            <div class="message bot">
                <div class="avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    <p>Hello! 👋 Welcome to College Enquiry Chatbot. How can I help you today?</p>
                    <div class="quick-questions">
                        <button class="quick-question">Admission process</button>
                        <button class="quick-question">Courses offered</button>
                        <button class="quick-question">Fee structure</button>
                        <button class="quick-question">Placement records</button>
                        <button class="quick-question">Hostel facilities</button>
                        <button class="quick-question">Find route from A to G</button>
                    </div>
                </div>
                <div class="message-time">Just now</div>
            </div>
        `;
        setupEventListeners();
    }
}

loadThemePreference();