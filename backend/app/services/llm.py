import json
from collections.abc import AsyncGenerator

from httpx import AsyncClient, HTTPStatusError, RequestError

from app.core.config import get_settings

SYSTEM_PROMPT_EN = """You are AgroGuard, an expert AI agricultural assistant for Myanmar (Burma).
Provide helpful, accurate, and concise advice about:
- Crop selection and farming best practices for Myanmar's climate zones
- Plant disease identification and treatment
- Soil management and irrigation
- Weather impact on agriculture
- NDVI and satellite vegetation analysis

Keep responses EXTREMELY brief, practical, and actionable (maximum 2-3 short sentences).
Answer in English."""

SYSTEM_PROMPT_MY = """သင်သည် မြန်မာနိုင်ငံအတွက် စိုက်ပျိုးရေးဆိုင်ရာ ကျွမ်းကျင် AI အကူအညီပေးသူ AgroGuard ဖြစ်ပါသည်။
အောက်ပါကိစ္စများအတွက် အထောက်အကူဖြစ်စေမည့် တိကျမှန်ကန်ပြီး လက်တွေ့ကျသော အကြံဉာဏ်များကို ပေးပါ-
- မြန်မာနိုင်ငံ၏ ရာသီဥတုဇုန်များအတွက် သီးနှံရွေးချယ်မှုနှင့် စိုက်ပျိုးရေးအကောင်းဆုံးနည်းလမ်းများ
- အပင်ရောဂါရှာဖွေခြင်းနှင့် ကုသခြင်း
- မြေဆီလွှာစီမံခန့်ခွဲမှုနှင့် ဆည်မြောင်း
- စိုက်ပျိုးရေးအပေါ် ရာသီဥတုသက်ရောက်မှု
- NDVI နှင့် ဂြိုဟ်တုအပင်ကျန်းမာရေးခွဲခြမ်းစိတ်ဖြာခြင်း

မြန်မာလယ်သမားများအတွက် လက်တွေ့ကျပြီး အသုံးဝင်သော အကြံဉာဏ်များကို မြန်မာဘာသာဖြင့် အလွန်တိုတောင်းစွာ (ဝါကျ ၂ ကြောင်း သို့မဟုတ် ၃ ကြောင်းသာ) ဖြေကြားပါ။"""

CROP_EXPLANATION_PROMPT_EN = (
    "You are an expert agricultural advisor for Myanmar.\n"
    "Given soil and weather conditions, explain why {crop} is suitable.\n"
    "Include information about:\n"
    "- Why {crop} thrives in soil pH {soil_pH}, rainfall {rainfall_mm}mm, "
    "and temperature {temperature_c}°C\n"
    "- Expected yield potential\n"
    "- Any specific cultivation tips for Myanmar farmers\n"
    "- Market considerations\n\n"
    "Keep the explanation concise (2-3 paragraphs) and practical. Answer in English."
)

CROP_EXPLANATION_PROMPT_MY = (
    "သင်သည် မြန်မာနိုင်ငံအတွက် စိုက်ပျိုးရေးကျွမ်းကျင်အကြံပေးတစ်ဦးဖြစ်ပါသည်။\n"
    "အောက်ပါမြေဆီလွှာနှင့် ရာသီဥတုအခြေအနေများအရ {crop} သည် "
    "အဘယ်ကြောင့် စိုက်ပျိုးရန် သင့်တော်သော သီးနှံဖြစ်သည်ကို ရှင်းပြပါ-\n"
    "- မြေဆီလွှာ pH {soil_pH}၊ မိုးရေချိန် {rainfall_mm}မီလီမီတာ "
    "နှင့် အပူချိန် {temperature_c}°C တွင် {crop} သည် "
    "အဘယ်ကြောင့်ဖြစ်ထွန်းသနည်း\n"
    "- မျှော်မှန်းအထွက်နှုန်း\n"
    "- မြန်မာလယ်သမားများအတွက် စိုက်ပျိုးနည်းဆိုင်ရာ အကြံပြုချက်များ\n"
    "- ဈေးကွက်အခြေအနေ\n\n"
    "ကျစ်လစ်ပြီး လက်တွေ့ကျသော အကြံဉာဏ်များကို "
    "မြန်မာဘာသာဖြင့် ရှင်းပြပါ။"
)

