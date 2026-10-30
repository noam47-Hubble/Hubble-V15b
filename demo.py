"""HUBIN — sample data loader: 9 hubs (3 professional, 3 business, 3 social) with random registrants.
Every sample hub belongs to the person who loads it (so they keep full management rights)."""
import base64
import random
import time
import uuid
from urllib.parse import quote

from models import (db, User, Card, CardPhoto, Hub, HubBlock, HubOpenPost, HubPresence, BoardMessage, Favorite,
                    HubBan, PrivateMessage, ContactShare, gen_hub_serial, gen_presence_code)

FIRST = ["נועה", "דניאל", "מאיה", "יובל", "תמר", "איתי", "שירה", "עמית", "רוני", "גל", "הילה", "אורי", "ליאור", "מורן", "אלון", "דנה", "ניצן", "יעל", "רן", "מיכל",
         "אסף", "נטע", "עידו", "קרן", "תומר", "שקד", "אביב", "לינוי", "בן", "טל", "אופיר", "עדי", "רותם", "מתן", "ענת", "גילי", "אריאל", "ספיר", "יונתן", "הדר"]
LAST = ["כהן", "לוי", "מזרחי", "פרץ", "ביטון", "דהן", "אברהם", "פרידמן", "אזולאי", "מלכה", "גולן", "שמעון", "אוחנה", "חדד", "בן דוד", "רוזן", "שפירא", "קפלן", "נחום", "אשכנזי",
        "סבן", "עמר", "ברק", "יוסף", "שלום", "זיו", "אלבז", "טל", "גבאי", "רביבו"]
TITLES = ["מנכ״ל", "סמנכ״ל שיווק", "מנהלת מוצר", "ראש צוות פיתוח", "יועץ עסקי", "מנהלת משאבי אנוש", "אנליסטית נתונים", "מהנדס תוכנה", "מעצבת UX", "מנהל מכירות",
          "יזם", "משקיעה", "CISO", "מנהל פרויקטים", "מרצה", "רופאה", "חוקר", "מנהלת תפעול"]
COMPANIES = ["טכנו-דאטה", "ענן ישראל", "סייבר-שילד", "ביונט", "נקסוס", "אלפא-סטארט", "בלו-וייב", "אופק מערכות", "דיגיטל פלוס", "גרין-אנרג׳י", "מדיקל-לינק", "פינטק-IL", "אורבן-לאב", "קוד-אקדמי"]
NICK = ["הנסיך", "הקפטן", "זאב", "דובי", "ברקי", "הכוכב", "פיצי", "שמש", "אריה", "נינג׳ה", "מלכת הכיתה", "רץ", "גולש", "הצל", "ירוק"]
BIOS = ["אוהב קפה טוב ושיחות טובות", "תמיד בדרך לעוד אירוע", "מחפש שותפים לרעיונות", "כאן בשביל הכיף", "מתעניין בטכנולוגיה וקהילה", "אוהבת לטייל ולפגוש אנשים", "פה בשביל הנטוורקינג", "חובב ספורט מושבע"]
MOODS = ["", "", "", "😀", "😎", "🥳", "💪", "🎯", "☕", "🚀"]
PALETTE = ["#2D8CE6", "#e8a33d", "#3ecf7a", "#8e5bd8", "#e0494e", "#17a2b8", "#f06595", "#5c7cfa", "#20c997", "#ff922b"]

BOARD_TEXTS = {
    "professional": ["מישהו יודע באיזה אולם ההרצאה הבאה?", "תודה על המפגש בדוכן הסטארטאפים, נשמח להמשיך את השיחה", "מחפשים שותף פיתוח לפרויקט בתחום ה-AI, מוזמנים לפנות", "מישהו רוצה להצטרף לארוחת צהריים ב-13:00?", "ההרצאה של הפתיחה הייתה מעולה!", "יש מקום פנוי באולם B", "מי מגיע למפגש הנטוורקינג בערב?"],
    "business": ["שלום, האם יש מבצע השבוע?", "היה מעולה, תודה!", "מישהו יודע אם פתוח גם בשישי?", "אשמח להמלצה על המנה הכי טובה", "הגעתי היום לראשונה, מקום נהדר", "יש חניה בסביבה?", "תודה על השירות המצוין"],
    "social": ["מי מגיע הערב? 🙌", "אני ליד הכניסה, חולצה כחולה", "מישהו עם מקום פנוי ברכב?", "איזה אווירה!", "נפגשים בשער בעוד עשר דקות", "מישהו ראה את דנה?", "תמונות מהערב בדרך 📸"],
}
POSTS = ["הנה עדכון קצר מהשטח", "מצאתי את זה מעניין, שווה לראות", "מי שמחפש חניה - החניון הצפוני פנוי", "שאלה לקהילה: מה הכי כדאי לראות כאן?", "תודה לכל מי שהצטרף היום"]

SCENES = {"cyber": "hall", "health": "hall", "startup": "city", "cafe": "cafe", "gym": "gym", "bike": "bike", "stadium": "stadium", "reunion": "beach", "run": "park"}
PINNED = {"cyber", "cafe"}      # only these hubs have an always-open (pinned) window

PLACES = {
    "expo": (32.1069, 34.8083, "מרכז הירידים, תל אביב"), "jlm": (31.7885, 35.2037, "בנייני האומה, ירושלים"), "tlv": (32.0738, 34.7922, "בית התפוצות, תל אביב"),
    "diz": (32.0795, 34.7745, "דיזנגוף 120, תל אביב"), "rlz": (32.0900, 34.8010, "רחוב ביאליק 8, רמת גן"), "hrz": (32.1665, 34.8430, "הרצליה פיתוח"),
    "blm": (32.0554, 34.7625, "אצטדיון בלומפילד, יפו"), "yrk": (32.1000, 34.8000, "פארק הירקון, תל אביב"), "bch": (32.0809, 34.7650, "חוף גורדון, תל אביב"),
}


