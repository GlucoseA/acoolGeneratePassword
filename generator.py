"""
generator.py - 增强版密码与密码短语生成模块

功能：
- 随机密码生成（可选字符集、排除相似/歧义字符、自定义排除）
- 密码短语生成（基于英文词库）
- PIN 码生成
- 密码强度评估（熵值、破解时间估算）
"""

import secrets
import string
import math
import re

# 容易混淆的字符（0/O/1/l/I/i）
SIMILAR_CHARS = frozenset("0O1lIi")

# 歧义特殊字符（在某些系统/字体中难以辨认）
AMBIGUOUS_CHARS = frozenset(r"""{}[]()/\'"`,;:.<>|""")

# ------------------------------------------------------------------
# 密码短语词库（~500 个常用英文单词）
# ------------------------------------------------------------------
WORDLIST = [
    "able", "acid", "aged", "also", "area", "army", "away", "baby", "back", "ball",
    "band", "bank", "base", "bath", "bear", "beat", "bell", "best", "bird", "bite",
    "blue", "boat", "body", "bomb", "bond", "bone", "book", "boot", "born", "boss",
    "bowl", "bulk", "burn", "busy", "calm", "card", "care", "case", "cash", "cave",
    "cell", "chef", "chip", "city", "clay", "clip", "club", "clue", "coat", "code",
    "coil", "cold", "cook", "cool", "copy", "core", "corn", "cost", "crab", "crop",
    "cube", "cure", "cute", "dark", "data", "date", "dawn", "dead", "deal", "dean",
    "debt", "deep", "deer", "deny", "desk", "dial", "diet", "dirt", "disk", "dock",
    "dome", "door", "dose", "down", "draw", "drop", "drum", "dump", "dusk", "dust",
    "duty", "earn", "east", "easy", "edge", "emit", "even", "ever", "evil", "exam",
    "face", "fact", "fail", "fall", "fame", "farm", "fast", "fate", "feel", "feet",
    "file", "fill", "film", "find", "fire", "fish", "fist", "flag", "flat", "flip",
    "flow", "foam", "fold", "folk", "fond", "font", "food", "foot", "fork", "form",
    "fort", "four", "free", "fuel", "full", "fund", "fuse", "gain", "game", "gaze",
    "gear", "gene", "gift", "girl", "give", "glad", "glow", "glue", "goal", "gold",
    "golf", "good", "grab", "gray", "grid", "grin", "grip", "grow", "gulf", "guru",
    "gust", "half", "hall", "hand", "hang", "hard", "harm", "hate", "have", "head",
    "heal", "heap", "heat", "heel", "held", "hero", "hide", "high", "hill", "hint",
    "hire", "hold", "hole", "holy", "home", "hook", "hope", "horn", "host", "hour",
    "hull", "hunt", "hurt", "icon", "idea", "idle", "inch", "iron", "isle", "item",
    "join", "joke", "jump", "just", "keen", "keep", "kick", "kind", "king", "knee",
    "knew", "knot", "know", "lake", "land", "lane", "last", "late", "lead", "leaf",
    "lean", "leap", "left", "lend", "lens", "less", "life", "lift", "like", "lime",
    "line", "link", "lion", "list", "live", "load", "loan", "lock", "loft", "logo",
    "long", "look", "loop", "loss", "loud", "love", "luck", "lung", "mail", "main",
    "make", "many", "mark", "mass", "mean", "meet", "melt", "menu", "mesh", "mild",
    "milk", "mill", "mind", "mine", "mint", "miss", "mode", "more", "most", "move",
    "much", "must", "nail", "name", "navy", "near", "neck", "need", "news", "next",
    "nice", "nine", "node", "none", "noon", "norm", "nose", "note", "noun", "obey",
    "odds", "only", "open", "oral", "over", "oven", "page", "paid", "palm", "park",
    "part", "pass", "path", "peak", "peer", "pick", "pier", "pile", "pine", "pipe",
    "plan", "play", "plot", "plug", "plus", "poem", "poet", "pole", "pool", "poor",
    "port", "pose", "post", "prey", "prod", "prop", "pull", "pump", "pure", "push",
    "race", "rack", "rain", "rank", "rare", "rate", "real", "reed", "rely", "rent",
    "rest", "rice", "rich", "ride", "ring", "rise", "risk", "road", "roam", "roar",
    "rock", "role", "roll", "roof", "room", "rope", "rose", "ruin", "rule", "rush",
    "rust", "safe", "sage", "sail", "sake", "sale", "salt", "same", "sand", "save",
    "seal", "seed", "seek", "seem", "self", "send", "shed", "ship", "shoe", "shop",
    "shot", "show", "shut", "sick", "sign", "silk", "sing", "sink", "site", "size",
    "skin", "skip", "slab", "slim", "slip", "slow", "snap", "snow", "soar", "sock",
    "soft", "soil", "sold", "sole", "song", "soon", "soul", "soup", "spin", "spot",
    "star", "stay", "stem", "step", "stir", "stop", "such", "suit", "sure", "swap",
    "swim", "tail", "tale", "tall", "tank", "tape", "task", "taxi", "team", "tell",
    "tend", "term", "test", "text", "tide", "tile", "till", "time", "tire", "told",
    "toll", "tomb", "tone", "took", "tool", "tour", "town", "trap", "tree", "trim",
    "trio", "trip", "true", "tune", "turn", "twin", "type", "ugly", "unit", "upon",
    "used", "user", "vary", "vast", "very", "vice", "view", "vine", "void", "vote",
    "wage", "wait", "wake", "walk", "wall", "want", "warm", "wash", "wave", "weak",
    "wear", "weed", "week", "well", "west", "wide", "wild", "will", "wind", "wine",
    "wing", "wire", "wish", "wolf", "wood", "word", "work", "worm", "wrap", "yard",
    "yarn", "year", "zero", "zone", "zoom", "atom", "barn", "beam", "bead", "beef",
    "beer", "belt", "bend", "bias", "bike", "bill", "bind", "bloom", "blow", "blur",
    "bolt", "bone", "bore", "brag", "bran", "bred", "brew", "brim", "bull", "bump",
    "bunk", "buoy", "burg", "buzz", "cage", "cake", "cane", "cape", "caps", "cart",
    "cats", "cave", "chap", "char", "chia", "chop", "chug", "cite", "clam", "clap",
    "claw", "clef", "clog", "clop", "clot", "clue", "coal", "coax", "coin", "cola",
    "comet", "cone", "cork", "cove", "cowl", "cram", "crave", "crew", "crop", "crow",
    "curb", "curl", "damp", "darn", "dart", "dash", "dive", "dock", "doll", "dote",
    "dove", "draft", "drag", "dram", "drape", "drew", "drip", "drool", "droop", "drop",
    "drove", "drown", "dual", "dune", "dupe", "dusk", "dwarf", "dwell", "earl", "earn",
    "ease", "edge", "eel", "elbow", "elm", "emote", "enact", "epoch", "equal", "equip",
    "erupt", "event", "exert", "exile", "exude", "fable", "facet", "faint", "fairy",
    "faith", "fault", "feast", "fence", "feral", "ferry", "fever", "fiber", "fifth",
    "fight", "finch", "fjord", "flame", "flair", "flank", "flap", "flaw", "flea",
    "flesh", "fleet", "flew", "flex", "flock", "flood", "flop", "flour", "flute",
    "focal", "foil", "foray", "forge", "forum", "frank", "fraud", "freak", "freed",
    "fresh", "frond", "frost", "froth", "froze", "fruit", "frugal", "fudge", "fungi",
]
# 去重并保留顺序
_seen = set()
_dedup = []
for _w in WORDLIST:
    if _w not in _seen:
        _seen.add(_w)
        _dedup.append(_w)
