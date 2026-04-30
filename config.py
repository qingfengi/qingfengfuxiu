# ====================================================
# Twitter API 配置（填入你自己的key后启用Twitter功能）
# 申请地址: https://developer.twitter.com/
# ====================================================
TWITTER_BEARER_TOKEN = ""   # 填入你的 Bearer Token
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""

# 抓取间隔（秒）
FETCH_INTERVAL = 300  # 每5分钟抓一次

# ====================================================
# RSS 数据源（无需API，立即可用）
# ====================================================
RSS_SOURCES = [
    # ---------- 国际权威媒体 ----------
    {
        "id": "reuters_world",
        "name": "Reuters 路透社",
        "url": "https://feeds.reuters.com/reuters/worldNews",
        "category": "权威媒体",
        "country": "美国/全球",
        "flag": "🌐",
        "color": "#FF6B35",
    },
    {
        "id": "ap_world",
        "name": "AP 美联社",
        "url": "https://rsshub.app/apnews/topics/ap-top-news",
        "category": "权威媒体",
        "country": "美国/全球",
        "flag": "🇺🇸",
        "color": "#E63946",
    },
    {
        "id": "bbc_world",
        "name": "BBC World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "权威媒体",
        "country": "英国",
        "flag": "🇬🇧",
        "color": "#BB1919",
    },
    {
        "id": "france24_en",
        "name": "France 24",
        "url": "https://www.france24.com/en/rss",
        "category": "官方媒体",
        "country": "法国",
        "flag": "🇫🇷",
        "color": "#003189",
    },
    {
        "id": "dw_world",
        "name": "Deutsche Welle 德国之声",
        "url": "https://rss.dw.com/xml/rss-en-world",
        "category": "官方媒体",
        "country": "德国",
        "flag": "🇩🇪",
        "color": "#C8161D",
    },
    {
        "id": "aljazeera",
        "name": "Al Jazeera 半岛电视台",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "权威媒体",
        "country": "卡塔尔",
        "flag": "🇶🇦",
        "color": "#E8721A",
    },
    {
        "id": "rt_world",
        "name": "RT 今日俄罗斯",
        "url": "https://www.rt.com/rss/news/",
        "category": "官方媒体",
        "country": "俄罗斯",
        "flag": "🇷🇺",
        "color": "#1A6FBF",
    },
    {
        "id": "xinhua_en",
        "name": "Xinhua 新华社",
        "url": "https://feeds.xinhuanet.com/english/rss/world.xml",
        "category": "官方媒体",
        "country": "中国",
        "flag": "🇨🇳",
        "color": "#CC0000",
    },
    {
        "id": "cgtn",
        "name": "CGTN 中国国际电视台",
        "url": "https://www.cgtn.com/subscribe/rss/section/world.do",
        "category": "官方媒体",
        "country": "中国",
        "flag": "🇨🇳",
        "color": "#8B0000",
    },
    {
        "id": "globaltimes",
        "name": "Global Times 环球时报",
        "url": "https://www.globaltimes.cn/rss/outbrain.xml",
        "category": "官方媒体",
        "country": "中国",
        "flag": "🇨🇳",
        "color": "#B22222",
    },
    {
        "id": "nyt_world",
        "name": "New York Times 纽约时报",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "category": "权威媒体",
        "country": "美国",
        "flag": "🇺🇸",
        "color": "#333333",
    },
    {
        "id": "guardian_world",
        "name": "The Guardian 卫报",
        "url": "https://www.theguardian.com/world/rss",
        "category": "权威媒体",
        "country": "英国",
        "flag": "🇬🇧",
        "color": "#052962",
    },
    {
        "id": "sputnik_world",
        "name": "Sputnik 卫星通讯社",
        "url": "https://sputnikglobe.com/export/rss2/world/index.xml",
        "category": "官方媒体",
        "country": "俄罗斯",
        "flag": "🇷🇺",
        "color": "#0055A5",
    },
    {
        "id": "nhk_world",
        "name": "NHK World 日本放送协会",
        "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "category": "官方媒体",
        "country": "日本",
        "flag": "🇯🇵",
        "color": "#003580",
    },
    {
        "id": "un_news",
        "name": "UN News 联合国新闻",
        "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
        "category": "国际组织",
        "country": "国际",
        "flag": "🌍",
        "color": "#009EDB",
    },
    {
        "id": "voa_world",
        "name": "VOA 美国之音",
        "url": "https://feeds.voanews.com/voaeng/world",
        "category": "官方媒体",
        "country": "美国",
        "flag": "🇺🇸",
        "color": "#1A5276",
    },
]