DISEASE_ADVICE_PROMPT_EN = (
    "You are an expert agricultural advisor for Myanmar.\n"
    "A plant disease model has identified {disease} on a {plant} leaf.\n"
    "Provide advice in JSON format EXACTLY matching this structure:\n"
    "{{\n"
    '  "visibleSymptoms": ["symptom 1", "symptom 2"],\n'
    '  "possibleCauses": ["cause 1", "cause 2"],\n'
    '  "treatmentRecommendations": ["treatment 1", "treatment 2"],\n'
    '  "preventionRecommendations": ["prevention 1", "prevention 2"]\n'
    "}}\n\n"
    "Keep each item concise and practical for Myanmar farmers. Output ONLY valid JSON."
)

DISEASE_ADVICE_PROMPT_MY = (
    "သင်သည် မြန်မာနိုင်ငံအတွက် စိုက်ပျိုးရေးကျွမ်းကျင်အကြံပေးတစ်ဦးဖြစ်ပါသည်။\n"
    "အပင်ရောဂါရှာဖွေရေး မော်ဒယ်သည် {plant} အရွက်ပေါ်တွင် {disease} ရောဂါကို တွေ့ရှိထားပါသည်။\n"
    "အောက်ပါ JSON ပုံစံအတိုင်း အတိအကျ အကြံဉာဏ်ပေးပါ-\n"
    "{{\n"
    '  "visibleSymptoms": ["ရောဂါလက္ခဏာ ၁", "ရောဂါလက္ခဏာ ၂"],\n'
    '  "possibleCauses": ["ဖြစ်နိုင်သော အကြောင်းရင်း ၁", "ဖြစ်နိုင်သော အကြောင်းရင်း ၂"],\n'
    '  "treatmentRecommendations": ["ကုသမှုနည်းလမ်း ၁", "ကုသမှုနည်းလမ်း ၂"],\n'
    '  "preventionRecommendations": ["ကာကွယ်ရေးနည်းလမ်း ၁", "ကာကွယ်ရေးနည်းလမ်း ၂"]\n'
    "}}\n\n"
    "အချက်တစ်ခုစီကို မြန်မာလယ်သမားများအတွက် လက်တွေ့ကျပြီး တိုတောင်းစွာရေးပါ။ JSON သီးသန့်သာ ထုတ်ပေးပါ။"
)


def _llm_headers() -> dict[str, str]:
    settings = get_settings()
    api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _llm_url() -> str:
    settings = get_settings()
    return f"{settings.llm_endpoint.rstrip('/')}/chat/completions"


async def _stream_sse(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    settings = get_settings()
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": True,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with AsyncClient(timeout=60) as client:
        try:
            async with client.stream("POST", _llm_url(), json=payload, headers=_llm_headers()) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            return
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except (HTTPStatusError, RequestError) as e:
            yield f"\n\n_Error communicating with LLM: {e}_"


def _build_messages(messages: list[dict], language: str) -> list[dict]:
    system_prompt = SYSTEM_PROMPT_MY if language == "my" else SYSTEM_PROMPT_EN
    return [{"role": "system", "content": system_prompt}, *messages]


def _lang_prompt(language: str, en: str, my: str) -> str:
    return my if language == "my" else en


async def stream_chat(
    messages: list[dict],
    language: str,
) -> AsyncGenerator[str, None]:
    async for chunk in _stream_sse(_build_messages(messages, language), temperature=0.5, max_tokens=512):
        yield chunk


def _fallback_chat_response(messages: list[dict], language: str) -> str:
    user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    if language == "my":
        return f"ကျေးဇူးပြု၍ AgroGuard API ကို အသုံးပြုရန်အတွက် LLM API သော့ကို သတ်မှတ်ပါ။\n\nမေးခွန်း- {user_msg}"
    return (
        f"AgroGuard requires an LLM API key to function. "
        f"Please set the `AGROGUARD_LLM_API_KEY` environment variable.\n\n"
        f"Your question was: {user_msg}"
    )


async def stream_crop_explanation(
    soil_pH: float,
    rainfall_mm: float,
    temperature_c: float,
    crop: str,
    language: str,
) -> AsyncGenerator[str, None]:
    prompt_template = CROP_EXPLANATION_PROMPT_MY if language == "my" else CROP_EXPLANATION_PROMPT_EN
    user_prompt = prompt_template.format(
        crop=crop,
        soil_pH=soil_pH,
        rainfall_mm=rainfall_mm,
        temperature_c=temperature_c,
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_MY if language == "my" else SYSTEM_PROMPT_EN},
        {"role": "user", "content": user_prompt},
    ]
    async for chunk in _stream_sse(messages, temperature=0.7, max_tokens=1024):
        yield chunk


