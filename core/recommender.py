"""Recommender — Рекомендательный движок.

Подбирает Skills и MCP-серверы на основе контекста задачи.
MVP-версия: keyword-matching. v2.0: семантический поиск через embeddings.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Путь к каталогам
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_catalog(filename: str) -> list[dict]:
    """Загрузить каталог из JSON-файла."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        logger.warning("Catalog file not found: %s", filepath)
        return []
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


class Recommender:
    """Движок рекомендаций Skills и MCP на основе контекста задачи."""

    def __init__(self) -> None:
        self._skills: list[dict] = _load_catalog("skills_catalog.json")
        self._mcps: list[dict] = _load_catalog("mcp_catalog.json")
        logger.info(
            "Recommender loaded: %d skills, %d MCPs",
            len(self._skills),
            len(self._mcps),
        )

    def recommend(
        self,
        category: str,
        subcategory: str,
        task_type: str,
        summary: str = "",
        max_skills: int = 5,
        max_mcps: int = 3,
    ) -> tuple[list[dict], list[dict]]:
        """Подобрать релевантные Skills и MCP.

        Args:
            category: Выбранная категория (dev, marketing, ...).
            subcategory: Подкатегория (backend, frontend, ...).
            task_type: Тип задачи (write, debug, ...).
            summary: Текстовое описание задачи от AI.
            max_skills: Максимум Skills в выдаче.
            max_mcps: Максимум MCP в выдаче.

        Returns:
            Кортеж (список Skills, список MCP).
        """
        search_tokens = self._build_search_tokens(
            category, subcategory, task_type, summary
        )

        scored_skills = self._score_items(self._skills, search_tokens)
        scored_mcps = self._score_items(self._mcps, search_tokens)

        top_skills = sorted(scored_skills, key=lambda x: x[1], reverse=True)[:max_skills]
        top_mcps = sorted(scored_mcps, key=lambda x: x[1], reverse=True)[:max_mcps]

        # Фильтруем items с нулевым скором
        result_skills = [item for item, score in top_skills if score > 0]
        result_mcps = [item for item, score in top_mcps if score > 0]

        logger.info(
            "Recommendations: %d skills, %d MCPs for [%s/%s/%s]",
            len(result_skills),
            len(result_mcps),
            category,
            subcategory,
            task_type,
        )

        return result_skills, result_mcps

    @staticmethod
    def _build_search_tokens(
        category: str,
        subcategory: str,
        task_type: str,
        summary: str,
    ) -> set[str]:
        """Собрать множество поисковых токенов."""
        tokens = {category.lower(), subcategory.lower(), task_type.lower()}
        if summary:
            # Разбиваем summary на слова, убираем короткие
            words = summary.lower().replace(",", " ").replace(".", " ").split()
            tokens.update(w for w in words if len(w) > 2)
        return tokens

    @staticmethod
    def _score_items(items: list[dict], tokens: set[str]) -> list[tuple[dict, int]]:
        """Посчитать score для каждого элемента каталога."""
        results = []
        for item in items:
            score = 0
            item_tags = {t.lower() for t in item.get("tags", [])}
            item_cats = {item.get("category", "").lower(), item.get("subcategory", "").lower()}
            item_keywords = {k.lower() for k in item.get("relevance_keywords", [])}

            # Совпадение по категории (высокий вес)
            score += len(tokens & item_cats) * 3
            # Совпадение по тегам (средний вес)
            score += len(tokens & item_tags) * 2
            # Совпадение по keywords (средний вес)
            score += len(tokens & item_keywords) * 2
            # Бонус за высокий приоритет
            if item.get("priority") == "high":
                score += 1

            results.append((item, score))
        return results