WORDLIST = _dedup

# ------------------------------------------------------------------
# 预设模板
# ------------------------------------------------------------------
PRESETS = {
    "高安全": {
        "length": 20,
        "use_lower": True,
        "use_upper": True,
        "use_digits": True,
        "use_special": True,
        "exclude_similar": False,
        "exclude_ambiguous": False,
    },
    "标准": {
        "length": 16,
        "use_lower": True,
        "use_upper": True,
        "use_digits": True,
        "use_special": True,
        "exclude_similar": True,
        "exclude_ambiguous": True,
    },
    "易记": {
        "length": 12,
        "use_lower": True,
        "use_upper": True,
        "use_digits": True,
        "use_special": False,
        "exclude_similar": True,
        "exclude_ambiguous": True,
    },
    "数字PIN": {
        "length": 6,
        "use_lower": False,
        "use_upper": False,
        "use_digits": True,
        "use_special": False,
        "exclude_similar": False,
        "exclude_ambiguous": False,
    },
}


# ------------------------------------------------------------------
# 字符集构建
# ------------------------------------------------------------------

def build_alphabet(
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
    exclude_similar: bool = False,
    exclude_ambiguous: bool = False,
    custom_exclude: str = "",
) -> str:
    """根据选项构建可用字符集（去重、有序）"""
    alphabet = ""

    def _filter(chars: str, excl_sim: bool, excl_amb: bool) -> str:
        if excl_sim:
            chars = "".join(c for c in chars if c not in SIMILAR_CHARS)
        if excl_amb:
            chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
        return chars

    if use_lower:
        alphabet += _filter(string.ascii_lowercase, exclude_similar, False)
    if use_upper:
        alphabet += _filter(string.ascii_uppercase, exclude_similar, False)
    if use_digits:
        alphabet += _filter(string.digits, exclude_similar, False)
    if use_special:
        alphabet += _filter(string.punctuation, False, exclude_ambiguous)

    if custom_exclude:
        excl_set = set(custom_exclude)
        alphabet = "".join(c for c in alphabet if c not in excl_set)

    # 去重保序
    seen = set()
    result = []
    for c in alphabet:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return "".join(result)


# ------------------------------------------------------------------
# 密码生成
# ------------------------------------------------------------------

