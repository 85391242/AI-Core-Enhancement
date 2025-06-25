import requests
import logging
import time
import re
import markdown
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple, Any, Set
import json
from pathlib import Path
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

from .version_service import StandardVersionControl

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AnalysisEngine")

class AnalysisError(Exception):
    """分析引擎相关错误的基类"""
    pass

class DataFetchError(AnalysisError):
    """数据获取失败时抛出"""
    pass

class AnalysisFailedError(AnalysisError):
    """分析过程失败时抛出"""
    pass

class CapabilityAnalyzer:
    """
    能力分析引擎
    
    负责分析AI行为准则，比较内外部标准，并生成增强建议。
    """
    
    KNOWLEDGE_SOURCES = {
        "ai_safety": "https://openai.com/research/safety",
        "ai_ethics": "https://deepmind.com/research/ethics-and-society",
        "responsible_ai": "https://www.microsoft.com/en-us/ai/responsible-ai",
        "ai_principles": "https://ai.google/principles/",
        "ai_governance": "https://www.ibm.com/watson/ai-ethics"
    }
    
    # 风险类别及其权重
    RISK_CATEGORIES = {
        "privacy": 0.9,
        "security": 0.95,
        "bias": 0.85,
        "transparency": 0.8,
        "accountability": 0.75,
        "safety": 0.9,
        "human_oversight": 0.85
    }
    
    # 缓存过期时间（秒）
    CACHE_EXPIRY = 86400  # 24小时
    
    def __init__(self, vc: StandardVersionControl, data_dir: str = "./data"):
        """
        初始化能力分析引擎
        
        参数:
            vc (StandardVersionControl): 版本控制系统实例
            data_dir (str): 数据目录路径
        """
        self.version_control = vc
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache = self._load_cache()
        self.performance_history = self._load_performance_history()
        self.lemmatizer = WordNetLemmatizer()
        
        # 确保NLTK资源可用
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            logger.info("下载NLTK资源...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        
        logger.info("能力分析引擎初始化完成")
    
    def _load_cache(self) -> Dict:
        """
        加载缓存数据
        
        返回:
            Dict: 缓存数据
        """
        cache_file = self.data_dir / "standards_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("缓存文件损坏，创建新缓存")
        return {}
    
    def _save_cache(self) -> None:
        """保存缓存数据"""
        cache_file = self.data_dir / "standards_cache.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _load_performance_history(self) -> List[Dict]:
        """
        加载性能历史数据
        
        返回:
            List[Dict]: 性能历史数据列表
        """
        history_file = self.data_dir / "performance_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("性能历史文件损坏，创建新历史记录")
        return []
    
    def _save_performance_history(self) -> None:
        """保存性能历史数据"""
        history_file = self.data_dir / "performance_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存性能历史失败: {e}")
    
    def fetch_external_standards(self, source: str) -> Dict:
        """
        获取外部AI准则参考
        
        参数:
            source (str): 数据源名称
            
        返回:
            Dict: 外部标准数据
            
        异常:
            DataFetchError: 数据获取失败时抛出
        """
        # 检查缓存是否有效
        if source in self.cache:
            cache_entry = self.cache[source]
            cache_time = datetime.fromisoformat(cache_entry["timestamp"])
            if datetime.now() - cache_time < timedelta(seconds=self.CACHE_EXPIRY):
                logger.info(f"使用缓存数据: {source}")
                return cache_entry["data"]
        
        if source not in self.KNOWLEDGE_SOURCES:
            error_msg = f"未知数据源: {source}"
            logger.error(error_msg)
            raise DataFetchError(error_msg)
            
        url = self.KNOWLEDGE_SOURCES[source]
        logger.info(f"获取外部标准: {source} ({url})")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = self._parse_html(response.text, source)
            
            # 更新缓存
            self.cache[source] = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            self._save_cache()
            
            return data
            
        except requests.RequestException as e:
            error_msg = f"获取外部标准失败: {e}"
            logger.error(error_msg)
            raise DataFetchError(error_msg)
    
    def _parse_html(self, html: str, source: str) -> Dict:
        """
        解析HTML内容
        
        参数:
            html (str): HTML内容
            source (str): 数据源名称
            
        返回:
            Dict: 解析后的数据
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.title.string if soup.title else "未知标题"
        
        # 提取主要内容
        main_content = ""
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
            text = tag.get_text().strip()
            if text:
                main_content += text + "\n\n"
        
        # 提取章节
        sections = []
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            text = heading.get_text().strip()
            if text:
                sections.append(text)
        
        # 提取关键词
        keywords = self._extract_keywords(main_content)
        
        # 识别风险相关内容
        risks = {}
        for risk_category in self.RISK_CATEGORIES:
            risk_content = self._extract_risk_content(main_content, risk_category)
            if risk_content:
                risks[risk_category] = risk_content
        
        return {
            "title": title,
            "source": source,
            "url": self.KNOWLEDGE_SOURCES[source],
            "sections": sections,
            "content": main_content,
            "keywords": keywords,
            "risks": risks,
            "version": "1.0",
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """
        从文本中提取关键词
        
        参数:
            text (str): 文本内容
            top_n (int): 返回的关键词数量
            
        返回:
            List[str]: 关键词列表
        """
        # 分词
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # 去除停用词
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        # 词形还原
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in filtered_tokens]
        
        # 计算词频
        word_freq = Counter(lemmatized_tokens)
        
        # 返回最常见的词
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def _extract_risk_content(self, text: str, risk_category: str) -> List[str]:
        """
        提取与特定风险类别相关的内容
        
        参数:
            text (str): 文本内容
            risk_category (str): 风险类别
            
        返回:
            List[str]: 相关内容列表
        """
        # 风险类别相关的关键词
        risk_keywords = {
            "privacy": ["privacy", "personal data", "confidential", "data protection", "anonymity", "consent"],
            "security": ["security", "attack", "vulnerability", "threat", "exploit", "breach", "protection"],
            "bias": ["bias", "fairness", "discrimination", "equity", "impartial", "prejudice", "stereotype"],
            "transparency": ["transparency", "explainable", "interpretable", "understandable", "clear", "open"],
            "accountability": ["accountability", "responsible", "liability", "obligation", "answerability"],
            "safety": ["safety", "harm", "risk", "danger", "hazard", "protection", "safeguard"],
            "human_oversight": ["oversight", "supervision", "human-in-the-loop", "control", "intervention"]
        }
        
        # 获取当前风险类别的关键词
        keywords = risk_keywords.get(risk_category, [])
        if not keywords:
            return []
        
        # 分句
        sentences = sent_tokenize(text)
        
        # 提取包含关键词的句子
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                relevant_sentences.append(sentence)
        
        return relevant_sentences
    
    def compare_standards(self, internal: Dict, external: Dict) -> Dict:
        """
        比对内外准则差异
        
        参数:
            internal (Dict): 内部标准
            external (Dict): 外部标准
            
        返回:
            Dict: 比较结果
        """
        comparison = {
            "missing_sections": [],
            "enhancement_opportunities": [],
            "risk_differences": [],
            "keyword_gaps": [],
            "overall_similarity": 0.0
        }
        
        # 章节结构比对
        internal_sections = set(internal.get("sections", []))
        external_sections = set(external.get("sections", []))
        
        for section in external_sections:
            if section not in internal_sections:
                comparison["missing_sections"].append({
                    "name": section,
                    "importance": self._estimate_section_importance(section, external)
                })
        
        # 关键词差异分析
        internal_keywords = set(internal.get("keywords", []))
        external_keywords = set(external.get("keywords", []))
        
        missing_keywords = external_keywords - internal_keywords
        for keyword in missing_keywords:
            comparison["keyword_gaps"].append({
                "keyword": keyword,
                "importance": self._estimate_keyword_importance(keyword, external)
            })
        
        # 风险覆盖分析
        for risk_category, weight in self.RISK_CATEGORIES.items():
            internal_risk = internal.get("risks", {}).get(risk_category, [])
            external_risk = external.get("risks", {}).get(risk_category, [])
            
            if not internal_risk and external_risk:
                comparison["risk_differences"].append({
                    "category": risk_category,
                    "weight": weight,
                    "status": "missing",
                    "examples": external_risk[:3]  # 最多包含3个示例
                })
            elif len(internal_risk) < len(external_risk) * 0.5:  # 内部覆盖不足50%
                comparison["risk_differences"].append({
                    "category": risk_category,
                    "weight": weight,
                    "status": "insufficient",
                    "coverage": len(internal_risk) / len(external_risk) if external_risk else 0
                })
        
        # 内容相似度分析
        internal_content = internal.get("content", "")
        external_content = external.get("content", "")
        
        if internal_content and external_content:
            # 计算整体相似度
            overall_ratio = SequenceMatcher(None, internal_content, external_content).ratio()
            comparison["overall_similarity"] = overall_ratio
            
            # 分段比较
            internal_paragraphs = internal_content.split("\n\n")
            for i, para in enumerate(internal_paragraphs):
                if len(para) < 50:  # 忽略太短的段