def _svg(s):
    return "data:image/svg+xml;base64," + base64.b64encode(s.encode("utf-8")).decode()


def avatar(rnd, seed_color=None):
    c1 = seed_color or rnd.choice(PALETTE); c2 = rnd.choice(PALETTE)
    skin = rnd.choice(["#f2c9a0", "#e0ac7e", "#c68642", "#8d5524", "#ffdbb0", "#d9a074"]); hair = rnd.choice(["#2b1d12", "#4a2f1b", "#b0722f", "#1a1a1a", "#d9b46c", "#7a3b1d", "#8c8c8c"])
    shirt = rnd.choice(["#243b6b", "#7a2a45", "#2f6b4f", "#444b5c", "#b5651d", "#3d3a8c", "#1f2937"])
    style = rnd.randint(0, 3)
    if style == 0:      # short hair
        hr = f'<path d="M36 50c0-18 12-26 24-26s24 8 24 26c-8-8-14-12-24-12s-16 4-24 12z" fill="{hair}"/>'
    elif style == 1:    # long hair
        hr = f'<path d="M32 62c-4-30 8-42 28-42s32 12 28 42c-2 10-6 16-8 16 2-14-2-26-20-26s-22 12-20 26c-2 0-6-6-8-16z" fill="{hair}"/>'
    elif style == 2:    # bald / cap
        hr = f'<path d="M36 46c2-16 12-22 24-22s22 6 24 22z" fill="{rnd.choice(PALETTE)}"/><rect x="34" y="44" width="52" height="5" rx="2" fill="#0003"/>'
    else:               # curly
        hr = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{hair}"/>' for x, y in ((40, 40), (50, 33), (62, 31), (74, 35), (82, 44), (38, 52)))
    glasses = '<g fill="none" stroke="#222" stroke-width="2.5"><circle cx="50" cy="54" r="7"/><circle cx="70" cy="54" r="7"/><path d="M57 54h6"/></g>' if rnd.random() < .3 else ""
    smile = f'<path d="M52 65q8 8 16 0" stroke="#7a3b2a" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    return _svg(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
                f'<rect width="120" height="120" fill="url(#g)"/><circle cx="96" cy="22" r="30" fill="#fff" opacity=".12"/><path d="M18 120c0-28 18-42 42-42s42 14 42 42z" fill="{shirt}"/><rect x="52" y="70" width="16" height="14" fill="{skin}"/>'
                f'<circle cx="60" cy="52" r="24" fill="{skin}"/>{hr}<circle cx="50" cy="54" r="2.6" fill="#222"/><circle cx="70" cy="54" r="2.6" fill="#222"/>{glasses}{smile}</svg>')


