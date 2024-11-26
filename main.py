from fastapi import FastAPI, HTTPException, WebSocket,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
from gtts import gTTS
import base64
import os
import io
from transformers import pipeline
from dotenv import load_dotenv
from src.translator import load_models, translate_text
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI()


groq_api_key = os.getenv('GROQ_API_KEY')
access_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant that helps users by answering their queries and the response should be concise."),
    ("human", """{query}""")
])

llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="Llama3-8b-8192",
        max_tokens=3000,
        temperature=0.2
    )
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Models for request/response
class ChatRequest(BaseModel):
    message: str
    language: str
    input_type: str  # 'text' or 'voice'

class SpeechRequest(BaseModel):
    text: str
    language: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/text-to-speech")
async def text_to_speech(request: SpeechRequest ):
    try:
        print(request)
        speech_lang = ''
        # Convert text to speech
        speech_lang = 'en' if request.language.lower() == 'english' else 'kn'
        tts = gTTS(text=request.text, lang= speech_lang)
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        # Convert to base64
        audio_data = base64.b64encode(audio_io.read()).decode()
        
        return JSONResponse(content={"audio_data": audio_data})
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
       
        if request.language == "english":
            # Send to LLM directly
            llm_response = await call_groq_api(request.message)
            # Translate LLM response to Kannada
            
            return {"response": llm_response}
        else:  # Kannada
            # Translate Kannada to English
            print(request.language)
            model = load_models(language_type= request.language)
            #request.message
            print(f"Message: {request.message}")
            translated_input =  translate_text(
                        request.message,
                        "kan_Knda",
                        "eng_Latn",
                       model[0],
                        model[1]
                    )
            print(f"tranlated_input:{translated_input} ")
            # Send to LLM
            llm_response = await call_groq_api(translated_input)
            model2 = load_models(language_type= "english")

            translated_response = translate_text(
                        llm_response,
                        "eng_Latn",
                        "kan_Knda",
                        model2[0],
                        model2[1]
                    )

            return {"response": translated_response}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def call_groq_api(message: str):
    formatted_prompt = prompt.format(query=message)
    response = llm.predict(formatted_prompt)
    return response
   

# WebSocket for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process websocket messages here
            response = await process_websocket_message(data)
            await websocket.send_text(response)
    except Exception as e:
        await websocket.close()

async def process_websocket_message(message: str):
    # Add websocket message processing logic here
    return "Processed message"