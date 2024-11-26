import streamlit as st
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

# Set page config
st.set_page_config(page_title="Language Translator", layout="wide")

# Initialize session state for models and tokenizers
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False

def load_models():
    """Load both translation models and tokenizers"""
    
    DEVICE = "cpu"  # Since we're using CPU only
    
    # Load English to Indic model
    en_indic_ckpt_dir = "ai4bharat/indictrans2-en-indic-dist-200M" # "ai4bharat/indictrans2-en-indic-1B"
    en_indic_tokenizer = AutoTokenizer.from_pretrained(en_indic_ckpt_dir, trust_remote_code=True)
    en_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
        en_indic_ckpt_dir,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    ).to(DEVICE)
    en_indic_model.eval()
    
    # Load Indic to English model
    indic_en_ckpt_dir = "ai4bharat/indictrans2-indic-en-dist-200M" #"ai4bharat/indictrans2-indic-en-1B"
    indic_en_tokenizer = AutoTokenizer.from_pretrained(indic_en_ckpt_dir, trust_remote_code=True)
    indic_en_model = AutoModelForSeq2SeqLM.from_pretrained(
        indic_en_ckpt_dir,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    ).to(DEVICE)
    indic_en_model.eval()
    
    return (en_indic_model, en_indic_tokenizer, indic_en_model, indic_en_tokenizer)

def translate_text(text, src_lang, tgt_lang, model, tokenizer):
    """Translate a single text input"""
    DEVICE = "cpu"
    ip = IndicProcessor(inference=True)
    
    # Preprocess the input
    preprocessed_text = ip.preprocess_batch([text], src_lang=src_lang, tgt_lang=tgt_lang)
    
    # Tokenize
    inputs = tokenizer(
        preprocessed_text,
        truncation=True,
        padding="longest",
        return_tensors="pt",
        return_attention_mask=True,
    ).to(DEVICE)
    
    # Generate translation
    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            use_cache=True,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1,
        )
    
    # Decode the generated tokens
    with tokenizer.as_target_tokenizer():
        translated_text = tokenizer.batch_decode(
            generated_tokens.detach().cpu().tolist(),
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
    
    # Postprocess the translation
    final_translation = ip.postprocess_batch(translated_text, lang=tgt_lang)
    
    return final_translation[0]

def main():
    st.title("English ⟷ ಕನ್ನಡ Translator")
    
    # Load models on first run
    if not st.session_state.models_loaded:
        with st.spinner("Loading translation models... This may take a few minutes..."):
            try:
                models = load_models()
                st.session_state.en_indic_model = models[0]
                st.session_state.en_indic_tokenizer = models[1]
                st.session_state.indic_en_model = models[2]
                st.session_state.indic_en_tokenizer = models[3]
                st.session_state.models_loaded = True
                st.success("Models loaded successfully!")
            except Exception as e:
                st.error(f"Error loading models: {str(e)}")
                return
    
    # Create two columns for input and output
    col1, col2 = st.columns(2)
    
    with col1:
        # Source language selection
        src_language = st.selectbox(
            "Select Input Language",
            ["English", "Kannada"],
            key="src_lang"
        )
        
        # Text input
        input_text = st.text_area(
            "Enter text to translate",
            height=200,
            key="input_text"
        )
    
    with col2:
        # Target language will be opposite of source language
        tgt_language = "Kannada" if src_language == "English" else "English"
        st.write(f"Translation ({tgt_language})")
        
        # Create a placeholder for the translation
        translation_placeholder = st.empty()
    
    # Translate button
    if st.button("Translate"):
        if input_text.strip() == "":
            st.warning("Please enter some text to translate.")
            return
        
        try:
            with st.spinner("Translating..."):
                if src_language == "English":
                    # English to Kannada
                    translation = translate_text(
                        input_text,
                        "eng_Latn",
                        "kan_Knda",
                        st.session_state.en_indic_model,
                        st.session_state.en_indic_tokenizer
                    )
                else:
                    # Kannada to English
                    translation = translate_text(
                        input_text,
                        "kan_Knda",
                        "eng_Latn",
                        st.session_state.indic_en_model,
                        st.session_state.indic_en_tokenizer
                    )
                
                # Display translation in the placeholder
                translation_placeholder.text_area(
                    "Translation",
                    value=translation,
                    height=200,
                    key="output_text"
                )
        
        except Exception as e:
            st.error(f"Translation error: {str(e)}")

if __name__ == "__main__":
    main()