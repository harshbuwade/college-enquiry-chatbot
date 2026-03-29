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

// Event Listeners
function setupEventListeners() {
    userInput.addEventListener('input', handleInput);
    userInput.addEventListener('keydown', handleKeyDown);
    sendButton.addEventListener('click', sendMessage);
    themeToggle.addEventListener('click', toggleTheme);
    clearChat.addEventListener('click', clearChatHistory);
    
    // Quick question buttons
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

// Send Message
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    handleInput();
    
    // Show typing indicator
    typingIndicator.classList.add('active');
    
    try {
        // Send to backend
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.classList.remove('active');
        
        // Add bot response
        setTimeout(() => {
            addMessage(data.response, 'bot', data);
        }, 500);
        
    } catch (error) {
        console.error('Error:', error);
        typingIndicator.classList.remove('active');
        
        let errorMessage = 'Sorry, I am having trouble connecting to the server. ';
        
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Please make sure the backend server is running at http://localhost:5000';
        } else {
            errorMessage += 'Please try again later.';
        }
        
        addMessage(errorMessage, 'bot');
    }
}

// Add message to chat
function addMessage(text, sender, data = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const time = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    
    let messageContent = `<p>${text}</p>`;
    
    // Add entity information if available
    if (data && data.entities) {
        const entities = [];
        if (data.entities.courses && data.entities.courses.length) {
            entities.push(`📚 Courses: ${data.entities.courses.join(', ')}`);
        }
        if (data.entities.dates && data.entities.dates.length) {
            entities.push(`📅 Dates: ${data.entities.dates.join(', ')}`);
        }
        if (data.entities.fees && data.entities.fees.length) {
            entities.push(`💰 Fees: ${data.entities.fees.join(', ')}`);
        }
        
        if (entities.length > 0) {
            messageContent += `<small style="display: block; margin-top: 8px; opacity: 0.8;">${entities.join(' • ')}</small>`;
        }
    }
    
    // Add sentiment indicator for bot messages
    if (sender === 'bot' && data && data.sentiment && data.sentiment !== 'neutral') {
        const sentimentEmoji = data.sentiment === 'positive' ? '😊' : '😟';
        messageContent += `<small style="display: block; margin-top: 4px; opacity: 0.6;">${sentimentEmoji}</small>`;
    }
    
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
    
    // Save to history
    messageHistory.push({ text, sender, time });
}

// Load chat history
async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/api/history`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const history = await response.json();
        
        if (history && history.length > 0) {
            // Clear welcome message
            chatMessages.innerHTML = '';
            
            // Add history messages in chronological order
            history.forEach(item => {
                addMessage(item.question, 'user');
                addMessage(item.answer, 'bot');
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
        // Don't show error to user, just keep welcome message
    }
}

// Toggle theme
function toggleTheme() {
    isDarkMode = !isDarkMode;
    
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    }
    
    // Save preference to localStorage
    localStorage.setItem('darkMode', isDarkMode);
}

// Load saved theme preference
function loadThemePreference() {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        isDarkMode = true;
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// Clear chat history
function clearChatHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Clear messages but keep welcome message
        chatMessages.innerHTML = `
            <div class="message bot">
                <div class="avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>Hello! 👋 Welcome to College Enquiry Chatbot. How can I help you today?</p>
                    <div class="quick-questions">
                        <button class="quick-question">Admission process</button>
                        <button class="quick-question">Courses offered</button>
                        <button class="quick-question">Fee structure</button>
                        <button class="quick-question">Placement records</button>
                        <button class="quick-question">Hostel facilities</button>
                        <button class="quick-question">Library timings</button>
                    </div>
                </div>
                <div class="message-time">Just now</div>
            </div>
        `;
        
        // Reattach quick question listeners
        document.querySelectorAll('.quick-question').forEach(btn => {
            btn.addEventListener('click', () => {
                userInput.value = btn.textContent;
                sendMessage();
            });
        });
        
        messageHistory = [];
        
        // Optionally clear backend history
        // This would need an API endpoint
    }
}

// Add suggestion chips based on context
function addSuggestionChips(chips) {
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'quick-questions';
    
    chips.forEach(chip => {
        const button = document.createElement('button');
        button.className = 'quick-question';
        button.textContent = chip;
        button.addEventListener('click', () => {
            userInput.value = chip;
            sendMessage();
        });
        suggestionsDiv.appendChild(button);
    });
    
    // Add to last bot message
    const lastMessage = chatMessages.lastElementChild;
    if (lastMessage && lastMessage.classList.contains('bot')) {
        const contentDiv = lastMessage.querySelector('.message-content');
        contentDiv.appendChild(suggestionsDiv);
    }
}

// Handle connection status
let connectionCheckInterval;

function startConnectionCheck() {
    // Check connection every 30 seconds
    connectionCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_URL}/api/health`);
            if (response.ok) {
                console.log('Backend connection OK');
            }
        } catch (error) {
            console.warn('Backend connection lost:', error);
        }
    }, 30000);
}

function stopConnectionCheck() {
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
    }
}

// Initialize on page load
loadThemePreference();
startConnectionCheck();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopConnectionCheck();
});

// Export for debugging (optional)
window.debug = {
    messageHistory,
    API_URL,
    sendMessage,
    clearChatHistory
};