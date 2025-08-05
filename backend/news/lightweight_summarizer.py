"""
Lightweight text summarization using TextBlob (no heavy dependencies).
"""
import logging
import re
from typing import Optional, List
from django.conf import settings
from textblob import TextBlob
from collections import Counter

logger = logging.getLogger(__name__)


class LightweightSummarizer:
    """Lightweight summarizer using TextBlob and frequency-based approach."""
    
    def __init__(self):
        # Common English stop words (built-in, no external dependency)
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'i', 'you', 'your', 'they', 'have',
            'had', 'this', 'but', 'not', 'or', 'what', 'said', 'each', 'which',
            'she', 'do', 'how', 'their', 'if', 'up', 'out', 'many', 'then',
            'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like',
            'into', 'him', 'time', 'two', 'more', 'go', 'no', 'way', 'could',
            'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now',
            'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made',
            'may', 'part', 'over', 'new', 'sound', 'take', 'only', 'little',
            'work', 'know', 'place', 'year', 'live', 'me', 'back', 'give',
            'most', 'very', 'after', 'thing', 'our', 'just', 'name', 'good',
            'sentence', 'man', 'think', 'say', 'great', 'where', 'help',
            'through', 'much', 'before', 'line', 'right', 'too', 'mean',
            'old', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want',
            'show', 'also', 'around', 'form', 'three', 'small', 'set',
            'put', 'end', 'does', 'another', 'well', 'large', 'must',
            'big', 'even', 'such', 'here', 'why', 'ask', 'went', 'men',
            'read', 'need', 'land', 'different', 'home', 'us', 'move',
            'try', 'kind', 'hand', 'picture', 'again', 'change', 'off',
            'play', 'spell', 'air', 'away', 'animal', 'house', 'page',
            'letter', 'mother', 'answer', 'found', 'study', 'still',
            'learn', 'should', 'America', 'world', 'high', 'every',
            'near', 'add', 'food', 'between', 'own', 'below', 'country',
            'plant', 'last', 'school', 'father', 'keep', 'tree', 'never',
            'start', 'city', 'earth', 'eye', 'light', 'thought', 'head',
            'under', 'story', 'saw', 'left', 'don\'t', 'few', 'while',
            'along', 'might', 'close', 'something', 'seem', 'next',
            'hard', 'open', 'example', 'begin', 'life', 'always',
            'those', 'both', 'paper', 'together', 'got', 'group',
            'often', 'run', 'important', 'until', 'children', 'side',
            'feet', 'car', 'mile', 'night', 'walk', 'white', 'sea',
            'began', 'grow', 'took', 'river', 'four', 'carry',
            'state', 'once', 'book', 'hear', 'stop', 'without',
            'second', 'late', 'miss', 'idea', 'enough', 'eat',
            'face', 'watch', 'far', 'Indian', 'real', 'almost',
            'let', 'above', 'girl', 'sometimes', 'mountain', 'cut',
            'young', 'talk', 'soon', 'list', 'song', 'being',
            'leave', 'family', 'it\'s', 'body', 'music', 'color',
            'stand', 'sun', 'questions', 'fish', 'area', 'mark',
            'dog', 'horse', 'birds', 'problem', 'complete', 'room',
            'knew', 'since', 'ever', 'piece', 'told', 'usually',
            'didn\'t', 'friends', 'easy', 'heard', 'order', 'red',
            'door', 'sure', 'become', 'top', 'ship', 'across',
            'today', 'during', 'short', 'better', 'best', 'however',
            'low', 'hours', 'black', 'products', 'happened',
            'whole', 'measure', 'remember', 'early', 'waves',
            'reached', 'listen', 'wind', 'rock', 'space', 'covered',
            'fast', 'several', 'hold', 'himself', 'toward',
            'five', 'step', 'morning', 'passed', 'vowel',
            'true', 'hundred', 'against', 'pattern', 'numeral',
            'table', 'north', 'slowly', 'money', 'map', 'farm',
            'pulled', 'draw', 'voice', 'seen', 'cold', 'cried',
            'plan', 'notice', 'south', 'sing', 'war', 'ground',
            'fall', 'king', 'town', 'I\'ll', 'unit', 'figure',
            'certain', 'field', 'travel', 'wood', 'fire', 'upon'
        }
        self.min_sentence_length = 10
        self.max_sentences = 3
    
    def summarize_text(self, text: str) -> Optional[str]:
        """
        Generate a summary using TextBlob and frequency-based approach.
        
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
            
            # Use TextBlob for sentence tokenization
            blob = TextBlob(cleaned_text)
            sentences = [str(sentence) for sentence in blob.sentences]
            
            if len(sentences) < 2:
                return text
            
            # Filter sentences
            filtered_sentences = [s for s in sentences if len(s.split()) >= self.min_sentence_length]
            
            if len(filtered_sentences) < 2:
                return text
            
            # Calculate word frequencies
            word_frequencies = self._calculate_word_frequencies(filtered_sentences)
            
            # Calculate sentence scores
            sentence_scores = self._calculate_sentence_scores(filtered_sentences, word_frequencies)
            
            # Get top sentences
            top_sentences = self._get_top_sentences(filtered_sentences, sentence_scores)
            
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
    
    def _calculate_word_frequencies(self, sentences: List[str]) -> dict:
        """Calculate word frequencies across all sentences."""
        word_freq = Counter()
        
        for sentence in sentences:
            # Use TextBlob for word tokenization
            blob = TextBlob(sentence.lower())
            words = [word for word in blob.words if word.isalpha() and word not in self.stop_words]
            word_freq.update(words)
        
        return dict(word_freq)
    
    def _calculate_sentence_scores(self, sentences: List[str], word_frequencies: dict) -> List[float]:
        """Calculate sentence scores based on word frequencies."""
        sentence_scores = []
        
        for sentence in sentences:
            # Use TextBlob for word tokenization
            blob = TextBlob(sentence.lower())
            words = [word for word in blob.words if word.isalpha() and word not in self.stop_words]
            
            # Calculate score based on word frequencies
            if words:
                score = sum(word_frequencies.get(word, 0) for word in words) / len(words)
            else:
                score = 0.0
            
            sentence_scores.append(score)
        
        return sentence_scores
    
    def _get_top_sentences(self, sentences: List[str], scores: List[float]) -> List[str]:
        """Get top sentences based on scores."""
        # Create list of (score, index, sentence) tuples
        scored_sentences = [(score, i, sentence) for i, (score, sentence) in enumerate(zip(scores, sentences))]
        
        # Sort by score (descending)
        scored_sentences.sort(reverse=True)
        
        # Get top sentences
        top_sentences = scored_sentences[:self.max_sentences]
        
        # Sort by original order
        top_sentences.sort(key=lambda x: x[1])
        
        return [sentence for _, _, sentence in top_sentences]
    
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
            'model_used': 'TextBlob (Lightweight)'
        }


# Global summarizer instance
_lightweight_summarizer_instance = None


def get_lightweight_summarizer() -> LightweightSummarizer:
    """Get the global lightweight summarizer instance."""
    global _lightweight_summarizer_instance
    if _lightweight_summarizer_instance is None:
        _lightweight_summarizer_instance = LightweightSummarizer()
    return _lightweight_summarizer_instance


def summarize_article_text_lightweight(text: str) -> Optional[str]:
    """
    Convenience function to summarize article text using lightweight approach.
    
    Args:
        text: The article text to summarize
        
    Returns:
        The generated summary or None if summarization fails
    """
    summarizer = get_lightweight_summarizer()
    return summarizer.summarize_text(text)


def get_summary_with_stats_lightweight(text: str) -> dict:
    """
    Get summary with statistics using lightweight approach.
    
    Args:
        text: The article text to summarize
        
    Returns:
        Dictionary with summary and statistics
    """
    summarizer = get_lightweight_summarizer()
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