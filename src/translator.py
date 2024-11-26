import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor

def load_models(language_type):
    """Load both translation models and tokenizers"""
    
    DEVICE = "cpu"  # Since we're using CPU only
    if language_type == "english":
        # Load English to Indic model
        en_indic_ckpt_dir = "ai4bharat/indictrans2-en-indic-dist-200M" # "ai4bharat/indictrans2-en-indic-1B"
        en_indic_tokenizer = AutoTokenizer.from_pretrained(en_indic_ckpt_dir, trust_remote_code=True)
        en_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
            en_indic_ckpt_dir,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        ).to(DEVICE)
        en_indic_model.eval()
        return (en_indic_model, en_indic_tokenizer)
    else: 
        # Load Indic to English model
        indic_en_ckpt_dir = "ai4bharat/indictrans2-indic-en-dist-200M" #"ai4bharat/indictrans2-indic-en-1B"
        indic_en_tokenizer = AutoTokenizer.from_pretrained(indic_en_ckpt_dir, trust_remote_code=True)
        indic_en_model = AutoModelForSeq2SeqLM.from_pretrained(
            indic_en_ckpt_dir,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        ).to(DEVICE)
        indic_en_model.eval()
        return (indic_en_model, indic_en_tokenizer)

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
