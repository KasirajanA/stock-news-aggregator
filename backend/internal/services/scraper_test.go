package services

import (
	"testing"
	"stock-news-aggregator/internal/models"
)

func validateArticles(t *testing.T, articles []models.Article, source string) {
	if len(articles) == 0 {
		t.Errorf("No articles found from %s", source)
		return
	}

	t.Logf("Successfully scraped %d articles from %s", len(articles), source)
	
	// Log the first article as a sample
	if len(articles) > 0 {
		sample := articles[0]
		t.Logf("Sample article from %s:", source)
		t.Logf("  Title: %s", sample.Title)
		t.Logf("  URL: %s", sample.URL)
		t.Logf("  Description: %s", sample.Description)
		t.Logf("  Image URL: %s", sample.ImageURL)
	}
}

func TestScrapers(t *testing.T) {
	t.Run("Livemint", func(t *testing.T) {
		articles, err := ScrapeLivemint()
		if err != nil {
			t.Errorf("Error scraping Livemint: %v", err)
			return
		}
		validateArticles(t, articles, "Livemint")
	})

	t.Run("Economic Times", func(t *testing.T) {
		articles, err := ScrapeEconomicTimes()
		if err != nil {
			t.Errorf("Error scraping Economic Times: %v", err)
			return
		}
		validateArticles(t, articles, "Economic Times")
	})

	t.Run("MoneyControl", func(t *testing.T) {
		articles, err := ScrapeMoneyControl()
		if err != nil {
			t.Errorf("Error scraping MoneyControl: %v", err)
			return
		}
		validateArticles(t, articles, "MoneyControl")
	})

	t.Run("Groww", func(t *testing.T) {
		articles, err := ScrapeGroww()
		if err != nil {
			t.Errorf("Error scraping Groww: %v", err)
			return
		}
		validateArticles(t, articles, "Groww")
	})

	t.Run("Business Standard", func(t *testing.T) {
		articles, err := ScrapeBusinessStandard()
		if err != nil {
			t.Errorf("Error scraping Business Standard: %v", err)
			return
		}
		validateArticles(t, articles, "Business Standard")
	})

	t.Run("India Today", func(t *testing.T) {
		articles, err := ScrapeIndiaToday()
		if err != nil {
			t.Errorf("Error scraping India Today: %v", err)
			return
		}
		validateArticles(t, articles, "India Today")
	})
}