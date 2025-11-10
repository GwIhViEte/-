"""
Quality scoring module for novel generation evaluation.
Provides heuristic and LLM-based quality assessment for chapters and sections.
"""

import re
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import json
import asyncio

# Optional imports for LLM evaluation
try:
    import aiohttp

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Setup quality-specific logger
quality_logger = logging.getLogger("novel_generator.quality")


def log_quality_metrics(
    doc_id: str,
    overall_score: float,
    word_count: int,
    processing_time: float,
    rewrite_count: int = 0,
):
    """Log quality metrics for tracking"""
    quality_logger.info(
        f"QUALITY_METRICS - doc_id:{doc_id}, score:{overall_score:.1f}, "
        f"words:{word_count}, time:{processing_time:.2f}s, rewrites:{rewrite_count}"
    )


def log_rewrite_event(
    doc_id: str, chapter_idx: int, section_idx: int, original_score: float, action: str
):
    """Log rewrite events"""
    quality_logger.info(
        f"REWRITE_EVENT - doc_id:{doc_id}, ch:{chapter_idx}, "
        f"sec:{section_idx}, score:{original_score:.1f}, action:{action}"
    )


@dataclass
class QualityScore:
    """Quality score data structure"""

    overall: float  # 0-100 overall score
    readability: float  # 0-100 readability score
    coherence: float  # 0-100 coherence score
    canon_consistency: float  # 0-100 canon consistency score
    genre_fit: float  # 0-100 genre fit score
    rewrite_suggestion: str = ""  # Suggestion for improvement
    word_count: int = 0
    processing_time: float = 0.0


@dataclass
class SectionQuality:
    """Section quality data"""

    idx: int
    score: QualityScore
    text: str = ""
    start_pos: int = 0
    end_pos: int = 0


@dataclass
class ChapterQuality:
    """Chapter quality data"""

    idx: int
    score: QualityScore
    sections: List[SectionQuality]
    text: str = ""


@dataclass
class DocumentQuality:
    """Document quality data"""

    doc_id: str
    chapters: List[ChapterQuality]
    overall_score: float
    total_word_count: int
    genre: str = ""
    language: str = "中文"
    created_at: str = ""


