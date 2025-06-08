from mpstemmer import MPStemmer
import emoji
import re
import unicodedata
from nltk.tokenize import word_tokenize



# --- Fungsi dan Logika Pra-pemrosesan (Tidak ada perubahan dari kode sebelumnya) ---
stemmer = MPStemmer()
slangwords = {
    "yg": "yang", "gk": "gak", "abis": "habis", "ad": "ada", "udh": "sudah", "gw": "aku",
    "gue": "aku", "gua": "aku", "lu": "kamu", "lo": "kamu", "admin": "administrator",
    "ads": "iklan", "aj": "saja", "aja": "saja", "ajg": "anjing", "ama": "sama",
    "anim": "anime", "anj": "anjing", "anjir": "anjing", "apk": "aplikasi",
    "apknya": "aplikasinya", "apl": "aplikasi", "app": "aplikasi", "sub": "dengan teks terjemahan",
    "dub": "sulih suara", "bgm": "musik latar", "profit": "untung", "cuan": "untung",
    "bossku": "bos", "gasken": "ayo", "gas": "ayo", "sultan": "kaya", "badai": "banyak",
    "spin": "putar", "nggak": "tidak", "real": "nyata", "cair": "mencair",
    "testimoni": "bukti", "jp": "jackpot", "jepe": "jackpot", "bigwin": "menang maksimal",
    "maxwin": "menang maksimal", "win": "menang", "wd": "withdraw", "wede": "withdraw",
    "skater": "scatter", "sekater": "scatter", "scater": "scatter", "depo": "deposit",
    "gacer": "gacor", "gecer": "gacor", "gicir": "gacor", "gacir": "gacor",
    "togel": "toto gelap",
}
judol_phrase = {
    "jackpot", "menang maksimal", "scatter", "deposit", "jepe", "slot", "victory", "pawpaw", "sgi",
    "gacor", "nagaikan", "pulauwin", "sgi88", "berkah99", "koislot", "gicir", "seketer", "toto gelap",
    "toto", "sekater", "miya88", "maxwin", "alexis17", "weton88", "jadwal303", "victory88", "tujuh tujuh",
    "withdraw", "mekswin", "makswin", "j200m", "xuxu4d", "dewadora", "aero88", "asia99", "alexis", "lexis",
}

def extract_features1(text):
    dum = {}
    dum['emoji_count'] = emoji.emoji_count(text)
    dum['stylized_alphanum_count'] = len(re.findall(
        r'[\U0001D400-\U0001D7FF\uFF10-\uFF5A\u0400-\u04FF\u0300-\u036F]',
        text
    ))
    return dum

def extract_features2(text):
    dum = {}
    dum['numeric_count'] = len(re.findall(r'[\d\U0001D7CE-\U0001D7FF]', text))
    dum['uppercase_count'] = sum(1 for w in text if w.isupper())
    lenWordSpace = len(re.findall(r'(?:[\W_]\w){2,}', text))
    dum['word_space_count'] = lenWordSpace if lenWordSpace >= 2 else 0
    dum['word_count'] = len(text)
    is_alpha_then_num, is_alpha_num_mixed = 0, 0
    for w in text.split():
        if len(w) < 5: continue
        if re.match(r'^[a-zA-Z]+\d+$', w):
            is_alpha_then_num = 1
            break
        if re.match(r'^(?=.*[a-zA-Z])(?=.*\d)', w):
            is_alpha_num_mixed = 1
    if is_alpha_then_num == 1: is_alpha_num_mixed = 0
    dum['is_alpha_then_num'] = is_alpha_then_num
    dum['is_alpha_num_mixed_and_not_alpha_then_num'] = is_alpha_num_mixed
    return dum

def extract_features3(text):
    dum = {"has_judol_phrase": 0}
    lower_text = text.lower()
    if any(keyword in lower_text for keyword in judol_phrase):
        dum["has_judol_phrase"] = 1
    return dum

def cleaningText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#[A-Za-z0-9]+', '', text)
    text = re.sub(r'RT[\s]', '', text)
    text = re.sub(r"http\S+", '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\n', ' ').strip(' ')
    pattern = r'(?<!\w)((?:[A-Za-z0-9][\s\-\_\.\,\;\:\'\"\`\(\)]){2,}[A-Za-z0-9])(?!\\w)'
    text = re.sub(pattern, lambda m: ' ' + re.sub(r'[\s\-\_\.\,\;\:\'\"\`\(\)]', '', m.group(1)) + ' ', text)
    return text.lower()

def fancytextToNormaltext(text):
    return unicodedata.normalize('NFKD', text)

def fix_slangwords(text):
    return ' '.join([slangwords.get(word.lower(), word) for word in text.split()])

def stemming(tokens_list):
    return stemmer.stem(' '.join(tokens_list))

def preprocess_text(original_comments):
    processed_texts, feature_list = [], []
    for comment in original_comments:

        features1 = extract_features1(comment)
        text_non_stylized = fancytextToNormaltext(comment)
        features2 = extract_features2(text_non_stylized)
        text_clean = cleaningText(text_non_stylized)
        text_slangwords = fix_slangwords(text_clean)
        text_tokenized = word_tokenize(text_slangwords)
        processed_text = stemming(text_tokenized)
        features3 = extract_features3(processed_text)
        features = {**features1, **features2, **features3}

        processed_texts.append(processed_text)
        feature_list.append(features)

    
    return processed_texts, feature_list

