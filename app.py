import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class MultilingualChatApp:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="Llama3-8b-8192",
            max_tokens=3000,
            temperature=0.2
        )

    def get_system_prompt(self, language):
        language = language.lower()
        system_prompts = {
            "english": "You are an AI assistant that helps users by answering their queries and the response should be concise in English.",
            "kannada": "You are an AI assistant that helps users by answering their queries and the response should be concise in Kannada. Give the response in Kannada only."
        }
        return system_prompts.get(language, system_prompts["english"])

    def call_groq_api(self, message, language):
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt(language)),
            ("human", "{query}")
        ])
        formatted_prompt = prompt.format(query=message)
        response = self.llm.predict(formatted_prompt)
        return response

    def load_conversation(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_conversation(self, filename, conversation):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=4, ensure_ascii=False)

    

    def run(self):
        st.set_page_config(page_title="Kannada ChatBot", layout="wide")

        # Initialize session state variables
        if 'conversation_file' not in st.session_state:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.makedirs("result", exist_ok=True)
            st.session_state.conversation_file = f'result/conversation_history_{timestamp}.json'

        if 'conversation' not in st.session_state:
            st.session_state.conversation = self.load_conversation(st.session_state.conversation_file)

        if 'editing_index' not in st.session_state:
            st.session_state.editing_index = None

        with st.container():
            st.title("Bilingual Kannada ChatBot")

        if st.session_state.conversation:
            json_data = json.dumps(st.session_state.conversation, ensure_ascii=False,indent=4)
            st.download_button(
                label="Download Conversation as JSON",
                data=json_data,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        # Display conversation
        for idx, entry in enumerate(st.session_state.conversation):
            col1, col2 = st.columns([2, 2])

            with col1:
                if entry.get('human'):
                    st.markdown(f"**User:** {entry['human']}")
            
            with col2:
            
                if st.session_state.editing_index == idx:
                    
                    new_response = st.text_area(
                        "Edit Assistant Response", 
                        value=entry['assistant'], 
                        key=f"edit_response_{idx}"
                    )
                    
                    save_col, cancel_col = st.columns(2)
                    with save_col:
                        if st.button("Save Changes", key=f"save_{idx}"):
                            # Update the conversation in session state
                            st.session_state.conversation[idx]['assistant'] = new_response
                            st.session_state.conversation[idx]['assistant_timestamp'] = datetime.now().isoformat()
                            
                            # Save to file
                            self.save_conversation(st.session_state.conversation_file, st.session_state.conversation)
                            
                            st.session_state.editing_index = None
                            st.rerun()
                    
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_{idx}"):
                           
                            st.session_state.editing_index = None
                            st.rerun()
                else:
            
                    if entry.get('assistant'):
                        st.markdown(f"**Assistant:** {entry['assistant']}")
                        if st.button("Edit", key=f"edit_{idx}"):
                           
                            st.session_state.editing_index = idx
                            st.rerun()

        with st.container():
            st.markdown("---")
            bottom_col1, bottom_col2, bottom_col3 = st.columns([2, 6, 1])

            with bottom_col1:
                language = st.selectbox("Language", ["English", "Kannada"], key="language")

            with bottom_col2:
               
                if 'user_input' not in st.session_state:
                    st.session_state.user_input = ""

                user_message = st.text_input(
                    "Type your message here...", 
                    value=st.session_state.user_input,
                    key="message_input"
                )

            with bottom_col3:
                st.markdown("\n")
                st.markdown("\n")
                if st.button("➤") and user_message.strip():
                    human_timestamp = datetime.now().isoformat()
                    assistant_response = self.call_groq_api(user_message, language)
                    assistant_timestamp = datetime.now().isoformat()

                    # Append to conversation
                    st.session_state.conversation.append({
                        "human": user_message,
                        "human_timestamp": human_timestamp,
                        "assistant": assistant_response,
                        "assistant_timestamp": assistant_timestamp,
                        "language": language
                    })

                    # Save to file
                    self.save_conversation(st.session_state.conversation_file, st.session_state.conversation)
                    st.session_state.user_input = ""

                    st.rerun()

if __name__ == "__main__":
    app = MultilingualChatApp()
    app.run()