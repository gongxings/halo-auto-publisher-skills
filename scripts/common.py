from __future__ import annotations

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


def assert_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def with_retry(action: Callable[[], T], max_retries: int = 3, base_delay_seconds: int = 2) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return action()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(base_delay_seconds * (2 ** (attempt - 1)))
    assert last_exc is not None
    raise last_exc


def new_work_dir(base: str | Path = Path(__file__).resolve().parent.parent / "output") -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = Path(base) / ts
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_markdown_title(markdown_path: str | Path) -> str:
    text = Path(markdown_path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return Path(markdown_path).stem


def sanitize_summary(markdown: str, max_len: int = 160) -> str:
    # Remove markdown formatting and extract plain text
    text = re.sub(r'#{1,6}\s+', '', markdown)  # Remove headings
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Remove italic
    text = re.sub(r'`{1,3}[^`]+`{1,3}', '', text)  # Remove code blocks
    text = re.sub(r'\[.+?\]\(.+?\)', '', text)  # Remove links
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len]


def generate_slug(title: str, max_length: int = 100) -> str:
    """
    Generate an English-only slug from title.
    Transliteration is complex, so we use a simple approach:
    - Keep only ASCII alphanumeric characters
    - Replace spaces with hyphens
    - If no ASCII chars remain, use a timestamp fallback
    """
    import time
    
    # Convert to lowercase
    slug = title.lower()
    
    # Replace common Chinese characters with pinyin-based approximations
    # This is a simplified mapping - for production, consider using pypinyin
    chinese_map = {
        '的': 'de', '一': 'yi', '是': 'shi', '在': 'zai', '不': 'bu',
        '了': 'le', '有': 'you', '和': 'he', '人': 'ren', '这': 'zhe',
        '中': 'zhong', '大': 'da', '为': 'wei', '上': 'shang', '个': 'ge',
        '国': 'guo', '我': 'wo', '以': 'yi', '要': 'yao', '他': 'ta',
        '时': 'shi', '来': 'lai', '用': 'yong', '们': 'men', '生': 'sheng',
        '到': 'dao', '作': 'zuo', '地': 'di', '于': 'yu', '出': 'chu',
        '而': 'er', '方': 'fang', '后': 'hou', '多': 'duo', '得': 'de',
        '说': 'shuo', '你': 'ni', '种': 'zhong', '说': 'shuo', ' ma': 'ma',
        '成': 'cheng', '对': 'dui', '都': 'dou', '和': 'he', '可': 'ke',
        '而': 'er', '去': 'qu', '能': 'neng', '然': 'ran', '过': 'guo',
        '学': 'xue', '它': 'ta', '在': 'zai', '这': 'zhe', '上': 'shang',
        '来': 'lai', '大': 'da', '中': 'zhong', '个': 'ge', '于': 'yu',
        '之': 'zhi', '年': 'nian', '发': 'fa', '成': 'cheng', '只': 'zhi',
        '以': 'yi', '主': 'zhu', '要': 'yao', '同': 'tong', '从': 'cong',
        '将': 'jiang', '看': 'kan', '动': 'dong', '还': 'hai', '进': 'jin',
        '很': 'hen', '意': 'yi', '名': 'ming', '次': 'ci', '事': 'shi',
        '把': 'ba', '价': 'jia', '作': 'zuo', '之': 'zhi', '现': 'xian',
        '力': 'li', '理': 'li', '计': 'ji', '效': 'xiao', '非': 'fei',
        '应': 'ying', '位': 'wei', '展': 'zhan', '但': 'dan', '或': 'huo',
        '却': 'que', '那': 'na', '些': 'xie', '很': 'hen', '知': 'zhi',
        '她': 'ta', '样': 'yang', '前': 'qian', '所': 'suo', ' per': 'per',
        '向': 'xiang', '两': 'liang', '应': 'ying', '些': 'xie', '咯': 'ge',
        '用': 'yong', '还': 'hai', '过': 'guo', '做': 'zuo', '好': 'hao',
        '点': 'dian', '无': 'wu', '已': 'yi', '自': 'zi', '让': 'rang',
        '此': 'ci', '亲': 'qin', '更': 'geng', '等': 'deng', '见': 'jian',
        '位': 'wei', '机': 'ji', '最': 'zui', '新': 'xin', '教': 'jiao',
        '者': 'zhe', '代': 'dai', '表': 'biao', '想': 'xiang', '间': 'jian',
        '与': 'yu', '话': 'hua', '给': 'gei', '把': 'ba', '并': 'bing',
        '度': 'du', '明': 'ming', '作': 'zuo', '果': 'guo', '机': 'ji',
        '外': 'wai', '部': 'bu', '路': 'lu', '条': 'tiao', '住': 'zhu',
        ' hi': 'hi', '请': 'qing', '青': 'qing', '高': 'gao', '开': 'kai',
        '当': 'dang', '书': 'shu', '识': 'shi', '长': 'zhang', '三': 'san',
        '书': 'shu', '下': 'xia', '月': 'yue', '文': 'wen', '比': 'bi',
        '男': 'nan', '女': 'nv', '子': 'zi', '父': 'fu', '母': 'mu',
        '儿': 'er', '先': 'xian', '老': 'lao', '师': 'shi', '星': 'xing',
        '期': 'qi', '回': 'hui', '水': 'shui', '火': 'huo', '木': 'mu',
        '金': 'jin', '土': 'tu', '天': 'tian', '地': 'di', '人': 'ren',
        '数': 'shu', '学': 'xue', '文': 'wen', '英': 'ying', '语': 'yu',
        '音': 'yin', '乐': 'yue', '体': 'ti', '美': 'mei', '术': 'shu',
        '科': 'ke', '技': 'ji', '信': 'xin', '息': 'xi', '计': 'ji',
        '算': 'suan', '机': 'ji', '网': 'wang', '络': 'luo', '编': 'bian',
        '程': 'cheng', '代': 'dai', '码': 'ma', '算': 'suan', '法': 'fa',
        '线': 'xian', '性': 'xing', '代': 'dai', '几': 'ji', '何': 'he',
        '函': 'han', '数': 'shu', '图': 'tu', '像': 'xiang', '视': 'shi',
        '频': 'pin', '声': 'sheng', '文': 'wen', '本': 'ben', '处': 'chu',
        '理': 'li', '编': 'bian', '辑': 'ji', '排': 'pai', '版': 'ban',
        '印': 'yin', '刷': 'shua', '出': 'chu', '版': 'ban', '社': 'she',
        '著': 'zhu', '作': 'zuo', '权': 'quan', '所': 'suo', '属': 'shu',
        '版': 'ban', '权': 'quan', '必': 'bi', '须': 'xu', '经': 'jing',
        '许': 'xu', '可': 'ke', '同': 'tong', '意': 'yi', '方': 'fang',
        '可': 'ke', '使': 'shi', '用': 'yong', '严': 'yan', '禁': 'jin',
        '转': 'zhuan', '载': 'zai', '引': 'yin', '用': 'yong', '请': 'qing',
        '注': 'zhu', '明': 'ming', '出': 'chu', '处': 'chu', '原': 'yuan',
        '作': 'zuo', '者': 'zhe', '公': 'gong', '众': 'zhong', '号': 'hao',
        '微': 'wei', '博': 'bo', '信': 'xin', '公': 'gong', '众': 'zhong',
        '号': 'hao', '订': 'ding', '阅': 'yue', '点': 'dian', '赞': 'zan',
        '转': 'zhuan', '发': 'fa', '分': 'fen', '享': 'xiang'
    }
    
    # Replace Chinese characters with pinyin approximations
    for chinese, pinyin in chinese_map.items():
        slug = slug.replace(chinese, pinyin)
    
    # Remove any non-ASCII alphanumeric characters (keep a-z, 0-9, hyphens)
    slug = re.sub(r'[^a-z0-9-]', '-', slug)
    
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Trim hyphens from start and end
    slug = slug.strip('-')
    
    # Ensure slug is not empty
    if not slug or len(slug) < 2:
        slug = f"post-{int(time.time())}"
    
    # Limit length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug
