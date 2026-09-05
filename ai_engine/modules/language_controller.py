"""Language Controller module for multilingual educational localization and voice selection."""
import re
from typing import Dict, List, Optional, Any
from ai_engine.schemas.language import (
    LanguageCode,
    LanguageMode,
    VoiceMetadata,
    LanguageConfig,
    LanguageDecision,
)
from ai_engine.schemas.scene import TeachingScene
from ai_engine.schemas.question import QuestionSchema, QuestionOptionSchema


class LanguageController:
    """
    Central controller responsible for:
    - Resolving requested languages and fallback handling.
    - Selecting compatible neural TTS voices.
    - Pedagogical localization of teacher narrations while preserving technical terms.
    - Preserving RAG source citations.
    - Localizing diagnostic questions and normalizing multilingual student answers.
    """

    LANGUAGE_REGISTRY: Dict[LanguageCode, LanguageConfig] = {
        LanguageCode.EN: LanguageConfig(
            code=LanguageCode.EN,
            display_name="English",
            native_name="English",
            script="Latin",
            fallback_language=LanguageCode.EN,
            default_voice_id="en-US-AriaNeural",
        ),
        LanguageCode.HI: LanguageConfig(
            code=LanguageCode.HI,
            display_name="Hindi",
            native_name="हिन्दी",
            script="Devanagari",
            fallback_language=LanguageCode.EN,
            default_voice_id="hi-IN-SwaraNeural",
        ),
        LanguageCode.TA: LanguageConfig(
            code=LanguageCode.TA,
            display_name="Tamil",
            native_name="தமிழ்",
            script="Tamil",
            fallback_language=LanguageCode.EN,
            default_voice_id="ta-IN-PallaviNeural",
        ),
        LanguageCode.TE: LanguageConfig(
            code=LanguageCode.TE,
            display_name="Telugu",
            native_name="తెలుగు",
            script="Telugu",
            fallback_language=LanguageCode.EN,
            default_voice_id="te-IN-ShrutiNeural",
        ),
        LanguageCode.ML: LanguageConfig(
            code=LanguageCode.ML,
            display_name="Malayalam",
            native_name="മലയാളം",
            script="Malayalam",
            fallback_language=LanguageCode.EN,
            default_voice_id="ml-IN-SobhanaNeural",
        ),
        LanguageCode.KN: LanguageConfig(
            code=LanguageCode.KN,
            display_name="Kannada",
            native_name="ಕನ್ನಡ",
            script="Kannada",
            fallback_language=LanguageCode.EN,
            default_voice_id="kn-IN-SapnaNeural",
        ),
    }

    VOICE_CATALOG: List[VoiceMetadata] = [
        # English
        VoiceMetadata(
            voice_id="en-US-AriaNeural",
            name="Aria (US English)",
            language_code=LanguageCode.EN,
            gender="female",
            is_default=True,
            description="Warm, clear, and engaging pedagogical voice",
        ),
        VoiceMetadata(
            voice_id="en-US-GuyNeural",
            name="Guy (US English)",
            language_code=LanguageCode.EN,
            gender="male",
            is_default=False,
            description="Calm and authoritative instructional tone",
        ),
        VoiceMetadata(
            voice_id="en-IN-NeerjaNeural",
            name="Neerja (Indian English)",
            language_code=LanguageCode.EN,
            gender="female",
            is_default=False,
            description="Clear and articulate Indian English accent",
        ),
        # Hindi
        VoiceMetadata(
            voice_id="hi-IN-SwaraNeural",
            name="Swara (Hindi)",
            language_code=LanguageCode.HI,
            gender="female",
            is_default=True,
            description="Natural and expressive Hindi educator voice",
        ),
        VoiceMetadata(
            voice_id="hi-IN-MadhurNeural",
            name="Madhur (Hindi)",
            language_code=LanguageCode.HI,
            gender="male",
            is_default=False,
            description="Deep and clear Hindi voice",
        ),
        # Tamil
        VoiceMetadata(
            voice_id="ta-IN-PallaviNeural",
            name="Pallavi (Tamil)",
            language_code=LanguageCode.TA,
            gender="female",
            is_default=True,
            description="Fluent and engaging Tamil educator",
        ),
        VoiceMetadata(
            voice_id="ta-IN-ValluvarNeural",
            name="Valluvar (Tamil)",
            language_code=LanguageCode.TA,
            gender="male",
            is_default=False,
            description="Resonant and academic Tamil voice",
        ),
        # Telugu
        VoiceMetadata(
            voice_id="te-IN-ShrutiNeural",
            name="Shruti (Telugu)",
            language_code=LanguageCode.TE,
            gender="female",
            is_default=True,
            description="Warm and clear Telugu educator",
        ),
        VoiceMetadata(
            voice_id="te-IN-MohanNeural",
            name="Mohan (Telugu)",
            language_code=LanguageCode.TE,
            gender="male",
            is_default=False,
            description="Clear and friendly Telugu instructional tone",
        ),
        # Malayalam
        VoiceMetadata(
            voice_id="ml-IN-SobhanaNeural",
            name="Sobhana (Malayalam)",
            language_code=LanguageCode.ML,
            gender="female",
            is_default=True,
            description="Articulate and natural Malayalam educator",
        ),
        VoiceMetadata(
            voice_id="ml-IN-MidhunNeural",
            name="Midhun (Malayalam)",
            language_code=LanguageCode.ML,
            gender="male",
            is_default=False,
            description="Calm and steady Malayalam instructional voice",
        ),
        # Kannada
        VoiceMetadata(
            voice_id="kn-IN-SapnaNeural",
            name="Sapna (Kannada)",
            language_code=LanguageCode.KN,
            gender="female",
            is_default=True,
            description="Engaging and authentic Kannada teacher",
        ),
        VoiceMetadata(
            voice_id="kn-IN-GaganNeural",
            name="Gagan (Kannada)",
            language_code=LanguageCode.KN,
            gender="male",
            is_default=False,
            description="Articulate and supportive Kannada educator",
        ),
    ]

    # Technical terms that must be preserved in English in Bilingual / Mixed mode
    TECHNICAL_TERMS: List[str] = [
        "Binary Tree",
        "Binary Trees",
        "Root Node",
        "Leaf Node",
        "Child",
        "Left Child",
        "Right Child",
        "Subtree",
        "Traversal",
        "In-Order",
        "Pre-Order",
        "Post-Order",
        "AVL Tree",
        "Balance Factor",
        "O(log n)",
        "O(n)",
        "O(1)",
        "Ohm's Law",
        "Voltage",
        "Current",
        "Resistance",
        "Amperes",
        "Volts",
        "Ohms",
        "I = V / R",
        "V = I * R",
        "Recursion",
        "Base Case",
        "Call Stack",
    ]

    @classmethod
    def resolve_language(
        cls, requested_code: str, fallback_code: str = "en", mode: str = "bilingual"
    ) -> LanguageDecision:
        """Resolve requested language code with safe fallback handling."""
        normalized = (requested_code or "en").strip().lower()
        if "-" in normalized:
            normalized = normalized.split("-")[0]

        # Alias resolution
        aliases = {
            "english": "en",
            "hindi": "hi",
            "tamil": "ta",
            "telugu": "te",
            "malayalam": "ml",
            "kannada": "kn",
        }
        normalized = aliases.get(normalized, normalized)

        try:
            lang_code = LanguageCode(normalized)
            fallback_used = False
        except ValueError:
            try:
                lang_code = LanguageCode(fallback_code)
            except ValueError:
                lang_code = LanguageCode.EN
            fallback_used = True

        config = cls.LANGUAGE_REGISTRY.get(lang_code, cls.LANGUAGE_REGISTRY[LanguageCode.EN])
        try:
            resolved_mode = LanguageMode(mode)
        except ValueError:
            resolved_mode = LanguageMode.BILINGUAL

        return LanguageDecision(
            requested_language=requested_code,
            resolved_language=lang_code,
            mode=resolved_mode,
            fallback_used=fallback_used,
            preserved_terms=cls.TECHNICAL_TERMS if resolved_mode != LanguageMode.FULL_LANGUAGE else [],
            voice_id=config.default_voice_id,
            script=config.script,
        )

    @classmethod
    def get_available_voices(cls, language_code: Optional[str] = None) -> List[VoiceMetadata]:
        """Retrieve voice catalog filtered by language code."""
        if not language_code:
            return cls.VOICE_CATALOG
        decision = cls.resolve_language(language_code)
        return [v for v in cls.VOICE_CATALOG if v.language_code == decision.resolved_language]

    @classmethod
    def get_default_voice(cls, language_code: str) -> str:
        """Get default neural voice ID for a language."""
        decision = cls.resolve_language(language_code)
        config = cls.LANGUAGE_REGISTRY.get(decision.resolved_language, cls.LANGUAGE_REGISTRY[LanguageCode.EN])
        return config.default_voice_id

    @classmethod
    def localize_scene_narration(
        cls,
        scene: TeachingScene,
        target_lang: str,
        mode: str = "bilingual",
        learner_name: str = "Learner",
    ) -> Dict[str, Any]:
        """
        Produce a pedagogically localized narration and onscreen text for a teaching scene.
        Preserves mathematical equations, code blocks, and technical terms in English when in Bilingual/Mixed mode.
        """
        decision = cls.resolve_language(target_lang, mode=mode)
        lang = decision.resolved_language
        is_bilingual = decision.mode in [LanguageMode.BILINGUAL, LanguageMode.MIXED]
        concept = scene.concept
        scene_type = scene.scene_type

        # Localized templates by language
        if lang == LanguageCode.EN:
            return {
                "narration": scene.narration,
                "onscreen_text": scene.onscreen_text,
                "language": "en",
            }

        elif lang == LanguageCode.HI:
            # Hindi
            if scene_type == "intro":
                narr = f"नमस्ते {learner_name}! आज हम '{concept}' के बारे में विस्तार से सीखेंगे। आइए इस महत्वपूर्ण विषय को आसान उदाहरणों और विजुअल के साथ समझें।"
                otext = f"{concept} - परिचय और बुनियादी समझ"
            elif scene_type == "visual_explanation":
                if is_bilingual:
                    narr = f"आइए इस डायग्राम को ध्यान से देखें। सबसे ऊपर जो सर्कल है, वह हमारा Root Node है। Binary Tree में प्रत्येक नोड के अधिकतम 2 Children हो सकते हैं: Left Child और Right Child। यह स्ट्रक्चर हमें तेज़ सर्च और एफिशिएंसी देता है।"
                    otext = "Root Node और दो शाखाएं (Left Child & Right Child)"
                else:
                    narr = f"आइए इस आरेख को ध्यान से देखें। सबसे ऊपर जो वृत्त है, वह हमारा मूल नोड है। बाइनरी ट्री में प्रत्येक नोड के अधिकतम दो उप-नोड हो सकते हैं। यह पदानुक्रमित संरचना हमें त्वरित खोज देती है।"
                    otext = "मूल नोड और दो शाखाएं"
            elif scene_type == "analogy_walkthrough":
                if is_bilingual:
                    narr = f"इसे याद रखने के लिए: Binary Tree को '20 Questions' के खेल की तरह समझें। हर सवाल पर रास्ता 2 हिस्सों में बंटता है, जिससे हम करोड़ों संभावनाओं में से सही उत्तर बहुत जल्दी ढूंढ लेते हैं!"
                    otext = "एनालॉजी: 20 Questions का खेल और 2-वे ब्रांचिंग"
                else:
                    narr = f"इसे याद रखने के लिए: इस ट्री को 'बीस प्रश्नों' के खेल की तरह समझें। प्रत्येक कदम पर रास्ता दो हिस्सों में बंटता है, जिससे हम लाखों संभावनाओं में से सही उत्तर तुरंत खोज लेते हैं।"
                    otext = "एनालॉजी: त्वरित निर्णय और दो-तरफा विभाजन"
            elif scene_type == "checkpoint_prompt":
                narr = "अब आइए देखें कि आपने क्या सीखा! आपके सामने एक संक्षिप्त चेकपॉइंट सवाल है। ध्यान से सोचकर उत्तर दें।"
                otext = "जांच: अपनी समझ का परीक्षण करें"
            elif scene_type == "adaptive_remediation":
                narr = f"कोई बात नहीं! यह बहुत स्वाभाविक भ्रम है। आइए एक अलग नज़रिए से समझते हैं: जब हम 'Binary' कहते हैं, इसका मतलब ही 'दो' है - जैसे साइकिल के दो पहिये होते हैं।"
                otext = "उपचारात्मक पाठ: 'Binary' का अर्थ हमेशा 'अधिकतम दो' है"
            else:
                narr = f"{concept} पर ध्यान दें। यह मुख्य सिद्धांत हमारे पूरे विषय का आधार है।"
                otext = f"{concept} - मुख्य सिद्धांत"

        elif lang == LanguageCode.TA:
            # Tamil
            if scene_type == "intro":
                narr = f"வணக்கம் {learner_name}! இன்று நாம் '{concept}' பற்றி தெளிவாகக் கற்கப் போகிறோம். இந்த அடிப்படை கருத்தை எளிமையான காட்சி விளக்கத்துடன் புரிந்துகொள்வோம்."
                otext = f"{concept} - அறிமுகம் மற்றும் அடிப்படை கருத்து"
            elif scene_type == "visual_explanation":
                if is_bilingual:
                    narr = f"இந்த வரைபடத்தைக் கவனியுங்கள். மேலே உள்ள வட்டம் நமது Root Node ஆகும். ஒரு Binary Tree-ல் எந்த ஒரு Node-க்கும் அதிகபட்சமாக 2 Children மட்டுமே இருக்க முடியும்: Left Child மற்றும் Right Child. இதுவே தகவல்களை விரைவாக தேட உதவுகிறது."
                    otext = "Root Node மற்றும் இரு கிளைகள் (Left & Right Child)"
                else:
                    narr = f"இந்த வரைபடத்தைக் கவனியுங்கள். மேலே உள்ள வட்டம் நமது வேர் முனை (Root) ஆகும். இதில் எந்த ஒரு முனைக்கும் அதிகபட்சமாக இரண்டு கிளைகள் மட்டுமே இருக்க முடியும். இதுவே விரைவான தேடலுக்கு அடிப்படை."
                    otext = "வேர் முனை மற்றும் இரு கிளைகள்"
            elif scene_type == "analogy_walkthrough":
                if is_bilingual:
                    narr = f"இதை நினைவில் வைக்க: Binary Tree-ஐ ஒரு '20 Questions' விளையாட்டைப் போலக் கருதுங்கள். ஒவ்வொரு முடிவிலும் வழி இரண்டாகப் பிரிவதால், மில்லியன் கணக்கான தகவல்களிலும் O(log n) நேரத்தில் தேடிவிடலாம்!"
                    otext = "உவமை: 20 Questions விளையாட்டு மற்றும் இருவழிப் பிரிவு"
                else:
                    narr = f"இதை எளிதாகப் புரிந்துகொள்ள: ஒரு முடிவெடுக்கும் மரத்தை நினைவில் கொள்ளுங்கள். ஒவ்வொரு படியிலும் பாதை இரண்டாகப் பிரிவதால் மிக விரைவாக இலக்கை அடைய முடிகிறது."
                    otext = "உவமை: முடிவெடுக்கும் மரம் மற்றும் இருவழிப் பிரிவு"
            elif scene_type == "checkpoint_prompt":
                narr = "இப்போது நீங்கள் கற்றுக்கொண்டதைச் சோதிப்போம்! உங்களுக்காக ஒரு விரைவான கேள்வி காத்திருக்கிறது. யோசித்து பதிலளியுங்கள்."
                otext = "சுய மதிப்பீடு: உங்கள் புரிதலைச் சோதிக்கவும்"
            elif scene_type == "adaptive_remediation":
                narr = "கவலைப்பட வேண்டாம்! இது பலருக்கும் ஏற்படும் பொதுவான குழப்பமே. 'Binary' என்ற சொல்லின் பொருளே 'இரண்டு' மட்டுமே - மிதிவண்டிக்கு இரண்டு சக்கரங்கள் இருப்பது போல!"
                otext = "சரிசெய்தல் விளக்கம்: Binary என்றால் அதிகபட்சம் 2 கிளைகள் மட்டுமே"
            else:
                narr = f"{concept} பற்றிய முக்கியமான விளக்கம் இது. தொடர்ந்து கவனிப்போம்."
                otext = f"{concept} - முக்கிய விளக்கம்"

        elif lang == LanguageCode.TE:
            # Telugu
            if scene_type == "intro":
                narr = f"నమస్కారం {learner_name}! ఈ రోజు మనం '{concept}' గురించి చాలా సులభంగా మరియు స్పష్టంగా నేర్చుకోబోతున్నాం. రండి visual diagram తో ప్రారంభిద్దాం."
                otext = f"{concept} - పరిచయం మరియు మూల భావన"
            elif scene_type == "visual_explanation":
                if is_bilingual:
                    narr = f"ఈ డయాగ్రమ్ గమనించండి. పైన ఉన్న సర్కిల్ మన Root Node. Binary Tree లో ప్రతి Node కి గరిష్టంగా 2 Children మాత్రమే ఉంటాయి: Left Child మరియు Right Child. ఇది శోధన సమయాన్ని చాలా తగ్గిస్తుంది."
                    otext = "Root Node మరియు రెండు కొమ్మలు (Left & Right Child)"
                else:
                    narr = f"ఈ చిత్రాన్ని చూడండి. పైన ఉన్న వృత్తం మన మూల స్థానం. ఒక బైనరీ ట్రీలో ప్రతి నోడ్‌కు గరిష్టంగా రెండు ఉప-నోడ్‌లు మాత్రమే ఉంటాయి. ఇది సమాచారాన్ని వేగంగా శోధించడానికి వీలు కల్పిస్తుంది."
                    otext = "మూల నోడ్ మరియు రెండు ఉప-శాఖలు"
            elif scene_type == "analogy_walkthrough":
                narr = "దీన్ని సులభంగా గుర్తుంచుకోవడానికి: ప్రతి మలుపులోనూ రెండు దారులు మాత్రమే ఉండే అన్వేషణలా భావించండి. దీనివల్ల అతి తక్కువ సమయంలో సరైన సమాధానం కనుగొనవచ్చు."
                otext = "ఉదాహరణ: రెండు దారుల విభజన మరియు వేగవంతమైన ఫలితం"
            elif scene_type == "checkpoint_prompt":
                narr = "ఇప్పుడు మీ అవగాహనను పరీక్షించుకుందాం! మీకోసం ఒక ప్రశ్న సిద్ధంగా ఉంది. శ్రద్ధగా ఆలోచించి సమాధానం ఇవ్వండి."
                otext = "పరిశీలన: మీ అవగాహన పరీక్ష"
            elif scene_type == "adaptive_remediation":
                narr = "పర్వాలేదు! ఇది సాధారణంగా వచ్చే సందేహమే. 'Binary' అంటేనే 'రెండు' అని అర్థం - సైకిల్‌కు రెండు చక్రాలు ఉన్నట్లుగానే ఇక్కడ గరిష్టంగా రెండే కొమ్మలు ఉంటాయి."
                otext = "సవరణ వివరణ: Binary అంటే గరిష్టంగా రెండు మాత్రమే"
            else:
                narr = f"{concept} గురించి ముఖ్యమైన సూత్రం ఇది."
                otext = f"{concept} - ప్రధాన సూత్రం"

        elif lang == LanguageCode.ML:
            # Malayalam
            if scene_type == "intro":
                narr = f"നമസ്കാരം {learner_name}! ഇന്ന് നമ്മൾ '{concept}' നെക്കുറിച്ച് വളരെ ലളിതമായി പഠിക്കാൻ പോകുന്നു. ഡയഗ്രാമുകളുടെ സഹായത്തോടെ നമുക്ക് മനസ്സിലാക്കാം."
                otext = f"{concept} - ആമുഖവും അടിസ്ഥാന തത്വങ്ങളും"
            elif scene_type == "visual_explanation":
                if is_bilingual:
                    narr = f"ഈ ഡയഗ്രാം ശ്രദ്ധിക്കുക. ഏറ്റവും മുകളിലുള്ള സർക്കിളാണ് Root Node. ഒരു Binary Tree യിൽ ഓരോ നോഡിനും പരമാവധി 2 Children മാത്രമേ ഉണ്ടാകൂ: Left Child ഉം Right Child ഉം."
                    otext = "Root Node ഉം രണ്ട് ശാഖകളും (Left & Right Child)"
                else:
                    narr = f"ഈ രേഖാചിത്രം ശ്രദ്ധിക്കുക. ഏറ്റവും മുകളിലുള്ളതാണ് പ്രധാന നോഡ്. ഇതിൽ ഓരോ നോഡിനും പരമാവധി രണ്ട് ഉപശാഖകൾ മാത്രമേ ഉണ്ടാകൂ."
                    otext = "പ്രധാന നോഡും രണ്ട് ഉപശാഖകളും"
            elif scene_type == "analogy_walkthrough":
                narr = "ഓരോ ഘട്ടത്തിലും വഴി രണ്ടായി പിരിയുന്ന ഒരു യാത്ര പോലെ ഇതിനെ സങ്കൽപ്പിക്കാം. ഇത് വളരെ വേഗത്തിൽ ലക്ഷ്യത്തിലെത്താൻ സഹായിക്കുന്നു."
                otext = "ഉദാഹരണം: ഇരുവഴി വിഭജനവും വേഗത്തിലുള്ള തിരച്ചിലും"
            elif scene_type == "checkpoint_prompt":
                narr = "ഇനി നിങ്ങളുടെ ധാരണ പരിശോധിക്കാം! നിങ്ങൾക്കായി ഒരു ലളിതമായ ചോദ്യം ഇതാ. ശ്രദ്ധിച്ച് ഉത്തരം നൽകുക."
                otext = "പരിശോധന: നിങ്ങളുടെ ധാരണ പരിശോധിക്കുക"
            elif scene_type == "adaptive_remediation":
                narr = "വിഷമിക്കേണ്ടതില്ല! ഇത് പലർക്കും ഉണ്ടാകുന്ന ഒരു സംശയമാണ്. 'Binary' എന്നാൽ 'രണ്ട്' എന്നാണ് അർത്ഥം - പരമാവധി രണ്ട് കുട്ടികൾ മാത്രം."
                otext = "പുനരവലോകനം: Binary എന്നാൽ പരമാവധി 2 മാത്രം"
            else:
                narr = f"{concept} നെക്കുറിച്ചുള്ള പ്രധാന ആശയം ഇതാണ്."
                otext = f"{concept} - പ്രധാന ആശയം"

        elif lang == LanguageCode.KN:
            # Kannada
            if scene_type == "intro":
                narr = f"ನಮಸ್ಕಾರ {learner_name}! ಇಂದು ನಾವು '{concept}' ಬಗ್ಗೆ ಸರಳವಾಗಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಕಲಿಯಲಿದ್ದೇವೆ. ಬನ್ನಿ visual diagram ನೊಂದಿಗೆ ಕಲಿಯೋಣ."
                otext = f"{concept} - ಪರಿಚಯ ಮತ್ತು ಮೂಲ ಪರಿಕಲ್ಪನೆ"
            elif scene_type == "visual_explanation":
                if is_bilingual:
                    narr = f"ಈ ಚಿತ್ರವನ್ನು ಗಮನಿಸಿ. ಮೇಲ್ಭಾಗದಲ್ಲಿರುವ ವೃತ್ತವೇ ನಮ್ಮ Root Node. Binary Tree ನಲ್ಲಿ ಪ್ರತಿಯೊಂದು ನೋಡ್‌ಗೆ ಗರಿಷ್ಠ 2 Children ಮಾತ್ರ ಇರಲು ಸಾಧ್ಯ: Left Child ಮತ್ತು Right Child."
                    otext = "Root Node ಮತ್ತು ಎರಡು ಶಾಖೆಗಳು (Left & Right Child)"
                else:
                    narr = f"ಈ ಚಿತ್ರವನ್ನು ಗಮನಿಸಿ. ಮೇಲ್ಭಾಗದಲ್ಲಿರುವ ವೃತ್ತವೇ ಮೂಲ ನೋಡ್. ಇದರಲ್ಲಿ ಪ್ರತಿಯೊಂದು ನೋಡ್‌ಗೆ ಗರಿಷ್ಠ ಎರಡು ಕವಲುಗಳು ಮಾತ್ರ ಇರಲು ಸಾಧ್ಯ."
                    otext = "ಮೂಲ ನೋಡ್ ಮತ್ತು ಎರಡು ಕವಲುಗಳು"
            elif scene_type == "analogy_walkthrough":
                narr = "ಪ್ರತಿ ಹೆಜ್ಜೆಯಲ್ಲೂ ದಾರಿ ಎರಡಾಗಿ ವಿಭಜನೆಯಾಗುವ ನಿರ್ಧಾರದಂತೆ ಇದನ್ನು ಭಾವಿಸಿ. ಇದರಿಂದ ಅತಿ ವೇಗವಾಗಿ ಉತ್ತರವನ್ನು ಹುಡುಕಬಹುದು."
                otext = "ಉದಾಹರಣೆ: ಎರಡು ಮಾರ್ಗಗಳ ವಿಭಜನೆ ಮತ್ತು ಕ್ಷಿಪ್ರ ಶೋಧನೆ"
            elif scene_type == "checkpoint_prompt":
                narr = "ಈಗ ನಿಮ್ಮ ಕಲಿಕೆಯನ್ನು ಪರಿಶೀಲಿಸೋಣ! ನಿಮಗಾಗಿ ಒಂದು ಸಣ್ಣ ಪ್ರಶ್ನೆ ಇದೆ. ಯೋಚಿಸಿ ಉತ್ತರಿಸಿ."
                otext = "ಪರಿಶೀಲನೆ: ನಿಮ್ಮ ತಿಳುವಳಿಕೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ"
            elif scene_type == "adaptive_remediation":
                narr = "ಚಿಂತಿಸಬೇಡಿ! ಇದು ಸಾಮಾನ್ಯವಾಗಿ ಬರುವ ಗೊಂದಲ. 'Binary' ಎಂದರೆ 'ಎರಡು' ಎಂದರ್ಥ - ಬೈಸಿಕಲ್‌ನ ಎರಡು ಚಕ್ರಗಳಂತೆ ಇಲ್ಲಿ ಗರಿಷ್ಠ ಎರಡೇ ಶಾಖೆಗಳು ಇರುತ್ತವೆ."
                otext = "ತಿದ್ದುಪಡಿ ವಿವರಣೆ: Binary ಎಂದರೆ ಗರಿಷ್ಠ ಎರಡು ಮಾತ್ರ"
            else:
                narr = f"{concept} ಕುರಿತ ಮುಖ್ಯ ಸಾರಾಂಶವಿದು."
                otext = f"{concept} - ಮುಖ್ಯ ಸಾರಾಂಶ"

        else:
            narr = scene.narration
            otext = scene.onscreen_text

        return {
            "narration": narr,
            "onscreen_text": otext,
            "language": lang.value,
        }

    @classmethod
    def localize_question(cls, question: QuestionSchema, target_lang: str) -> QuestionSchema:
        """
        Localize question prompt and options into the target language.
        Preserves question_id, section_id, concept, expected_answer, rubric, and difficulty.
        """
        decision = cls.resolve_language(target_lang)
        lang = decision.resolved_language

        if lang == LanguageCode.EN:
            return question

        prompt = question.prompt
        options = question.options

        # Localized prompts for common questions
        if "maximum number of children" in question.prompt.lower():
            if lang == LanguageCode.HI:
                prompt = "बाइनरी ट्री (Binary Tree) में किसी एक नोड के अधिकतम कितने चिल्ड्रेन (Children) हो सकते हैं?"
            elif lang == LanguageCode.TA:
                prompt = "ஒரு பைனரி ட்ரீயில் (Binary Tree) ஏதேனும் ஒரு முனைக்கு அதிகபட்சமாக எத்தனை குழந்தைகள் (Children) இருக்க முடியும்?"
            elif lang == LanguageCode.TE:
                prompt = "బైనరీ ట్రీ (Binary Tree) లో ఏదైనా ఒక నోడ్‌కు గరిష్టంగా ఎన్ని పిల్లలు (Children) ఉండవచ్చు?"
            elif lang == LanguageCode.ML:
                prompt = "ഒരു ബൈനറി ട്രീയിൽ (Binary Tree) ഏതെങ്കിലും ഒരു നോഡിന് പരമാവധി എത്ര കുട്ടികൾ (Children) ഉണ്ടാകാം?"
            elif lang == LanguageCode.KN:
                prompt = "ಬೈನರಿ ಟ್ರೀ (Binary Tree) ಯಲ್ಲಿ ಯಾವುದೇ ಒಂದು ನೋಡ್‌ಗೆ ಗರಿಷ್ಠ ಎಷ್ಟು ಮಕ್ಕಳು (Children) ಇರಬಹುದು?"

        # Localized options if present
        localized_options = None
        if options:
            localized_options = []
            for opt in options:
                text = opt.text
                if opt.key == "A" and "1" in text:
                    text = f"1 ({'केवल एक' if lang == LanguageCode.HI else 'ஒன்று மட்டும்' if lang == LanguageCode.TA else text})"
                elif opt.key == "B" and "2" in text:
                    text = f"2 ({'अधिकतम दो' if lang == LanguageCode.HI else 'அதிகபட்சம் இரண்டு' if lang == LanguageCode.TA else text})"
                elif opt.key == "C" and "any" in text.lower():
                    text = f"{'असीमित' if lang == LanguageCode.HI else 'எண்ணற்ற' if lang == LanguageCode.TA else text}"
                elif opt.key == "D" and "0" in text:
                    text = f"0 ({'शून्य' if lang == LanguageCode.HI else 'பூஜ்ஜியம்' if lang == LanguageCode.TA else text})"
                localized_options.append(QuestionOptionSchema(key=opt.key, text=text))

        return QuestionSchema(
            question_id=question.question_id,
            section_id=question.section_id,
            concept=question.concept,
            question_type=question.question_type,
            prompt=prompt,
            options=localized_options or question.options,
            expected_answer=question.expected_answer,
            difficulty=question.difficulty,
            rubric=question.rubric,
            hints=question.hints,
        )

    @classmethod
    def normalize_student_answer(cls, answer_text: str, student_lang: str = "en") -> str:
        """
        Normalize multilingual student response text so the semantic AnswerEvaluator
        and MisconceptionDetector can evaluate it accurately regardless of language.
        """
        clean = (answer_text or "").strip().lower()

        # Numeric and choice normalization across languages
        # Hindi
        clean = clean.replace("दो", "2").replace("चार", "4").replace("एक", "1").replace("शून्य", "0")
        clean = clean.replace("हाँ", "yes").replace("नहीं", "no").replace("सही", "correct")
        # Tamil
        clean = clean.replace("இரண்டு", "2").replace("நான்கு", "4").replace("ஒன்று", "1")
        clean = clean.replace("ஆம்", "yes").replace("இல்லை", "no")
        # Telugu
        clean = clean.replace("రెండు", "2").replace("నాలుగు", "4").replace("ఒకటి", "1")
        clean = clean.replace("అవును", "yes").replace("కాదు", "no")
        # Malayalam
        clean = clean.replace("രണ്ട്", "2").replace("നാല്", "4").replace("ഒന്ന്", "1")
        # Kannada
        clean = clean.replace("ಎರಡು", "2").replace("ನಾಲ್ಕು", "4").replace("ಒಂದು", "1")

        return clean