def _wrap(inner, w=1200, h=800, c1="#123", c2="#012"):
    return _svg(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs><rect width="{w}" height="{h}" fill="url(#g)"/>{inner}</svg>')


def _skyline(rnd, c, base=800, h0=260, h1=520):
    out, x = "", -20
    while x < 1200:
        w = rnd.randint(60, 150); h = rnd.randint(h0, h1)
        out += f'<rect x="{x}" y="{base-h}" width="{w}" height="{h}" fill="{c}" opacity="{rnd.choice([.55,.7,.85])}"/>'
        for wy in range(base - h + 18, base - 10, 34):
            for wx in range(x + 10, x + w - 14, 24):
                if rnd.random() < .45:
                    out += f'<rect x="{wx}" y="{wy}" width="9" height="14" fill="#ffd978" opacity="{rnd.choice([.5,.8,1])}"/>'
        x += w + rnd.randint(0, 14)
    return out


def hub_bg(c1, c2, kind, scene="city"):
    rnd = random.Random()
    stars = "".join(f'<circle cx="{rnd.randint(0,1200)}" cy="{rnd.randint(0,380)}" r="{rnd.choice([1.2,1.8,2.4])}" fill="#fff" opacity="{rnd.choice([.4,.7,1])}"/>' for _ in range(60))
    if scene == "city":        # night skyline
        inner = stars + f'<circle cx="980" cy="130" r="48" fill="#fff" opacity=".85"/>' + _skyline(rnd, c2) + _skyline(rnd, "#000", 800, 150, 330).replace('opacity="', 'opacity=".5" data-o="')
    elif scene == "stadium":   # pitch + floodlights
        lights = "".join(f'<g><rect x="{x}" y="120" width="10" height="330" fill="#cfd8dc"/><rect x="{x-40}" y="90" width="90" height="46" rx="6" fill="#fffde7"/></g><path d="M{x+5} 136L{x-260} 800H{x+270}z" fill="#fff" opacity=".07"/>' for x in (180, 600, 1020))
        pitch = '<rect y="470" width="1200" height="330" fill="#1f8f4a"/>' + "".join(f'<rect x="{i*150}" y="470" width="75" height="330" fill="#fff" opacity=".05"/>' for i in range(8)) + '<ellipse cx="600" cy="640" rx="130" ry="40" fill="none" stroke="#fff" stroke-width="5" opacity=".7"/><path d="M600 470V800" stroke="#fff" stroke-width="5" opacity=".7"/>'
        crowd = "".join(f'<circle cx="{x}" cy="{rnd.randint(440,470)}" r="{rnd.randint(10,16)}" fill="{rnd.choice(PALETTE)}" opacity=".9"/>' for x in range(0, 1200, 26))
        inner = stars + lights + pitch + crowd
    elif scene == "cafe":      # warm interior
        inner = '<rect y="540" width="1200" height="260" fill="#5b3a29"/>' + "".join(f'<rect x="{80+i*170}" y="120" width="130" height="{rnd.randint(150,230)}" rx="6" fill="{rnd.choice(["#c9a66b","#8c5a3c","#2f6b4f","#b55d3a","#4a6fa5"])}"/>' for i in range(7)) + "".join(f'<g><ellipse cx="{x}" cy="610" rx="95" ry="20" fill="#d8b98f"/><rect x="{x-8}" y="610" width="16" height="140" fill="#3b2418"/><circle cx="{x-30}" cy="585" r="16" fill="#fff"/><circle cx="{x+34}" cy="588" r="14" fill="#fff"/></g>' for x in (250, 600, 950)) + "".join(f'<g><path d="M{x} 0V70" stroke="#222" stroke-width="3"/><path d="M{x-34} 70h68l-14 40h-40z" fill="#ffcf6e"/><circle cx="{x}" cy="116" r="60" fill="#ffd978" opacity=".12"/></g>' for x in (300, 600, 900))
    elif scene == "gym":
        inner = '<rect y="560" width="1200" height="240" fill="#1b1d2b"/>' + "".join(f'<g transform="translate({x},{y})"><rect x="0" y="0" width="260" height="14" rx="7" fill="#9aa4b2"/><rect x="-16" y="-34" width="26" height="82" rx="8" fill="#e24b4a"/><rect x="-44" y="-24" width="22" height="62" rx="8" fill="#e24b4a"/><rect x="250" y="-34" width="26" height="82" rx="8" fill="#e24b4a"/><rect x="278" y="-24" width="22" height="62" rx="8" fill="#e24b4a"/></g>' for x, y in ((120, 300), (700, 420), (380, 600))) + "".join(f'<path d="M0 {y}L1200 {y-60}" stroke="#fff" stroke-opacity=".05" stroke-width="40"/>' for y in (200, 500))
    elif scene == "bike":
        wheel = lambda cx: f'<circle cx="{cx}" cy="560" r="110" fill="none" stroke="#f5f5f5" stroke-width="14"/><circle cx="{cx}" cy="560" r="12" fill="#f5f5f5"/>' + "".join(f'<path d="M{cx} 560L{cx+110*__import__("math").cos(a/8*6.283):.0f} {560+110*__import__("math").sin(a/8*6.283):.0f}" stroke="#f5f5f5" stroke-width="2.5"/>' for a in range(8))
        inner = '<rect y="660" width="1200" height="140" fill="#222"/>' + wheel(380) + wheel(760) + '<path d="M380 560L520 380H680L760 560M520 380L470 330H430M680 380L650 330M520 380L610 560L380 560M610 560L680 380" stroke="#ff7a59" stroke-width="14" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' + "".join(f'<circle cx="{rnd.randint(0,1200)}" cy="{rnd.randint(60,300)}" r="{rnd.randint(30,90)}" fill="#fff" opacity=".05"/>' for _ in range(8))
    elif scene == "park":      # hills, trees, sun
        trees = "".join(f'<g><rect x="{x-6}" y="560" width="12" height="70" fill="#5b3a29"/><circle cx="{x}" cy="540" r="{r}" fill="#2e8b57"/></g>' for x, r in ((90, 70), (300, 55), (840, 75), (1080, 60)))
        inner = '<circle cx="920" cy="190" r="80" fill="#ffd978"/><circle cx="920" cy="190" r="130" fill="#ffd978" opacity=".18"/><path d="M0 520Q300 380 620 500T1200 450V800H0z" fill="#3aa05f"/><path d="M0 620Q400 520 800 620T1200 590V800H0z" fill="#2a7d46"/><path d="M-50 760Q500 560 1250 700" stroke="#e8d9a8" stroke-width="40" fill="none"/>' + trees + "".join(f'<ellipse cx="{x}" cy="{y}" rx="70" ry="22" fill="#fff" opacity=".8"/>' for x, y in ((200, 120), (560, 80), (1040, 140)))
    elif scene == "beach":
        inner = stars + '<circle cx="600" cy="420" r="90" fill="#ffb347"/><rect y="420" width="1200" height="380" fill="#1d4e89"/>' + "".join(f'<path d="M0 {y}Q300 {y-30} 600 {y}T1200 {y}" stroke="#fff" stroke-opacity=".3" stroke-width="5" fill="none"/>' for y in (470, 520, 580, 650)) + '<path d="M0 700Q600 640 1200 710V800H0z" fill="#e8d6a0"/>' + "".join(f'<g><path d="M{x} 700V560" stroke="#5b3a29" stroke-width="10"/><path d="M{x} 560q-70-40-110 10M{x} 560q70-40 110 10M{x} 560q-30-70-80-60M{x} 560q30-70 80-60" stroke="#2e8b57" stroke-width="12" fill="none" stroke-linecap="round"/></g>' for x in (150, 1040))
    else:                      # conference hall: stage + spotlights + audience
        beams = "".join(f'<path d="M{x} 0L{x-170} 620H{x+170}z" fill="#fff" opacity=".06"/>' for x in (240, 600, 960))
        stage = '<rect x="260" y="300" width="680" height="150" rx="10" fill="#0d1b3d" opacity=".8"/><rect x="300" y="320" width="600" height="90" rx="6" fill="' + c1 + '"/><text x="600" y="382" text-anchor="middle" font-family="Arial" font-size="46" font-weight="700" fill="#fff" opacity=".9">LIVE</text>'
        aud = "".join(f'<g><circle cx="{x}" cy="{y}" r="22" fill="#0b1226" opacity=".9"/><path d="M{x-34} {y+70}q34-70 68 0z" fill="#0b1226" opacity=".9"/></g>' for y in (590, 690) for x in range(30 if y == 590 else 70, 1200, 110))
        inner = beams + stage + aud
    return _wrap(inner, c1=c1, c2=c2)


def block_img(title, c1, c2, rnd):
    """Illustration for an authority window (map / menu / schedule / people / sponsors...)."""
    t = title
    if any(k in t for k in ("מפה", "מפת", "מסלול")):
        roads = "".join(f'<path d="M{rnd.randint(0,640)} 0Q{rnd.randint(0,640)} 200 {rnd.randint(0,640)} 400" stroke="#fff" stroke-width="{rnd.choice([10,16,22])}" fill="none" opacity=".9"/>' for _ in range(6)) + "".join(f'<path d="M0 {rnd.randint(0,400)}Q320 {rnd.randint(0,400)} 640 {rnd.randint(0,400)}" stroke="#fff" stroke-width="{rnd.choice([8,14])}" fill="none" opacity=".9"/>' for _ in range(5))
        blocks = "".join(f'<rect x="{rnd.randint(0,600)}" y="{rnd.randint(0,360)}" width="{rnd.randint(40,110)}" height="{rnd.randint(30,80)}" rx="6" fill="{rnd.choice(["#cfe8cf","#e6e1d3","#d7e3ee"])}" opacity=".9"/>' for _ in range(14))
        pin = '<g transform="translate(320 190)"><path d="M0 0c-26-34-38-52-38-70a38 38 0 1 1 76 0c0 18-12 36-38 70z" fill="#e24b4a"/><circle cy="-70" r="14" fill="#fff"/></g><ellipse cx="320" cy="198" rx="26" ry="7" fill="#000" opacity=".25"/>'
        return _wrap('<rect width="640" height="400" fill="#e9eef3"/>' + blocks + roads + pin, 640, 400, "#e9eef3", "#e9eef3")
    if any(k in t for k in ("תפריט", "מוצרים", "מנויים", "מבצע")):
        dishes = "".join(f'<g transform="translate({x} 200)"><circle r="92" fill="#fff"/><circle r="70" fill="{col}"/><circle r="36" fill="#fff" opacity=".35"/></g>' for x, col in ((130, "#e07b39"), (320, "#6aa84f"), (510, "#c0504d")))
        return _wrap('<rect width="640" height="400" fill="#f6efe4"/><rect y="300" width="640" height="100" fill="#d9c3a0"/>' + dishes + f'<text x="320" y="62" text-anchor="middle" font-family="Arial" font-size="40" font-weight="700" fill="{c2}">{t}</text>', 640, 400, "#f6efe4", "#f6efe4")
    if any(k in t for k in ("דוברים", "מציגים", "צוות", "מאמנים", "משקיעים")):
        faces = "".join(avatar(rnd).join(('<image href="', f'" x="{30+i*150}" y="130" width="120" height="120" clip-path="circle(60px at 60px 60px)"/>')) for i in range(4))
        return _wrap(f'<rect width="640" height="400" fill="{c2}"/><text x="320" y="80" text-anchor="middle" font-family="Arial" font-size="44" font-weight="700" fill="#fff">{t}</text>' + faces + '<g fill="#fff" opacity=".7">' + "".join(f'<rect x="{35+i*150}" y="275" width="110" height="12" rx="6"/><rect x="{55+i*150}" y="300" width="70" height="10" rx="5"/>' for i in range(4)) + '</g>', 640, 400, c2, c2)
    if any(k in t for k in ("חסות", "ספונס")):
        logos = "".join(f'<g transform="translate({60+i*190} 150)"><rect width="150" height="110" rx="18" fill="#fff"/><circle cx="75" cy="55" r="30" fill="{col}"/></g>' for i, col in enumerate(rnd.sample(PALETTE, 3)))
        return _wrap(f'<rect width="640" height="400" fill="{c2}"/><text x="320" y="86" text-anchor="middle" font-family="Arial" font-size="44" font-weight="700" fill="#fff">{t}</text>' + logos, 640, 400, c2, c2)
    # schedule / program / default banner
    rows = "".join(f'<g transform="translate(60 {110+i*58})"><rect width="520" height="44" rx="10" fill="#fff" opacity=".92"/><rect x="14" y="12" width="70" height="20" rx="6" fill="{c1}"/><rect x="104" y="16" width="{rnd.randint(200,380)}" height="12" rx="6" fill="#999"/></g>' for i in range(5))
    return _wrap(f'<text x="320" y="70" text-anchor="middle" font-family="Arial" font-size="44" font-weight="700" fill="#fff">{t}</text>' + rows, 640, 400, c1, c2)


def hub_logo(letters, c1, c2):
    return _svg(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs><rect width="120" height="120" rx="26" fill="url(#g)"/><text x="60" y="76" font-family="Arial,sans-serif" font-size="46" font-weight="700" fill="#fff" text-anchor="middle">{letters}</text></svg>')


HUBS = [
    # ---- professional
    dict(key="cyber", type="professional", name="CyberTech Israel 2026", tag="כנס הסייבר והאבטחה הגדול בישראל", dates="10-11.11.2026", place="expo", tpl="corporate_classic", c=("#0b3d91", "#071a3a"), logo="CT",
         presence="both", approve=True, n=(70, 110), org="צוות CyberTech",
         blocks=[("תוכנית הכנס", "09:00 רישום וקפה\n10:00 פתיחה וברכות\n10:45 הרצאת מליאה: איומי העתיד\n12:30 ארוחת צהריים\n14:00 סדנאות מקבילות", "other", True), ("מפת האולם", "אולם A - קומה 1 · אולם B - קומה 2 · יריד הסטארטאפים - קומה 0", "other", False),
                 ("דוברים", "ד״ר דנה רוזן - אבטחת ענן\nיובל ברק - Zero Trust\nמיכל גולן - רגולציה", "other", False), ("נותני חסות", "ענן ישראל · סייבר-שילד · נקסוס", "other", False), ("לוח שיתופי", "", "open", False), ("צור קשר", "info@cybertech.example", "other", False)]),
    dict(key="health", type="professional", name="כנס רפואת העתיד", tag="HealthTech Summit - חדשנות בבריאות דיגיטלית", dates="03.12.2026", place="tlv", tpl="creator_purple", c=("#5b2a86", "#1d0f3a"), logo="HT",
         presence="code", approve=True, n=(50, 85), org="הפורום לרפואה דיגיטלית",
         blocks=[("לוח זמנים", "08:30 התכנסות\n09:30 מושב ראשון - AI בדימות\n11:30 פאנל: פרטיות מטופלים\n13:30 סיכום", "other", True), ("מציגים", "מדיקל-לינק · ביונט · פינטק-IL", "other", False), ("מפה", "בית התפוצות, כניסה ראשית מצד צפון", "other", False), ("לוח שיתופי", "", "open", False)]),
    dict(key="startup", type="professional", name="פסגת הסטארטאפים ירושלים", tag="משקיעים פוגשים יזמים", dates="20.12.2026", place="jlm", tpl="logistics_red", c=("#a32d2d", "#3a0e0e"), logo="SP",
         presence="none", approve=False, n=(35, 60), org="ערן ושות׳", pending=5,
         blocks=[("תוכנית היום", "10:00 פיצ׳ים של 20 סטארטאפים\n13:00 מפגש משקיעים\n16:00 נטוורקינג", "other", True), ("רשימת משקיעים", "אלפא-סטארט · בלו-וייב · אורבן-לאב", "other", False), ("לינק לאתר האירוע", "https://example.com/startup-summit", "other", False)]),
    # ---- business
    dict(key="cafe", type="business", name="קפה ספרים - דיזנגוף", tag="קפה, ספרים ואנשים טובים", dates="", place="diz", tpl="community_dynamic", c=("#0f6e56", "#08362b"), logo="קס",
         presence="location", approve=True, n=(30, 55), org="נועה ויובל, בעלי המקום", radius=120,
         blocks=[("תפריט", "קפה הפוך 14 · שקשוקה 42 · סלט ירוק 38 · עוגת גבינה 28", "other", True), ("שעות פעילות", "א-ה 07:00-23:00 · ו 07:00-16:00 · שבת 09:00-23:00", "other", False), ("מבצעים", "קפה + עוגה ב-35 ₪ בשעות הבוקר", "other", False), ("לוח שיתופי", "", "open", False), ("צור קשר", "03-5551234", "other", False)]),
    dict(key="gym", type="business", name="סטודיו כושר Pulse", tag="אימון קבוצתי ואישי", dates="", place="rlz", tpl="minimalist_dark", c=("#e24b4a", "#12141f"), logo="PS",
         presence="none", approve=True, n=(40, 70), org="צוות Pulse",
         blocks=[("מערכת שעות", "א, ג, ה: 06:30 קרוספיט · 18:00 יוגה\nב, ד: 07:00 פילאטיס · 19:00 HIIT", "other", True), ("מנויים ומחירים", "כניסה בודדת 60 ₪ · חודשי 350 ₪ · שנתי 3,200 ₪", "other", False), ("צוות המאמנים", "גל · מורן · אסף · הילה", "other", False), ("לוח שיתופי", "", "open", False)]),
    dict(key="bike", type="business", name="פדל - חנות אופניים וסדנה", tag="אופניים, תיקונים וקהילת רוכבים", dates="", place="hrz", tpl="logistics_red", c=("#c0392b", "#3d1410"), logo="פד",
         presence="location", approve=True, n=(25, 45), org="אלון, בעל החנות", radius=150,
         blocks=[("מוצרים ושירותים", "אופני כביש · אופני הרים · חשמליים · תיקונים תוך יום", "other", True), ("שעות פעילות", "א-ה 09:00-19:00 · ו 09:00-14:00", "other", False), ("מבצעים", "טיפול שנתי ב-199 ₪ עד סוף החודש", "other", False), ("מפה", "הרצליה פיתוח, ליד תחנת הרכבת", "other", False)]),
    # ---- social
    dict(key="stadium", type="social", name="בלומפילד - שער 5", tag="כדורגל · משחק הערב", dates="", place="blm", tpl="community_dynamic", c=("#1b7a3e", "#0a2f18"), logo="B5", glow=True,
         presence="location", approve=True, n=(45, 80), org="חבורת שער 5", radius=500,
         blocks=[("תוכנית הערב", "18:00 התכנסות בשער · 19:30 שריקת פתיחה · 22:00 חגיגות", "other", True), ("מפה", "שער 5, צד מזרחי של האצטדיון", "other", False), ("לוח שיתופי", "", "open", False)]),
    dict(key="reunion", type="social", name="מפגש מחזור י״ב 2006", tag="20 שנה לסיום - ערב נוסטלגיה", dates="14.01.2027", place="bch", tpl="creator_purple", c=("#6a3fb0", "#241047"), logo="20", glow=True,
         presence="none", approve=True, n=(30, 55), org="ועדת המחזור",
         blocks=[("תוכנית האירוע", "20:00 קבלת פנים · 21:00 סרטון זכרונות · 22:00 ריקודים", "other", True), ("לינק לקבוצה", "https://example.com/reunion", "other", False), ("לוח שיתופי", "", "open", False)]),
    dict(key="run", type="social", name="ריצת בוקר פארק הירקון", tag="כל שבת ב-07:00 · כל הקצבים", dates="", place="yrk", tpl="corporate_classic", c=("#1769aa", "#0a2a4a"), logo="🏃", glow=True,
         presence="code", approve=True, n=(25, 50), org="קבוצת הרצים",
         blocks=[("מסלול השבוע", "10 ק״מ סביב הפארק · נקודת מים בקילומטר 5", "other", True), ("לוח שיתופי", "", "open", False), ("צור קשר", "הצטרפו לקבוצת הריצה", "other", False)]),
]


def _pool(rnd, n):
    out, used = [], set()
    while len(out) < n:
        nm = rnd.choice(FIRST) + " " + rnd.choice(LAST)
        if nm in used:
            continue
        used.add(nm); out.append(nm)
    return out


def _make_user(rnd, name):
    u = User(device_id="demo-" + uuid.uuid4().hex, reg_name=name, is_demo=True)
    db.session.add(u); db.session.flush()
    photo = avatar(rnd)
    cards = {}
    for typ in ("business", "social"):
        c = Card(user_id=u.id, card_type=typ, is_active=(typ == "business"), is_open_to_contact=rnd.random() < 0.92, card_name=name.split()[0] + ("1" if typ == "business" else "2"),
                 name=name, name_visible=True, mood=rnd.choice(MOODS))
        if typ == "business":
            c.title, c.title_visible = rnd.choice(TITLES), True
            c.company, c.company_visible = rnd.choice(COMPANIES), True
            if rnd.random() < .4:
                c.phone, c.phone_visible = "05%d-%07d" % (rnd.choice([0, 2, 4, 8]), rnd.randint(1000000, 9999999)), True
            if rnd.random() < .3:
                c.linkedin, c.linkedin_visible = "linkedin.com/in/" + uuid.uuid4().hex[:8], True
        else:
            c.nickname, c.nickname_visible = rnd.choice(NICK), rnd.random() < .6
            c.bio, c.bio_visible = rnd.choice(BIOS), True
        db.session.add(c); db.session.flush()
        if photo:
            db.session.add(CardPhoto(card_id=c.id, url=photo, is_visible=True, is_profile_photo=True, order=0))
        cards[typ] = c
    return u, cards


def _post_img(rnd):
    c1, c2 = rnd.sample(PALETTE, 2)
    return _wrap(f'<circle cx="{rnd.randint(200,1000)}" cy="{rnd.randint(150,350)}" r="{rnd.randint(80,200)}" fill="#fff" opacity=".18"/><path d="M0 800Q300 {rnd.randint(380,520)} 600 {rnd.randint(500,640)}T1200 {rnd.randint(420,560)}V800z" fill="#000" opacity=".25"/>', c1=c1, c2=c2)


def seed(owner):
    """Create the 9 sample hubs (owned by `owner`) with random registrants. Returns a summary."""
    rnd = random.Random()
    now = time.time()
    own_cards = Card.query.filter_by(user_id=owner.id).all()
    if not own_cards:
        raise ValueError("נא ליצור כרטיס אישי לפני טעינת האבי דוגמה")
    biz = next((c for c in own_cards if c.card_type == "business" and c.is_active), None) or next((c for c in own_cards if c.card_type == "business"), None)
    soc = next((c for c in own_cards if c.is_active), None) or own_cards[0]
    pool = []
    for nm in _pool(rnd, 150):
        pool.append(_make_user(rnd, nm))
    summary = []
    for spec in HUBS:
        lat, lng, addr = PLACES[spec["place"]]
        serial = gen_hub_serial()
        while Hub.query.filter_by(serial=serial).first():
            serial = gen_hub_serial()
        oc = (biz or soc) if spec["type"] != "social" else soc
        hub = Hub(owner_user_id=owner.id, owner_card_id=oc.id, name=spec["name"], serial=serial, hub_type=spec["type"], tagline=spec["tag"], event_dates=spec["dates"],
                  location=addr, loc_address=addr, organizer_names=spec["org"], auto_approve=spec["approve"], is_published=True, template_id=spec["tpl"],
                  presence_mode=spec["presence"], loc_lat=lat + rnd.uniform(-.0006, .0006), loc_lng=lng + rnd.uniform(-.0006, .0006), loc_radius=spec.get("radius", 250),
                  presence_code=gen_presence_code(), background_image_url=hub_bg(spec["c"][0], spec["c"][1], spec["type"], SCENES[spec["key"]]), logo_url=hub_logo(spec["logo"], spec["c"][0], spec["c"][1]),
                  glow=bool(spec.get("glow")), card_enabled=True, card_use_hub_bg=True, card_message=rnd.choice(["ברוכים הבאים! נעים שהצטרפתם", "שמחים לראות אתכם כאן", "היכנסו, הכול מוכן בשבילכם"]), is_demo=True)
        db.session.add(hub); db.session.flush()
        blocks = []
        for i, (title, content, cat, pinned) in enumerate(spec["blocks"]):
            b = HubBlock(hub_id=hub.id, title=title, content=content, category=cat, is_default=(bool(pinned) and spec["key"] in PINNED), image_url=("" if cat == "open" or "צור קשר" in title or "לינק" in title else block_img(title, spec["c"][0], spec["c"][1], rnd)), order=i, is_visible=True)
            db.session.add(b); db.session.flush(); blocks.append(b)
        k = rnd.randint(*spec["n"])
        crowd = rnd.sample(pool, k)
        pres = []
        for u, cards in crowd:
            c = cards["social"] if spec["type"] == "social" else cards["business"]
            physical = rnd.random() < .28
            p = HubPresence(hub_id=hub.id, user_id=u.id, card_id=c.id, status="green" if c.is_open_to_contact else "red", is_physical=physical, physical_ts=now + 30 * 86400 if physical else 0.0,
                            is_live=False, approval_status="approved", joined_at=now - rnd.randint(600, 6 * 86400), last_seen=now - rnd.randint(0, 3600), demo=True)
            db.session.add(p); pres.append((u, c))
        for u, cards in rnd.sample(pool, spec.get("pending", 0)):
            c = cards["business"]
            db.session.add(HubPresence(hub_id=hub.id, user_id=u.id, card_id=c.id, status="green", approval_status="pending", is_live=False, joined_at=now - rnd.randint(60, 3000), demo=True))
        for _ in range(rnd.randint(6, 12)):
            u, c = rnd.choice(pres)
            db.session.add(BoardMessage(hub_id=hub.id, sender_user_id=u.id, sender_card_id=c.id, text=rnd.choice(BOARD_TEXTS[spec["type"]]), ts=now - rnd.randint(120, 7 * 3600)))
        for b in blocks:
            if b.category == "open":
                for _ in range(rnd.randint(3, 5)):
                    u, c = rnd.choice(pres)
                    db.session.add(HubOpenPost(hub_id=hub.id, block_id=b.id, user_id=u.id, card_id=c.id, text=rnd.choice(POSTS), image_url=(_post_img(rnd) if rnd.random() < .5 else ""), ts=now - rnd.randint(300, 5 * 3600)))
        # the owner is registered in his own hub as well
        db.session.add(HubPresence(hub_id=hub.id, user_id=owner.id, card_id=oc.id, status="green", approval_status="approved", is_live=False, joined_at=now - 86400, demo=False))
        summary.append({"hub_id": hub.id, "name": hub.name, "type": hub.hub_type, "serial": hub.serial, "registered": k + 1})
    db.session.commit()
    return summary


def clear(owner, everyone=False):
    """Delete the sample hubs (of `owner`, or all of them) and the sample people that no longer belong anywhere."""
    q = Hub.query.filter_by(is_demo=True)
    if not everyone:
        q = q.filter_by(owner_user_id=owner.id)
    ids = [h.id for h in q.all()]
    for hid in ids:
        for model in (HubOpenPost, BoardMessage, Favorite, HubBan, HubPresence, HubBlock):
            model.query.filter_by(hub_id=hid).delete()
        PrivateMessage.query.filter_by(hub_id=hid).update({PrivateMessage.hub_id: None})
        ContactShare.query.filter_by(hub_id=hid).update({ContactShare.hub_id: None})
        Hub.query.filter_by(id=hid).delete()
    db.session.commit()
    if not Hub.query.filter_by(is_demo=True).count():
        for u in User.query.filter_by(is_demo=True).all():
            if PrivateMessage.query.filter((PrivateMessage.from_user_id == u.id) | (PrivateMessage.to_user_id == u.id)).first() or ContactShare.query.filter_by(from_user_id=u.id).first():
                continue      # somebody interacted with this person: keep (still harmless)
            cids = [c.id for c in Card.query.filter_by(user_id=u.id).all()]
            if cids:
                CardPhoto.query.filter(CardPhoto.card_id.in_(cids)).delete(synchronize_session=False)
            Card.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
        db.session.commit()
    return len(ids)


# ---------------------------------------------------------------------------
# A real event hub (not sample data): Mare MED IV Conference. Images live in static/events/maremed/.
# ---------------------------------------------------------------------------
MAREMED_PROGRAM = """13.10 (שני) · 20:00
ערב גאלה בשגרירות יוון בישראל

14.10 (שלישי) · יום הכנס, Herzog Tower  (התוכנית טנטטיבית)
08:30-09:00  התכנסות וקפה
09:00-11:30  פתיחה ומושב ראשון
  · Welcome and Opening - BMP / Conference
  · Opening Remarks - HE Amb. Yael Ravia-Zadok (MFA), HE Amb. Maya Solomou, Sabby Mionis, HE Amb. Christos Sofianopoulos
  · Opportunities Across the Eastern Mediterranean - Adv. Mark Phillips, Herzog
  · The Mare Med Initiative - Adv. Yanos Gramatidis, BAHAS-GRAMATIDIS
  · Data Centers as a Regional Enterprise - Chen Herzog, BDO
  · IAI Welcome - Hezi Israel, IAI
  · The IMEC Potential, the Adani Global Perspective - Capt. Sumit Chauhan, Haifa Port
  · The IMEC Forum and Israel Port Company - Pinhas Tsruya, Israel Ports Company
  · Business Development in the Region - Panayiotis Chrysostomou, Eurobank
  · Greek-Israel Business Development - Adam Ben-Yehuda, Mizrahi-Tefahot
  · Bilateral Cooperation in Developing the Eastern Mediterranean - Prof. Yizhaq Makovsky, University of Haifa
  · Elite Solutions for Maritime Challenges - Alon Shop, Uri Golan, Danchor
  · Technological Water Solutions From Israel to Greece - BlueGen
11:30-12:00  הפסקת קפה
12:00-13:30  מושב שני
  · Gadot Group Brings the IMEC Vision to Life - Opher Linchevski, Gadot Group
  · Israel Shipyards: A Maritime Bridge Between Israel and Greece - Zvi Shechterman
  · IAI presentation: Freedom of Navigation - Sea Lines Security (Sassi Hodeda) · Defence Challenges in the Maritime Arena (Assaf Shtrich) · Evolving Threats to Maritime Ports and Critical Infrastructure (Noam Donenfeld, Avishai Inbar) · Audisea - Next Gen of Acoustic Intelligence (Yair Yanovich)
  · AI Native Professional Services and Cross-Border Transactions - Nimrod Vroman, After The Flood
  · Port Electrification Reinvented - Giora Naveh, Parkomat
  · An Outlook for 2027 Greek-Israeli Tourism - Leon Avigad, Brown Hotels
  · The Next Steps in IMEC, Israel & Greece - Rafael Dreyfus, Cabynda
  · Closing Remarks - Mike Bailey
13:30-14:30  ארוחת צהריים
14:30-18:00  פגישות B2B

15.10 (רביעי) · 09:00-14:00
סיור בחיל הים"""

MAREMED_TOPICS = "מים · חדשנות · ביטחון · אנרגיה · שילוח · תשתיות · נמלים · חקלאות · השקעות · IMEC"
MAREMED_ABOUT = ("ישראל ויוון, בצומת של אירופה, המזרח התיכון, אסיה וצפון אפריקה, חולקות שותפות אסטרטגית וחזון משותף לקידום מזרח הים התיכון כמרכז של חדשנות, קישוריות וצמיחה כלכלית.\n"
                 "הכנס מפגיש מנהיגים בכירים מעולם העסקים, הממשל, התעשייה ומערכת ההשקעות, בתחומי נמלים, שילוח, חקלאות, מים, ביטחון ואנרגיה, וזו הפעם הרביעית שהוא נערך. מטרתו: רשת B2B דינמית ואפקטיבית.")


def load_maremed(owner):
    """Create the 'Mare MED IV' hub for `owner` (real content, no sample registrants). ValueError if it already exists / no card."""
    name = "Mare MED IV Conference"
    if Hub.query.filter_by(owner_user_id=owner.id, name=name).first():
        raise ValueError("ההאב Mare MED IV כבר קיים אצלך")
    cards = Card.query.filter_by(user_id=owner.id).all()
    if not cards:
        raise ValueError("נא ליצור כרטיס אישי לפני טעינת ההאב")
    oc = next((c for c in cards if c.card_type == "business" and c.is_active), None) or next((c for c in cards if c.card_type == "business"), None) or cards[0]
    serial = gen_hub_serial()
    while Hub.query.filter_by(serial=serial).first():
        serial = gen_hub_serial()
    P = "/static/events/maremed/"
    hub = Hub(owner_user_id=owner.id, owner_card_id=oc.id, name=name, serial=serial, hub_type="professional",
              tagline="ישראל · יוון · מזרח הים התיכון", event_dates="13-15.10.2026", location="Herzog Tower, תל אביב",
              loc_address="Yitzhak Sadeh St 6, Tel Aviv-Jaffa", organizer_names="BMP · RESTART",
              auto_approve=True, is_published=True, template_id="corporate_classic", presence_mode="both",
              loc_lat=32.0586, loc_lng=34.7893, loc_radius=250, presence_code=gen_presence_code(),
              background_image_url=P + "banner.jpg", logo_url=P + "logo.png", card_enabled=True, card_use_hub_bg=True,
              card_message="ברוכים הבאים ל-Mare MED IV", description="Mare MED IV Conference, תל אביב, 13-15 באוקטובר 2026")
    db.session.add(hub); db.session.flush()
    blocks = [
        ("תוכנית הכנס", MAREMED_PROGRAM, "", "", ""),
        ("דוברים", "כ-30 דוברים מהמגזר הציבורי, העסקי והביטחוני בישראל וביוון.", P + "speakers.jpg", "", ""),
        ("נושאי הכנס", MAREMED_TOPICS + "\n\n" + MAREMED_ABOUT, P + "topics.jpg", "", ""),
        ("נותני חסות ושותפים", "BMP · Bahas Gramatidis · Herzog Fox & Neeman · BDO · IAI · Enterprise Greece · שגרירות יוון בישראל ועוד", P + "sponsors.jpg", "", ""),
        ("מפה והגעה", "Herzog Tower, Yitzhak Sadeh St 6, Tel Aviv-Jaffa", P + "map.jpg", "", "https://www.google.com/maps/search/?api=1&query=Herzog+Tower+Yitzhak+Sadeh+6+Tel+Aviv"),
        ("המארגנים", "BMP Benny Moran Productions בשיתוף RESTART Innovation & Investment\nמיכל אשכנזי - Event Producer · ליאור רחמנוב - Head of Production · מייק ביילי - Content Director · רותי ברנר-תלמן - Partnership Manager", P + "organizers.jpg", "", ""),
        ("לוח שיתופי", "", "", "open", ""),
        ("צור קשר והרשמה", "Production@bmp.co.il\n03-6966000", "", "", "https://www.bmp.co.il/mare-med-israel-2026"),
    ]
    for i, (title, content, img, cat, link) in enumerate(blocks):
        db.session.add(HubBlock(hub_id=hub.id, title=title, content=content, image_url=img, link_url=link, category=cat or "other", is_default=False, order=i, is_visible=True))
    db.session.add(HubPresence(hub_id=hub.id, user_id=owner.id, card_id=oc.id, status="green", approval_status="approved", is_live=False, joined_at=time.time()))
    db.session.commit()
    return {"hub_id": hub.id, "name": hub.name, "serial": hub.serial}