# ====================================================
# Twitter 账号配置（需要Twitter API key）
# ====================================================
TWITTER_ACCOUNTS = [
    # 中国官方媒体
    {"username": "XHNews", "name": "新华社英文", "category": "官方媒体", "country": "中国", "flag": "🇨🇳"},
    {"username": "CGTNOfficial", "name": "CGTN", "category": "官方媒体", "country": "中国", "flag": "🇨🇳"},
    {"username": "PDChina", "name": "人民日报英文", "category": "官方媒体", "country": "中国", "flag": "🇨🇳"},
    {"username": "globaltimesnews", "name": "环球时报", "category": "官方媒体", "country": "中国", "flag": "🇨🇳"},
    {"username": "MFA_China", "name": "中国外交部", "category": "政府机构", "country": "中国", "flag": "🇨🇳"},

    # 俄罗斯
    {"username": "RT_com", "name": "RT今日俄罗斯", "category": "官方媒体", "country": "俄罗斯", "flag": "🇷🇺"},
    {"username": "tass_agency", "name": "塔斯社", "category": "官方媒体", "country": "俄罗斯", "flag": "🇷🇺"},
    {"username": "MFA_Russia", "name": "俄罗斯外交部", "category": "政府机构", "country": "俄罗斯", "flag": "🇷🇺"},

    # 美国政府
    {"username": "POTUS", "name": "美国总统", "category": "国家领导人", "country": "美国", "flag": "🇺🇸"},
    {"username": "StateDept", "name": "美国国务院", "category": "政府机构", "country": "美国", "flag": "🇺🇸"},
    {"username": "WhiteHouse", "name": "白宫", "category": "政府机构", "country": "美国", "flag": "🇺🇸"},

    # 国际机构
    {"username": "UN", "name": "联合国", "category": "国际组织", "country": "国际", "flag": "🌍"},
    {"username": "SecGen", "name": "联合国秘书长", "category": "国际组织", "country": "国际", "flag": "🌍"},
    {"username": "NATO", "name": "北约", "category": "国际组织", "country": "国际", "flag": "🌐"},

    # 国际权威媒体
    {"username": "Reuters", "name": "路透社", "category": "权威媒体", "country": "全球", "flag": "🌐"},
    {"username": "AP", "name": "美联社", "category": "权威媒体", "country": "全球", "flag": "🌐"},
    {"username": "BBCWorld", "name": "BBC World", "category": "权威媒体", "country": "英国", "flag": "🇬🇧"},
    {"username": "AJEnglish", "name": "半岛电视台英文", "category": "权威媒体", "country": "卡塔尔", "flag": "🇶🇦"},
    {"username": "DWWorld", "name": "德国之声", "category": "权威媒体", "country": "德国", "flag": "🇩🇪"},
    {"username": "France24", "name": "法国24小时", "category": "权威媒体", "country": "法国", "flag": "🇫🇷"},
]

CATEGORIES = ["全部", "官方媒体", "权威媒体", "国家领导人", "政府机构", "国际组织", "中立媒体"]
COUNTRIES = ["全部", "中国", "美国", "英国", "法国", "德国", "俄罗斯", "日本", "卡塔尔", "国际"]
