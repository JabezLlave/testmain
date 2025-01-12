from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from googletrans import Translator
import speech_recognition as sr
import os
import logging
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure temp directory exists
os.makedirs('temp', exist_ok=True)

LANGUAGE_OPTIONS = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar", "Armenian": "hy", "Azerbaijani": "az",
    "Basque": "eu", "Belarusian": "be", "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chichewa": "ny", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW", "Corsican": "co",
    "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en", "Esperanto": "eo", "Estonian": "et",
    "Filipino": "tl", "Finnish": "fi", "French": "fr", "Frisian": "fy", "Galician": "gl", "Georgian": "ka", "German": "de",
    "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw", "Hebrew": "he", "Hindi": "hi",
    "Hmong": "hmn", "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig", "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jw", "Kannada": "kn", "Kazakh": "kk", "Khmer": "km", "Korean": "ko", "Kurdish (Kurmanji)": "ku",
    "Kyrgyz": "ky", "Lao": "lo", "Latin": "la", "Latvian": "lv", "Lithuanian": "lt", "Luxembourgish": "lb", "Macedonian": "mk",
    "Malagasy": "mg", "Malay": "ms", "Malayalam": "ml", "Maltese": "mt", "Maori": "mi", "Marathi": "mr", "Mongolian": "mn",
    "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no", "Nyanja": "ny", "Odia": "or", "Pashto": "ps", "Persian": "fa",
    "Polish": "pl", "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Samoan": "sm", "Scots Gaelic": "gd",
    "Serbian": "sr", "Sesotho": "st", "Shona": "sn", "Sindhi": "sd", "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl",
    "Somali": "so", "Spanish": "es", "Sundanese": "su", "Swahili": "sw", "Swedish": "sv", "Tajik": "tg", "Tamil": "ta",
    "Tatar": "tt", "Telugu": "te", "Thai": "th", "Turkish": "tr", "Turkmen": "tk", "Ukrainian": "uk", "Urdu": "ur",
    "Uyghur": "ug", "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}

CULTURAL_RESPONSES = {
    "fr": [
        "In France, meals are a social event that can last several hours.",
        "French people typically greet with 'la bise' - a kiss on each cheek.",
        "The French take their bread very seriously - there are laws about baking baguettes!"
    ],
    "es": [
        "In Spain, dinner is typically eaten between 9-11 PM.",
        "The siesta is an important cultural tradition in Spain.",
        "Tapas are small portions of food often shared among friends."
    ],
    "zh-CN": [ 
        "Red is considered a lucky color in Chinese culture.",
        "The number 8 is considered lucky in Chinese culture.",
        "Chinese New Year celebrations last for 15 days."
    ]
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.json
        text = data.get('text')
        target_language = data.get('language')
        
        if not text or not target_language:
            return jsonify({'error': 'Missing text or target language'}), 400
        
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        
        cultural_context = None
        if target_language in CULTURAL_RESPONSES:
            cultural_context = random.choice(CULTURAL_RESPONSES[target_language])
        
        return jsonify({
            'translation': translated.text,
            'cultural_context': cultural_context
        })
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'error': 'Translation service unavailable'}), 500

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    try:
        temp_path = os.path.join('temp', f'temp_audio_{random.randint(1000, 9999)}.wav')
        audio_file.save(temp_path)

        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return jsonify({'text': text})
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        return jsonify({'error': 'Speech recognition failed'}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")

@app.route('/image-to-text', methods=['POST'])
def image_to_text():
    return jsonify({
        'text': 'Image to text feature is currently under maintenance. Please try again later.',
        'status': 'maintenance'
    }), 503

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message', '').lower()
        
        if any(word in message for word in ["hello", "hi", "hey"]):
            response = "Hello! I can help you learn about different cultures. Which culture interests you?"

        if any(word in message for word in ["who is Jabez Llave", "Jabez ", "Jabez Llave", "jabez", "who is jabez llave"]):
            response = "The developer of this site is Jabez Llave, a grade 12 STEM Student who want to improve the social media world."    

        elif any(lang.lower() in message for lang in LANGUAGE_OPTIONS.keys()):
            for lang, code in LANGUAGE_OPTIONS.items():
                if lang.lower() in message and code in CULTURAL_RESPONSES:
                    response = random.choice(CULTURAL_RESPONSES[code])
                    break
            else:
                response = "I'd be happy to tell you about that culture. What would you like to know?"
        
        else:
            response = "I'm your AI cultural assistant. Feel free to ask about any culture or language!"
            
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Chat service unavailable'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)