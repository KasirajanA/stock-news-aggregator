"""
Text summarization functionality using NLTK and TextRank.
"""
import logging
import re
from typing import Optional, List
from django.conf import settings
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class TextRankSummarizer:
    """TextRank-based summarizer for articles."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.min_sentence_length = 10
        self.max_sentences = 3
    
    def summarize_text(self, text: str) -> Optional[str]:
        """
        Generate a summary of the given text using TextRank.
        
        Args:
            text: The text to summarize
            
        Returns:
            The generated summary or None if summarization fails
        """
        if not text or len(text.strip()) < 100:
            logger.warning("Text too short for summarization")
            return text
        
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Split into sentences
            sentences = sent_tokenize(cleaned_text)
            
            if len(sentences) < 2:
                return text
            
            # Filter sentences
            filtered_sentences = [s for s in sentences if len(s.split()) >= self.min_sentence_length]
            
            if len(filtered_sentences) < 2:
                return text
            
            # Create similarity matrix
            similarity_matrix = self._create_similarity_matrix(filtered_sentences)
            
            # Calculate sentence scores using PageRank algorithm
            scores = self._calculate_scores(similarity_matrix)
            
            # Get top sentences
            top_sentences = self._get_top_sentences(filtered_sentences, scores)
            
            # Combine into summary
            summary = ' '.join(top_sentences)
            
            logger.info(f"Generated summary of {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for summarization."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def _preprocess_sentence(self, sentence: str) -> List[str]:
        """Preprocess a sentence for similarity calculation."""
        # Tokenize and lowercase
        words = word_tokenize(sentence.lower())
        
        # Remove stopwords and lemmatize
        words = [
            self.lemmatizer.lemmatize(word) 
            for word in words 
            if word.isalnum() and word not in self.stop_words
        ]
        
        return words
    
    def _create_similarity_matrix(self, sentences: List[str]) -> np.ndarray:
        """Create similarity matrix between sentences."""
        n = len(sentences)
        similarity_matrix = np.zeros((n, n))
        
        # Preprocess all sentences
        processed_sentences = [self._preprocess_sentence(s) for s in sentences]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    similarity_matrix[i][j] = self._calculate_similarity(
                        processed_sentences[i], 
                        processed_sentences[j]
                    )
        
        return similarity_matrix
    
    def _calculate_similarity(self, words1: List[str], words2: List[str]) -> float:
        """Calculate similarity between two word lists using Jaccard similarity."""
        if not words1 or not words2:
            return 0.0
        
        set1 = set(words1)
        set2 = set(words2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_scores(self, similarity_matrix: np.ndarray, damping: float = 0.85, max_iter: int = 100) -> np.ndarray:
        """Calculate sentence scores using PageRank algorithm."""
        n = len(similarity_matrix)
        scores = np.ones(n) / n
        
        for _ in range(max_iter):
            new_scores = (1 - damping) / n + damping * (similarity_matrix.T @ scores)
            
            if np.allclose(scores, new_scores):
                break
                
            scores = new_scores
        
        return scores
    
    def _get_top_sentences(self, sentences: List[str], scores: np.ndarray) -> List[str]:
        """Get top sentences based on scores."""
        # Get indices of top sentences
        top_indices = np.argsort(scores)[-self.max_sentences:]
        
        # Sort by original order
        top_indices = sorted(top_indices)
        
        return [sentences[i] for i in top_indices]
    
    def get_summary_stats(self, original_text: str, summary: str) -> dict:
        """Get statistics about the summarization."""
        if not summary:
            return {}
        
        original_length = len(original_text.split())
        summary_length = len(summary.split())
        compression_ratio = (original_length - summary_length) / original_length * 100
        
        return {
            'original_length': original_length,
            'summary_length': summary_length,
            'compression_ratio': round(compression_ratio, 2),
            'model_used': 'TextRank (NLTK)'
        }


# Global summarizer instance
_summarizer_instance = None


def get_summarizer() -> TextRankSummarizer:
    """Get the global summarizer instance."""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = TextRankSummarizer()
    return _summarizer_instance


def summarize_article_text(text: str) -> Optional[str]:
    """
    Convenience function to summarize article text.
    
    Args:
        text: The article text to summarize
        
    Returns:
        The generated summary or None if summarization fails
    """
    summarizer = get_summarizer()
    return summarizer.summarize_text(text)


def get_summary_with_stats(text: str) -> dict:
    """
    Get summary with statistics.
    
    Args:
        text: The article text to summarize
        
    Returns:
        Dictionary with summary and statistics
    """
    summarizer = get_summarizer()
    summary = summarizer.summarize_text(text)
    
    if summary:
        stats = summarizer.get_summary_stats(text, summary)
        return {
            'summary': summary,
            'stats': stats,
            'success': True
        }
    else:
        return {
            'summary': None,
            'stats': {},
            'success': False,
            'error': 'Failed to generate summary'
        } 