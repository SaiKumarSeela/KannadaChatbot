// static/js/chat.js
class ChatBot {
    constructor() {
        this.language = null;
        this.recognition = null;
        this.isListening = false;
        this.initialize();
    }

    initialize() {
        // DOM elements
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.micButton = document.getElementById('micButton');
        this.chatMessages = document.getElementById('chatMessages');

        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.micButton.addEventListener('click', () => this.toggleSpeechRecognition());

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window) {
            this.initializeSpeechRecognition();
        }

        // Start with language selection
        this.showLanguageSelection();
    }

    showLanguageSelection() {

        this.addMessage("Hi! Please select a language:\n1. English\n2. Kannada. \nTo change the language type 'change language'", 'bot');
        const message4 = "Hi Please select a language 1. English 2. Kannada.To change the language type change language"
        this.playAudio(message4, "english")
    }

    initializeSpeechRecognition() {
        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.sendMessage();
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopListening();
        };

        this.recognition.onend = () => {
            this.stopListening();
        };
    }

    toggleSpeechRecognition() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        this.recognition.lang = this.language === 'english' ? 'en-IN' : 'kn-IN';
        this.recognition.start();
        this.isListening = true;
        this.micButton.classList.add('active');
    }

    stopListening() {
        this.recognition.stop();
        this.isListening = false;
        this.micButton.classList.remove('active');
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        // Add user message to chat

        this.addMessage(message, 'user');

        // Clear input
        this.messageInput.value = '';

        // Handle language selection
        if (!this.language) {
            this.handleLanguageSelection(message);
            return;
        }

        // Handle language change request
        if (message.toLowerCase() === 'change language') {
            this.language = null;
            this.showLanguageSelection();
            return;
        }



        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await this.sendToServer(message);
            this.hideTypingIndicator();
            this.playAudio(response.response, this.language)
            this.addMessage(response.response, 'bot');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, there was an error processing your message.', 'bot');
            console.error('Error:', error);
        }
    }

    handleLanguageSelection(message) {
        const selection = message.trim();
        if (selection === '1') {
            this.language = 'english';
            const message3 = 'You selected English. How can I help you?'
            this.playAudio(message3, this.language)
            this.addMessage(message3, 'bot');
        } else if (selection === '2') {
            this.language = 'kannada';
            const message2 = 'ನೀವು ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಿ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?'
            this.playAudio(message2, this.language);
            this.addMessage(message2, 'bot');
        } else {
            const message = 'Please select 1 for English or 2 for Kannada.'
            this.playAudio(message, 'english');
            this.addMessage(message, 'bot');
        }
    }

    async sendToServer(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: this.language,
                input_type: this.isListening ? 'voice' : 'text'
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response.json();
    }



    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        document.querySelector('.typing-indicator').style.display = 'block';
    }

    hideTypingIndicator() {
            document.querySelector('.typing-indicator').style.display = 'none';
        }
        // Play audio
    async playAudio(text, lang) {
        try {
            console.log(lang)
            console.log(text)
            const response = await fetch("/text-to-speech", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text, language: lang }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
            audio.play();
        } catch (error) {
            console.error("Error playing audio:", error);
            alert("Error playing audio. Please try again.");
        }
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});