# Kannada AI Chatbot

This chatbot built with **FastAPI**. The chatbot provides real-time text-based and voice-based interactions, supporting both **English** and **Kannada**. It leverages state-of-the-art machine learning models such as **Llama3-8b-8192** (via **ChatGroq**) for generating concise and relevant responses.

---

## Features

- **Multilingual Support**: 
  - Users can chat in **English** or **Kannada**.
  - Kannada messages are translated to English for processing and then translated back to Kannada for responses.

- **Text-to-Speech (TTS)**:
  - Converts chatbot responses into audio in either **English** or **Kannada** using **gTTS**.

- **Speech-Recongition**:
  - Transcribe the speech into text for both **English** or **Kannada** languages using WebkitSpeechRecognition library. 

- **WebSocket Support**:
  - Enables real-time communication for dynamic use cases.

---

## Prerequisites

1. **Python 3.10.2 or above**
2. **Environment Variables**:
   - `GROQ_API_KEY`: API key for **ChatGroq**.
   - `HUGGINGFACEHUB_API_TOKEN`: Access token for **Hugging Face**.
---

## Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/SaiKumarSeela/KannadaChatbot.git
cd KannadaChatbot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
git clone https://github.com/VarunGumma/IndicTransToolkit.git
cd IndicTransToolkit
pip install --editable ./
cd ..
python -c "import nltk; nltk.download('punkt')"
```


### Step 3: Configure Environment Variables

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token
```

### Step 4: Run the Application

```bash
uvicorn main:app --reload
```

### Step 5: Access the Application

Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)