def _fallback_crop_explanation(crop: str, language: str) -> str:
    if language == "my":
        return (
            f"{crop} သည် မြန်မာနိုင်ငံ၏ ရာသီဥတုအခြေအနေများအတွက် သင့်လျော်သော သီးနှံတစ်မျိုးဖြစ်ပါသည်။ "
            f"အသေးစိတ်ရှင်းလင်းချက်အတွက် LLM API သော့ကို သတ်မှတ်ပေးပါ။"
        )
    return (
        f"{crop} is a suitable crop for Myanmar's growing conditions. "
        f"Set the AGROGUARD_LLM_API_KEY environment variable for a detailed AI-powered explanation."
    )


async def get_disease_advice(
    plant: str,
    disease: str,
    is_healthy: bool,
    language: str,
) -> dict:
    if is_healthy:
        if language == "my":
            return {
                "visibleSymptoms": ["ကျန်းမာသောအရွက်လက္ခဏာများ", "စိမ်းလန်းစိုပြေမှု"],
                "possibleCauses": ["ကောင်းမွန်သောစောင့်ရှောက်မှု", "သင့်လျော်သောရာသီဥတု"],
                "treatmentRecommendations": ["လက်ရှိစောင့်ရှောက်မှုကို ဆက်လက်လုပ်ဆောင်ပါ"],
                "preventionRecommendations": ["ရေနှင့်နေရောင်ခြည် အလုံအလောက်ရရှိပါစေ", "ပေါင်းပင်များရှင်းလင်းပါ"]
            }
        return {
            "visibleSymptoms": ["Healthy green foliage", "No spots or discoloration"],
            "possibleCauses": ["Good plant care", "Favorable environment"],
            "treatmentRecommendations": ["Maintain current care routine"],
            "preventionRecommendations": ["Ensure adequate water and sunlight", "Keep area free of weeds"]
        }

    settings = get_settings()
    prompt_template = DISEASE_ADVICE_PROMPT_MY if language == "my" else DISEASE_ADVICE_PROMPT_EN
    user_prompt = prompt_template.format(plant=plant, disease=disease)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_MY if language == "my" else SYSTEM_PROMPT_EN},
        {"role": "user", "content": user_prompt},
    ]

    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 800,
        "response_format": {"type": "json_object"}
    }

    async with AsyncClient(timeout=30) as client:
        try:
            response = await client.post(_llm_url(), json=payload, headers=_llm_headers())
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            return json.loads(content)
        except Exception as e:
            print(f"Error fetching LLM disease advice: {e}")
            return _fallback_disease_advice(plant, disease, language)

def _fallback_disease_advice(plant: str, disease: str, language: str) -> dict:
    if language == "my":
        return {
            "visibleSymptoms": [f"{disease} ၏ ပုံမှန်လက္ခဏာများ"],
            "possibleCauses": [f"{disease} ရောဂါပိုး"],
            "treatmentRecommendations": ["စိုက်ပျိုးရေးပညာရှင်နှင့် တိုင်ပင်ပါ", "သင့်လျော်သော မှိုသတ်ဆေး/ပိုးသတ်ဆေး အသုံးပြုပါ"],
            "preventionRecommendations": ["လေဝင်လေထွက်ကောင်းစေရန် သေချာစေပါ", "ရောဂါကျနေသော အရွက်များကို ဖယ်ရှားပါ"]
        }
    return {
        "visibleSymptoms": [f"Typical symptoms of {disease}"],
        "possibleCauses": [f"{disease} pathogen"],
        "treatmentRecommendations": ["Consult a local agricultural expert", "Apply appropriate fungicide/pesticide"],
        "preventionRecommendations": ["Ensure good airflow", "Remove and destroy infected leaves"]
    }
