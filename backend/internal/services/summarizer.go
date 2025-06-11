package services

import (
	"fmt"
	"net/http"
	"strings"
	"unicode"

	"github.com/PuerkitoBio/goquery"
)

// TextSummarizer provides text summarization functionality
type TextSummarizer struct {
	maxSentences int
}

// NewTextSummarizer creates a new instance of TextSummarizer
func NewTextSummarizer(maxSentences int) *TextSummarizer {
	if maxSentences <= 0 {
		maxSentences = 5 // default value
	}
	return &TextSummarizer{maxSentences: maxSentences}
}

// SummarizeURL fetches content from a URL and summarizes it
func (ts *TextSummarizer) SummarizeURL(url string) (string, error) {
	// Fetch the webpage content
	resp, err := http.Get(url)
	if err != nil {
		return "", fmt.Errorf("failed to fetch URL: %v", err)
	}
	defer resp.Body.Close()

	// Parse the HTML content
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to parse HTML: %v", err)
	}

	// Extract main article text
	var articleText strings.Builder
	doc.Find("p").Each(func(i int, s *goquery.Selection) {
		articleText.WriteString(s.Text())
		articleText.WriteString(" ")
	})

	// Summarize the extracted text
	return ts.Summarize(articleText.String())
}

// Summarize generates a summary of the given text
func (ts *TextSummarizer) Summarize(text string) (string, error) {
	if text == "" {
		return "", fmt.Errorf("empty text provided")
	}

	// Split text into sentences
	sentences := splitIntoSentences(text)
	if len(sentences) == 0 {
		return "", fmt.Errorf("no sentences found in text")
	}

	// If text is already short enough, return as is
	if len(sentences) <= ts.maxSentences {
		return strings.Join(sentences, " "), nil
	}

	// Simple extractive summarization:
	// 1. Keep the first sentence (usually contains important context)
	// 2. Score remaining sentences based on word importance
	// 3. Select top N-1 sentences
	
	summary := []string{sentences[0]}
	
	// Score and select remaining sentences
	type scoredSentence struct {
		sentence string
		score    float64
	}
	
	scored := make([]scoredSentence, len(sentences)-1)
	for i, sent := range sentences[1:] {
		scored[i] = scoredSentence{
			sentence: sent,
			score:    scoreSentence(sent, text),
		}
	}

	// Sort sentences by score (descending)
	for i := 0; i < len(scored)-1; i++ {
		for j := i + 1; j < len(scored); j++ {
			if scored[j].score > scored[i].score {
				scored[i], scored[j] = scored[j], scored[i]
			}
		}
	}

	// Add top N-1 sentences to summary
	for i := 0; i < ts.maxSentences-1 && i < len(scored); i++ {
		summary = append(summary, scored[i].sentence)
	}

	return strings.Join(summary, " "), nil
}

// Helper function to split text into sentences
func splitIntoSentences(text string) []string {
	// Basic sentence splitting - can be improved
	text = strings.TrimSpace(text)
	sentences := strings.FieldsFunc(text, func(r rune) bool {
		return r == '.' || r == '!' || r == '?'
	})

	// Clean up sentences
	var result []string
	for _, s := range sentences {
		s = strings.TrimSpace(s)
		if s != "" {
			result = append(result, s+".")
		}
	}
	return result
}

// Helper function to score a sentence based on word importance
func scoreSentence(sentence, fullText string) float64 {
	words := strings.FieldsFunc(sentence, unicode.IsSpace)
	if len(words) == 0 {
		return 0
	}

	// Simple scoring based on word frequency in full text
	wordFreq := make(map[string]int)
	for _, word := range strings.FieldsFunc(fullText, unicode.IsSpace) {
		word = strings.ToLower(strings.Trim(word, ".,!?\"'()[]{}"))
		if word != "" {
			wordFreq[word]++
		}
	}

	// Calculate score based on average word importance
	var score float64
	for _, word := range words {
		word = strings.ToLower(strings.Trim(word, ".,!?\"'()[]{}"))
		if word != "" {
			score += float64(wordFreq[word])
		}
	}

	return score / float64(len(words))
} 