class QualityScorer:
    """Main quality scoring class"""

    def __init__(
        self,
        use_llm_evaluation: bool = False,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        llm_budget_limit: int = 10,
    ):
        """
        Initialize quality scorer

        Args:
            use_llm_evaluation: Whether to use LLM for evaluation
            api_key: API key for LLM evaluation
            model: Model name for LLM evaluation
            base_url: Base URL for LLM API
            llm_budget_limit: Maximum number of LLM evaluations
        """
        self.use_llm_evaluation = use_llm_evaluation
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.llm_budget_limit = llm_budget_limit
        self.llm_usage_count = 0

    def _calculate_readability_heuristic(self, text: str) -> float:
        """Calculate readability score using heuristic methods"""
        if not text:
            return 0.0

        # Basic text statistics
        sentences = re.split(r"[。！？.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        # Average sentence length
        avg_sentence_length = len(text) / len(sentences)

        # Sentence length variation (good writing has variation)
        sentence_lengths = [len(s) for s in sentences]
        length_variance = sum(
            (l - avg_sentence_length) ** 2 for l in sentence_lengths
        ) / len(sentence_lengths)

        # Paragraph structure
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Scoring factors
        score = 50.0  # Base score

        # Optimal sentence length is 15-25 characters for Chinese
        if 15 <= avg_sentence_length <= 25:
            score += 20
        elif 10 <= avg_sentence_length <= 35:
            score += 10
        elif avg_sentence_length > 50 or avg_sentence_length < 8:
            score -= 20

        # Sentence length variation
        if 50 <= length_variance <= 200:
            score += 15
        elif length_variance > 500:
            score -= 10

        # Paragraph structure (3-8 paragraphs per section is good)
        if 3 <= len(paragraphs) <= 8:
            score += 10
        elif len(paragraphs) > 15:
            score -= 10

        # Dialogue balance (for fiction)
        dialogue_matches = re.findall(r'["「『].*?["」』]', text)
        dialogue_ratio = len("".join(dialogue_matches)) / len(text) if text else 0
        if 0.1 <= dialogue_ratio <= 0.3:  # 10-30% dialogue is good
            score += 5
        elif dialogue_ratio > 0.5:
            score -= 10

        return min(100.0, max(0.0, score))

    def _calculate_coherence_heuristic(self, text: str) -> float:
        """Calculate coherence score using heuristic methods"""
        if not text:
            return 0.0

        sentences = re.split(r"[。！？.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 50.0

        score = 50.0

        # Check for transition words
        transition_words = [
            "但是",
            "然而",
            "因此",
            "所以",
            "接着",
            "然后",
            "首先",
            "其次",
            "最后",
            "不过",
            "另外",
            "此外",
            "总之",
            "综上所述",
            "由此可见",
        ]
        transition_count = sum(1 for word in transition_words if word in text)
        transition_ratio = transition_count / len(sentences)

        if 0.1 <= transition_ratio <= 0.3:
            score += 20
        elif transition_ratio < 0.05:
            score -= 15

        # Check pronoun consistency (simplified)
        pronoun_patterns = ["他", "她", "它", "他们", "她们", "它们", "我", "你", "您"]
        pronoun_usage = [text.count(p) for p in pronoun_patterns]

        # Basic coherence: avoid too many sudden topic changes
        if len(sentences) > 0:
            # Check sentence length consistency (extreme variations may indicate incoherence)
            sentence_lengths = [len(s) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            extreme_variations = sum(
                1
                for length in sentence_lengths
                if length < avg_length * 0.3 or length > avg_length * 3
            )

            if extreme_variations / len(sentences) < 0.2:
                score += 10
            else:
                score -= 10

        # Check for repeated phrases (may indicate poor flow)
        words = re.findall(r"[\w]+", text)
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # Penalize excessive repetition
            repeated_words = sum(
                1 for count in word_freq.values() if count > len(words) * 0.1
            )
            if repeated_words == 0:
                score += 10
            elif repeated_words > 3:
                score -= 15

        return min(100.0, max(0.0, score))

    def _calculate_canon_consistency_heuristic(
        self, text: str, context: Optional[str] = None
    ) -> float:
        """Calculate canon consistency score using heuristic methods"""
        if not text:
            return 0.0

        score = 70.0  # Base score - assume consistency unless proven otherwise

        # Check for consistency indicators
        consistency_issues = []

        # Time consistency (simplified check)
        time_indicators = [
            "早上",
            "中午",
            "下午",
            "晚上",
            "昨天",
            "今天",
            "明天",
            "过去",
            "未来",
        ]
        time_mentions = [
            indicator for indicator in time_indicators if indicator in text
        ]

        # Character name consistency (basic check)
        # This is a simplified version - in practice, you'd need NER
        potential_names = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
        name_freq = {}
        for name in potential_names:
            if len(name) >= 2:  # Likely a name
                name_freq[name] = name_freq.get(name, 0) + 1

        # Look for potential inconsistencies (very basic)
        if context:
            # Check if key elements from context are maintained
            context_names = set(re.findall(r"[\u4e00-\u9fff]{2,4}", context))
            text_names = set(potential_names)

            # If context has names but text doesn't, might be inconsistent
            if context_names and not context_names.intersection(text_names):
                score -= 20

        # Check for contradictory statements (simplified)
        contradictions = ["但是", "然而", "相反", "与此相反"]
        contradiction_count = sum(1 for word in contradictions if word in text)

        # Some contradictions are fine for drama, too many may indicate inconsistency
        if contradiction_count > len(text) / 1000:  # More than 1 per 1000 characters
            score -= 15

        return min(100.0, max(0.0, score))

    def _calculate_genre_fit_heuristic(self, text: str, genre: str) -> float:
        """Calculate genre fit score using heuristic methods"""
        if not text or not genre:
            return 50.0

        # Genre-specific keywords (simplified)
        genre_keywords = {
            "奇幻冒险": [
                "魔法",
                "龙",
                "精灵",
                "冒险",
                "剑",
                "法术",
                "异世界",
                "勇士",
                "魔王",
            ],
            "科幻未来": [
                "科技",
                "未来",
                "星际",
                "机器人",
                "人工智能",
                "宇宙",
                "时间",
                "基因",
            ],
            "悬疑推理": [
                "案件",
                "谜题",
                "线索",
                "证据",
                "凶手",
                "真相",
                "推理",
                "嫌疑",
            ],
            "武侠江湖": [
                "武功",
                "江湖",
                "侠客",
                "剑法",
                "内功",
                "门派",
                "师父",
                "仇人",
            ],
            "都市言情": [
                "爱情",
                "感情",
                "心动",
                "约会",
                "表白",
                "分手",
                "吃醋",
                "浪漫",
            ],
            "历史传奇": [
                "古代",
                "皇帝",
                "将军",
                "战争",
                "朝代",
                "历史",
                "传奇",
                "天下",
            ],
        }

        score = 50.0  # Base score

        if genre in genre_keywords:
            keywords = genre_keywords[genre]
            keyword_count = sum(1 for keyword in keywords if keyword in text)
            keyword_density = keyword_count / len(keywords)

            # Score based on keyword presence
            if keyword_density >= 0.3:
                score += 30
            elif keyword_density >= 0.1:
                score += 15
            elif keyword_density == 0:
                score -= 20

        # Check tone and style appropriateness
        text_length = len(text)

        # Different genres have different optimal lengths
        if "奇幻" in genre or "科幻" in genre:
            # These genres typically need more descriptive text
            if text_length > 500:
                score += 10
        elif "言情" in genre:
            # Romance can be more dialogue-heavy
            dialogue_ratio = (
                len(re.findall(r'["「『].*?["」』]', text)) / text_length if text else 0
            )
            if 0.2 <= dialogue_ratio <= 0.4:
                score += 10

        return min(100.0, max(0.0, score))

    async def _evaluate_with_llm(
        self,
        text: str,
        context: Optional[str] = None,
        genre: str = "",
        section_type: str = "section",
    ) -> QualityScore:
        """Evaluate text quality using LLM"""
        if not HAS_AIOHTTP:
            quality_logger.warning(
                "aiohttp not available, falling back to heuristic evaluation"
            )
            return self._evaluate_heuristic(text, context, genre)

        if self.llm_usage_count >= self.llm_budget_limit:
            quality_logger.warning(
                f"LLM budget limit reached ({self.llm_budget_limit}), falling back to heuristic"
            )
            return self._evaluate_heuristic(text, context, genre)

        start_time = time.time()

        prompt = f"""
请评估以下{section_type}文本的质量，从4个维度打分（0-100分）：

1. 可读性 (Readability) - 文字是否流畅易懂，句子结构是否合理
2. 连贯性 (Coherence) - 逻辑是否清晰，段落间衔接是否自然  
3. 设定一致性 (Canon Consistency) - 人物、时间、地点等设定是否前后一致
4. 类型贴合度 (Genre Fit) - 是否符合{genre or '小说'}类型的特征和风格

文本内容：
{text[:2000]}  # Limit text length for API

{'前文上下文：' + context[:500] if context else ''}

请以JSON格式返回评分：
{{
    "readability": 分数,
    "coherence": 分数, 
    "canon_consistency": 分数,
    "genre_fit": 分数,
    "rewrite_suggestion": "改进建议（50字以内）"
}}
"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            }

            url = (
                f"{self.base_url}/chat/completions"
                if self.base_url
                else "https://api.openai.com/v1/chat/completions"
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=headers, json=data, timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]

                        # Parse JSON response
                        try:
                            evaluation = json.loads(content)
                            self.llm_usage_count += 1

                            processing_time = time.time() - start_time

                            return QualityScore(
                                overall=0,  # Will be calculated
                                readability=evaluation.get("readability", 50),
                                coherence=evaluation.get("coherence", 50),
                                canon_consistency=evaluation.get(
                                    "canon_consistency", 50
                                ),
                                genre_fit=evaluation.get("genre_fit", 50),
                                rewrite_suggestion=evaluation.get(
                                    "rewrite_suggestion", ""
                                ),
                                processing_time=processing_time,
                            )
                        except json.JSONDecodeError:
                            quality_logger.error("Failed to parse LLM response as JSON")
                            return self._evaluate_heuristic(text, context, genre)
                    else:
                        quality_logger.error(
                            f"LLM API request failed: {response.status}"
                        )
                        return self._evaluate_heuristic(text, context, genre)

        except Exception as e:
            quality_logger.error(f"LLM evaluation failed: {str(e)}")
            return self._evaluate_heuristic(text, context, genre)

    def _evaluate_heuristic(
        self, text: str, context: Optional[str] = None, genre: str = ""
    ) -> QualityScore:
        """Evaluate text quality using heuristic methods"""
        start_time = time.time()

        readability = self._calculate_readability_heuristic(text)
        coherence = self._calculate_coherence_heuristic(text)
        canon_consistency = self._calculate_canon_consistency_heuristic(text, context)
        genre_fit = self._calculate_genre_fit_heuristic(text, genre)

        # Calculate overall score (weighted average)
        overall = (
            readability * 0.3
            + coherence * 0.3
            + canon_consistency * 0.2
            + genre_fit * 0.2
        )

        processing_time = time.time() - start_time

        # Generate rewrite suggestion based on lowest score
        scores = {
            "可读性": readability,
            "连贯性": coherence,
            "设定一致性": canon_consistency,
            "类型贴合度": genre_fit,
        }

        lowest_aspect = min(scores, key=scores.get)
        suggestions = {
            "可读性": "调整句式结构，增加段落层次",
            "连贯性": "加强逻辑衔接，补充过渡词句",
            "设定一致性": "检查人物设定，确保时间线一致",
            "类型贴合度": "增强类型特征，调整写作风格",
        }

        rewrite_suggestion = suggestions.get(lowest_aspect, "整体优化提升")

        return QualityScore(
            overall=overall,
            readability=readability,
            coherence=coherence,
            canon_consistency=canon_consistency,
            genre_fit=genre_fit,
            rewrite_suggestion=rewrite_suggestion,
            word_count=len(text),
            processing_time=processing_time,
        )

    async def evaluate_text(
        self,
        text: str,
        context: Optional[str] = None,
        genre: str = "",
        use_llm: Optional[bool] = None,
    ) -> QualityScore:
        """
        Evaluate text quality

        Args:
            text: Text to evaluate
            context: Previous context for coherence checking
            genre: Genre of the text
            use_llm: Whether to use LLM evaluation (overrides instance setting)

        Returns:
            QualityScore object
        """
        if not text:
            return QualityScore(
                overall=0, readability=0, coherence=0, canon_consistency=0, genre_fit=0
            )

        use_llm = use_llm if use_llm is not None else self.use_llm_evaluation

        if use_llm and self.api_key:
            return await self._evaluate_with_llm(text, context, genre)
        else:
            return self._evaluate_heuristic(text, context, genre)

    def split_text_into_sections(
        self, text: str, max_section_length: int = 1000
    ) -> List[str]:
        """Split text into sections for evaluation"""
        if not text:
            return []

        # Try to split by paragraphs first
        paragraphs = re.split(r"\n\s*\n", text)
        sections = []
        current_section = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if len(current_section + paragraph) <= max_section_length:
                current_section += paragraph + "\n\n"
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = paragraph + "\n\n"

        if current_section:
            sections.append(current_section.strip())

        # If no paragraphs or sections too long, split by sentence
        if not sections or any(len(s) > max_section_length * 1.5 for s in sections):
            sections = []
            sentences = re.split(r"[。！？.!?]+", text)
            current_section = ""

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                if len(current_section + sentence) <= max_section_length:
                    current_section += sentence + "。"
                else:
                    if current_section:
                        sections.append(current_section)
                    current_section = sentence + "。"

            if current_section:
                sections.append(current_section)

        return sections

    async def evaluate_chapter(
        self,
        chapter_text: str,
        chapter_idx: int,
        context: Optional[str] = None,
        genre: str = "",
    ) -> ChapterQuality:
        """
        Evaluate a chapter

        Args:
            chapter_text: Chapter text content
            chapter_idx: Chapter index
            context: Previous chapters context
            genre: Genre of the novel

        Returns:
            ChapterQuality object
        """
        sections_text = self.split_text_into_sections(chapter_text)
        sections = []

        for i, section_text in enumerate(sections_text):
            # Get context for this section (previous sections)
            section_context = (
                context + "\n\n".join(sections_text[:i]) if context or i > 0 else None
            )

            score = await self.evaluate_text(section_text, section_context, genre)

            section = SectionQuality(
                idx=i + 1,
                score=score,
                text=section_text,
                start_pos=(
                    chapter_text.find(section_text)
                    if section_text in chapter_text
                    else 0
                ),
                end_pos=(
                    chapter_text.find(section_text) + len(section_text)
                    if section_text in chapter_text
                    else len(section_text)
                ),
            )
            sections.append(section)

        # Calculate chapter overall score
        if sections:
            chapter_overall = sum(s.score.overall for s in sections) / len(sections)
            chapter_readability = sum(s.score.readability for s in sections) / len(
                sections
            )
            chapter_coherence = sum(s.score.coherence for s in sections) / len(sections)
            chapter_canon = sum(s.score.canon_consistency for s in sections) / len(
                sections
            )
            chapter_genre = sum(s.score.genre_fit for s in sections) / len(sections)
            chapter_word_count = sum(s.score.word_count for s in sections)
            chapter_processing_time = sum(s.score.processing_time for s in sections)

            chapter_score = QualityScore(
                overall=chapter_overall,
                readability=chapter_readability,
                coherence=chapter_coherence,
                canon_consistency=chapter_canon,
                genre_fit=chapter_genre,
                word_count=chapter_word_count,
                processing_time=chapter_processing_time,
            )
        else:
            chapter_score = await self.evaluate_text(chapter_text, context, genre)

        return ChapterQuality(
            idx=chapter_idx, score=chapter_score, sections=sections, text=chapter_text
        )

    async def evaluate_document(
        self,
        doc_id: str,
        chapters: List[Tuple[int, str]],
        genre: str = "",
        language: str = "中文",
    ) -> DocumentQuality:
        """
        Evaluate an entire document

        Args:
            doc_id: Document ID
            chapters: List of (chapter_idx, chapter_text) tuples
            genre: Genre of the novel
            language: Language of the novel

        Returns:
            DocumentQuality object
        """
        import datetime

        start_time = time.time()

        chapter_qualities = []
        total_word_count = 0
        total_processing_time = 0
        context = ""

        quality_logger.info(f"Starting quality evaluation for document: {doc_id}")

        for chapter_idx, chapter_text in chapters:
            chapter_quality = await self.evaluate_chapter(
                chapter_text, chapter_idx, context, genre
            )
            chapter_qualities.append(chapter_quality)

            total_word_count += chapter_quality.score.word_count
            total_processing_time += chapter_quality.score.processing_time

            # Update context for next chapter (use summary to avoid too much context)
            if len(context) < 2000:  # Keep context manageable
                context += f"\n\n第{chapter_idx}章: {chapter_text[:500]}..."
            else:
                context = f"...第{chapter_idx}章: {chapter_text[:500]}..."

        # Calculate document overall score
        if chapter_qualities:
            doc_overall = sum(c.score.overall for c in chapter_qualities) / len(
                chapter_qualities
            )
        else:
            doc_overall = 0

        total_time = time.time() - start_time

        # Log quality metrics
        log_quality_metrics(doc_id, doc_overall, total_word_count, total_time)

        quality_logger.info(
            f"Quality evaluation completed for {doc_id}: {doc_overall:.1f}/100, "
            f"{len(chapter_qualities)} chapters, {total_word_count} words"
        )

        return DocumentQuality(
            doc_id=doc_id,
            chapters=chapter_qualities,
            overall_score=doc_overall,
            total_word_count=total_word_count,
            genre=genre,
            language=language,
            created_at=datetime.datetime.now().isoformat(),
        )

    def to_dict(self, doc_quality: DocumentQuality) -> Dict[str, Any]:
        """Convert DocumentQuality to dictionary for JSON serialization"""
        return {
            "doc_id": doc_quality.doc_id,
            "overall_score": doc_quality.overall_score,
            "total_word_count": doc_quality.total_word_count,
            "genre": doc_quality.genre,
            "language": doc_quality.language,
            "created_at": doc_quality.created_at,
            "chapters": [
                {
                    "idx": chapter.idx,
                    "score": asdict(chapter.score),
                    "sections": [
                        {
                            "idx": section.idx,
                            "score": asdict(section.score),
                            "start_pos": section.start_pos,
                            "end_pos": section.end_pos,
                        }
                        for section in chapter.sections
                    ],
                }
                for chapter in doc_quality.chapters
            ],
        }

    def from_dict(self, data: Dict[str, Any]) -> DocumentQuality:
        """Convert dictionary to DocumentQuality"""
        chapters = []
        for chapter_data in data.get("chapters", []):
            sections = []
            for section_data in chapter_data.get("sections", []):
                section_score = QualityScore(**section_data["score"])
                section = SectionQuality(
                    idx=section_data["idx"],
                    score=section_score,
                    start_pos=section_data["start_pos"],
                    end_pos=section_data["end_pos"],
                )
                sections.append(section)

            chapter_score = QualityScore(**chapter_data["score"])
            chapter = ChapterQuality(
                idx=chapter_data["idx"], score=chapter_score, sections=sections
            )
            chapters.append(chapter)

        return DocumentQuality(
            doc_id=data["doc_id"],
            chapters=chapters,
            overall_score=data["overall_score"],
            total_word_count=data["total_word_count"],
            genre=data.get("genre", ""),
            language=data.get("language", "中文"),
            created_at=data.get("created_at", ""),
        )

    def save_quality_report(self, doc_quality: DocumentQuality, filepath: str):
        """Save quality report as JSON"""
        data = self.to_dict(doc_quality)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_quality_report(self, filepath: str) -> DocumentQuality:
        """Load quality report from JSON"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.from_dict(data)

    def generate_markdown_report(
        self, doc_quality: DocumentQuality, low_score_threshold: float = 70
    ) -> str:
        """Generate markdown quality report"""
        lines = []
        lines.append("# 小说质量评估报告")
        lines.append("")
        lines.append(f"**文档ID**: {doc_quality.doc_id}")
        lines.append(f"**生成时间**: {doc_quality.created_at}")
        lines.append(f"**小说类型**: {doc_quality.genre}")
        lines.append(f"**总字数**: {doc_quality.total_word_count:,}")
        lines.append(f"**总体评分**: {doc_quality.overall_score:.1f}/100")
        lines.append("")

        # Chapter summary
        lines.append("## 章节评分概览")
        lines.append("")
        lines.append(
            "| 章节 | 综合评分 | 可读性 | 连贯性 | 设定一致性 | 类型贴合度 | 字数 |"
        )
        lines.append(
            "|------|----------|--------|--------|------------|------------|------|"
        )

        for chapter in doc_quality.chapters:
            lines.append(
                f"| {chapter.idx} | {chapter.score.overall:.1f} | "
                f"{chapter.score.readability:.1f} | {chapter.score.coherence:.1f} | "
                f"{chapter.score.canon_consistency:.1f} | {chapter.score.genre_fit:.1f} | "
                f"{chapter.score.word_count:,} |"
            )

        lines.append("")

        # Low score sections
        lines.append("## 低分小节清单")
        lines.append("")

        low_score_sections = []
        for chapter in doc_quality.chapters:
            for section in chapter.sections:
                if section.score.overall < low_score_threshold:
                    low_score_sections.append((chapter.idx, section))

        if low_score_sections:
            lines.append(
                f"### 低于 {low_score_threshold} 分的小节（共 {len(low_score_sections)} 个）"
            )
            lines.append("")

            for chapter_idx, section in low_score_sections:
                lines.append(f"#### 第{chapter_idx}章 - 小节{section.idx}")
                lines.append(f"- **综合评分**: {section.score.overall:.1f}")
                lines.append(f"- **改进建议**: {section.score.rewrite_suggestion}")
                lines.append("")
        else:
            lines.append(f"🎉 所有小节评分均高于 {low_score_threshold} 分！")
            lines.append("")

        # Improvement suggestions
        lines.append("## 改进建议")
        lines.append("")

        # Calculate average scores by dimension
        all_readability = [
            s.score.readability
            for chapter in doc_quality.chapters
            for s in chapter.sections
        ]
        all_coherence = [
            s.score.coherence
            for chapter in doc_quality.chapters
            for s in chapter.sections
        ]
        all_canon = [
            s.score.canon_consistency
            for chapter in doc_quality.chapters
            for s in chapter.sections
        ]
        all_genre = [
            s.score.genre_fit
            for chapter in doc_quality.chapters
            for s in chapter.sections
        ]

        if all_readability:
            avg_readability = sum(all_readability) / len(all_readability)
            avg_coherence = sum(all_coherence) / len(all_coherence)
            avg_canon = sum(all_canon) / len(all_canon)
            avg_genre = sum(all_genre) / len(all_genre)

            lines.append("### 各维度平均分")
            lines.append(f"- **可读性**: {avg_readability:.1f}/100")
            lines.append(f"- **连贯性**: {avg_coherence:.1f}/100")
            lines.append(f"- **设定一致性**: {avg_canon:.1f}/100")
            lines.append(f"- **类型贴合度**: {avg_genre:.1f}/100")
            lines.append("")

            # Identify weakest areas
            dimensions = {
                "可读性": avg_readability,
                "连贯性": avg_coherence,
                "设定一致性": avg_canon,
                "类型贴合度": avg_genre,
            }
            weakest = min(dimensions, key=dimensions.get)

            lines.append(f"### 主要改进方向")
            lines.append(
                f"最需要改进的维度是：**{weakest}**（{dimensions[weakest]:.1f}分）"
            )
            lines.append("")

            if weakest == "可读性":
                lines.append("建议：")
                lines.append("- 调整句式结构，避免过长的句子")
                lines.append("- 增加段落间的逻辑连接")
                lines.append("- 优化对话和叙述的比例")
            elif weakest == "连贯性":
                lines.append("建议：")
                lines.append("- 加强段落间的过渡")
                lines.append("- 确保情节发展的逻辑性")
                lines.append("- 检查时间线和因果关系")
            elif weakest == "设定一致性":
                lines.append("建议：")
                lines.append("- 检查人物设定的一致性")
                lines.append("- 确保时间线和地点设定不冲突")
                lines.append("- 保持世界观设定的一致性")
            else:  # genre_fit
                lines.append("建议：")
                lines.append("- 增强类型特征的体现")
                lines.append("- 调整写作风格以符合类型特点")
                lines.append("- 增加该类型读者的期待元素")

        lines.append("")
        lines.append("---")
        lines.append("*此报告由 AI 小说生成器质量评估系统自动生成*")

        return "\n".join(lines)