def generate_password(
    length: int = 16,
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_special: bool = True,
    capitalize_first: bool = False,
    exclude_similar: bool = False,
    exclude_ambiguous: bool = False,
    custom_exclude: str = "",
) -> str:
    """生成密码，保证每种选中字符类型至少出现一次"""
    alphabet = build_alphabet(
        use_lower, use_upper, use_digits, use_special,
        exclude_similar, exclude_ambiguous, custom_exclude,
    )
    if not alphabet:
        raise ValueError("没有可用的字符集，请至少选择一种字符类型")

    rng = secrets.SystemRandom()
    excl_set = set(custom_exclude)

    def _pool(chars: str, excl_sim: bool = False, excl_amb: bool = False) -> str:
        if excl_sim:
            chars = "".join(c for c in chars if c not in SIMILAR_CHARS)
        if excl_amb:
            chars = "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
        if excl_set:
            chars = "".join(c for c in chars if c not in excl_set)
        return chars

    # 保证每类至少一个字符
    required = []
    if use_lower:
        pool = _pool(string.ascii_lowercase, exclude_similar)
        if pool:
            required.append(rng.choice(pool))
    if use_upper:
        pool = _pool(string.ascii_uppercase, exclude_similar)
        if pool:
            required.append(rng.choice(pool))
    if use_digits:
        pool = _pool(string.digits, exclude_similar)
        if pool:
            required.append(rng.choice(pool))
    if use_special:
        pool = _pool(string.punctuation, excl_amb=exclude_ambiguous)
        if pool:
            required.append(rng.choice(pool))

    # 截断到目标长度（极端情况）
    if len(required) > length:
        required = required[:length]

    remaining = length - len(required)
    all_chars = required + [rng.choice(alphabet) for _ in range(remaining)]
    rng.shuffle(all_chars)
    password = "".join(all_chars)

    if capitalize_first and password:
        password = password[0].upper() + password[1:]

    return password


# ------------------------------------------------------------------
# 密码短语生成
# ------------------------------------------------------------------

def generate_passphrase(
    num_words: int = 4,
    separator: str = "-",
    capitalize: bool = True,
    add_number: bool = True,
) -> str:
    """生成易记密码短语（单词组合）"""
    rng = secrets.SystemRandom()
    words = [rng.choice(WORDLIST) for _ in range(num_words)]
    if capitalize:
        words = [w.capitalize() for w in words]
    passphrase = separator.join(words)
    if add_number:
        passphrase += separator + str(rng.randint(10, 99))
    return passphrase


# ------------------------------------------------------------------
# PIN 码生成
# ------------------------------------------------------------------

def generate_pin(length: int = 6) -> str:
    """生成数字 PIN 码"""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


# ------------------------------------------------------------------
# 密码强度评估
# ------------------------------------------------------------------

def calculate_strength(password: str) -> dict:
    """
    计算密码强度，返回：
      entropy    - 熵值（bits）
      level      - 强度等级 0-5
      label      - 中文强度标签
      color      - 显示颜色
      crack_time - 人类可读破解时间（假设 GPU 集群 1e11 次/秒）
      char_space - 字符空间大小
    """
    length = len(password)
    if length == 0:
        return {"entropy": 0, "level": 0, "label": "—", "color": "#95a5a6",
                "crack_time": "—", "char_space": 0}

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

    char_space = 0
    if has_lower:   char_space += 26
    if has_upper:   char_space += 26
    if has_digit:   char_space += 10
    if has_special: char_space += 32

    entropy = length * math.log2(char_space) if char_space > 0 else 0

    # 重复字符惩罚
    unique_ratio = len(set(password)) / length
    if unique_ratio < 0.5:
        entropy *= 0.75

    if entropy < 28:
        level, label, color = 0, "极弱", "#e74c3c"
    elif entropy < 40:
        level, label, color = 1, "弱",   "#e67e22"
    elif entropy < 60:
        level, label, color = 2, "一般", "#f1c40f"
    elif entropy < 80:
        level, label, color = 3, "强",   "#2ecc71"
    elif entropy < 100:
        level, label, color = 4, "很强", "#27ae60"
    else:
        level, label, color = 5, "极强", "#1a8a4a"

    guesses_per_sec = 1e11  # GPU 集群
    seconds = (2 ** entropy) / guesses_per_sec
    crack_time = _format_time(seconds)

    return {
        "entropy": round(entropy, 1),
        "level": level,
        "label": label,
        "color": color,
        "crack_time": crack_time,
        "char_space": char_space,
    }


def _format_time(seconds: float) -> str:
    """将秒数格式化为人类可读字符串"""
    if seconds < 1:
        return "不到1秒"
    elif seconds < 60:
        return f"{seconds:.0f} 秒"
    elif seconds < 3600:
        return f"{seconds/60:.0f} 分钟"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} 小时"
    elif seconds < 365.25 * 86400:
        return f"{seconds/86400:.0f} 天"
    elif seconds < 100 * 365.25 * 86400:
        return f"{seconds/(365.25*86400):.1f} 年"
    else:
        years = seconds / (365.25 * 86400)
        if years < 1e6:
            return f"{years:,.0f} 年"
        elif years < 1e12:
            return f"{years:.2e} 年"
        else:
            return f">{years:.1e} 年"
