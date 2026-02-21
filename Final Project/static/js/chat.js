// AgriSahayak Chatbot JavaScript
let allowApply = false;

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        addMessage(data.reply, 'bot');
        allowApply = data.allow_apply;
        
        // Check if bot asks about applying and show apply button
        const botMessage = data.reply.toLowerCase();
        const asksAboutApplying = botMessage.includes('apply for any of these schemes') || 
                                botMessage.includes('would you like to apply') ||
                                botMessage.includes('क्या आप इनमें से किसी योजना के लिए आवेदन करना चाहेंगे') ||
                                botMessage.includes('तुम्ही यापैका कोणत्या योजनांसाठी अर्ज करू इच्छित का');
        
        // Show/hide apply button
        const applySection = document.getElementById('applySection');
        if (allowApply || asksAboutApplying) {
            applySection.style.display = 'block';
        } else {
            applySection.style.display = 'none';
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addMessage('I can help you with crop damage, government schemes, and farming advice. Please tell me your crop and issue.', 'bot');
        console.error('Error:', error);
    });
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message fade-in`;
    
    const alertClass = sender === 'user' ? 'alert-primary' : 'alert-info';
    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const alignment = sender === 'user' ? 'text-right' : 'text-left';
    
    messageDiv.innerHTML = `
        <div class="alert ${alertClass} ${alignment}" style="display: inline-block;">
            <i class="${icon}"></i> ${message}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
        <div class="alert alert-info" style="display: inline-block;">
            <i class="fas fa-robot"></i> 
            <span class="spinner">●</span> Thinking...
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function applyForScheme() {
    if (!allowApply) {
        alert('Please complete the chat conversation first before applying.');
        return;
    }
    
    const applyBtn = document.getElementById('applyBtn');
    applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    applyBtn.disabled = true;
    
    fetch('/apply_scheme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            crop: 'detected',
            damage: 'detected'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessage('✅ Your application has been submitted successfully! The admin will review your application and update the status. You can check the status in your dashboard.', 'bot');
            document.getElementById('applySection').style.display = 'none';
            allowApply = false;
        } else {
            addMessage('❌ Failed to submit application. Please try again.', 'bot');
        }
        applyBtn.innerHTML = '<i class="fas fa-file-contract"></i> Apply for Scheme';
        applyBtn.disabled = false;
    })
    .catch(error => {
        addMessage('❌ Failed to submit application. Please try again.', 'bot');
        applyBtn.innerHTML = '<i class="fas fa-file-contract"></i> Apply for Scheme';
        applyBtn.disabled = false;
        console.error('Error:', error);
    });
}

function showChat() {
    // This function can be used to show chat section if needed
    const chatSection = document.getElementById('chatSection');
    if (chatSection) {
        chatSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.focus();
    }
});

// Handle Enter key in chat input
document.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && event.target.id === 'chatInput') {
        sendMessage();
    }
});

// Smooth scroll animation for messages
function smoothScrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        const scrollHeight = chatMessages.scrollHeight;
        const height = chatMessages.clientHeight;
        const maxScrollTop = scrollHeight - height;
        chatMessages.scrollTop = maxScrollTop > 0 ? maxScrollTop : 0;
    }
}

// Add some helpful suggestions when user starts typing
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('focus', function() {
            if (this.value === '') {
                this.placeholder = 'Try: "My wheat crops are damaged due to heavy rain"';
            }
        });
        
        chatInput.addEventListener('blur', function() {
            this.placeholder = 'Type your message here...';
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to send message
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const chatInput = document.getElementById('chatInput');
        if (chatInput && document.activeElement === chatInput) {
            sendMessage();
        }
    }
});

// Add message timestamp functionality
function addTimestamp(message) {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    return `${message} <small class="text-muted">(${time})</small>`;
}

// Enhanced message display with timestamps
function addMessageWithTimestamp(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message fade-in`;
    
    const alertClass = sender === 'user' ? 'alert-primary' : 'alert-info';
    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const alignment = sender === 'user' ? 'text-right' : 'text-left';
    
    const timestampedMessage = addTimestamp(message);
    
    messageDiv.innerHTML = `
        <div class="alert ${alertClass} ${alignment}" style="display: inline-block;">
            <i class="${icon}"></i> ${timestampedMessage}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    smoothScrollToBottom();
}

// Auto-resize chat input based on content
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    }
});

// Add typing animation for bot messages
function animateBotMessage(message, callback) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message fade-in';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info';
    alertDiv.style.display = 'inline-block';
    alertDiv.innerHTML = '<i class="fas fa-robot"></i> <span id="typing-text"></span>';
    
    messageDiv.appendChild(alertDiv);
    chatMessages.appendChild(messageDiv);
    
    const typingText = document.getElementById('typing-text');
    let index = 0;
    
    function typeChar() {
        if (index < message.length) {
            typingText.textContent += message[index];
            index++;
            smoothScrollToBottom();
            setTimeout(typeChar, 30);
        } else if (callback) {
            callback();
        }
    }
    
    typeChar();
}

// Export functions for global access
window.sendMessage = sendMessage;
window.applyForScheme = applyForScheme;
window.showChat = showChat;
