package services

import (
	"log"
	"math/rand"
	"sort"
	"time"
	"stock-news-aggregator/internal/database"
	"stock-news-aggregator/internal/models"
)

func FetchAllNews() ([]models.Article, error) {
	// This function will now fetch from the database instead of scraping directly
	articles, _, err := database.GetArticles(1, 1000, "") // Large page size to get all articles
	if err != nil {
		return nil, err
	}

	// Convert database.Article to models.Article
	var modelArticles []models.Article
	for _, article := range articles {
		modelArticles = append(modelArticles, models.Article{
			Title:       article.Title,
			URL:         article.URL,
			Source:      models.Source{Name: article.Source},
			Content:     article.Content,
			PublishedAt: article.PublishedAt,
		})
	}

	return modelArticles, nil
}

func GetNewsFromDB(page, pageSize int, search string) ([]models.Article, int, error) {
	// Get a larger set of articles to allow for shuffling
	multiplier := 3 // Get 3x the requested page size to ensure good distribution
	articles, totalCount, err := database.GetArticles(page, pageSize*multiplier, search)
	if err != nil {
		return nil, 0, err
	}

	// Group articles by source
	sourceGroups := make(map[string][]database.Article)
	sources := make([]string, 0)
	for _, article := range articles {
		if _, exists := sourceGroups[article.Source]; !exists {
			sources = append(sources, article.Source)
		}
		sourceGroups[article.Source] = append(sourceGroups[article.Source], article)
	}

	// Sort sources to ensure consistent ordering
	sort.Strings(sources)

	// Initialize random number generator with current time
	rnd := rand.New(rand.NewSource(time.Now().UnixNano()))

	// Shuffle articles within each source group
	for _, articles := range sourceGroups {
		rnd.Shuffle(len(articles), func(i, j int) {
			articles[i], articles[j] = articles[j], articles[i]
		})
	}

	// Create a balanced selection of articles from different sources
	var selectedArticles []database.Article
	sourceIndex := 0
	for len(selectedArticles) < pageSize && len(selectedArticles) < len(articles) {
		source := sources[sourceIndex%len(sources)]
		if articles := sourceGroups[source]; len(articles) > 0 {
			selectedArticles = append(selectedArticles, articles[0])
			sourceGroups[source] = articles[1:] // Remove the selected article
		}
		sourceIndex++
	}

	// Convert database.Article to models.Article
	var modelArticles []models.Article
	for _, article := range selectedArticles {
		modelArticles = append(modelArticles, models.Article{
			Title:       article.Title,
			URL:         article.URL,
			Source:      models.Source{Name: article.Source},
			Content:     article.Content,
			Description: article.Description,
			PublishedAt: article.PublishedAt,
		})
	}

	return modelArticles, totalCount, nil
}

// ScrapeAndStoreNews performs the scraping of news articles and stores them in the database
func ScrapeAndStoreNews() error {
	log.Println("Starting news scraping from all sources...")

	// Create channels for concurrent scraping
	livemintChan := make(chan []models.Article)
	etChan := make(chan []models.Article)
	mcChan := make(chan []models.Article)
	growwChan := make(chan []models.Article)
	bsChan := make(chan []models.Article)
	indiaTodayChan := make(chan []models.Article)
	errorChan := make(chan error)

	// Scrape from all sources concurrently
	go func() {
		log.Println("Starting Livemint scraping...")
		articles, err := ScrapeLivemint()
		if err != nil {
			log.Printf("Error scraping Livemint: %v\n", err)
			errorChan <- err
			livemintChan <- nil
			return
		}
		livemintChan <- articles
	}()

	go func() {
		log.Println("Starting Economic Times scraping...")
		articles, err := ScrapeEconomicTimes()
		if err != nil {
			log.Printf("Error scraping Economic Times: %v\n", err)
			errorChan <- err
			etChan <- nil
			return
		}
		etChan <- articles
	}()

	go func() {
		log.Println("Starting MoneyControl scraping...")
		articles, err := ScrapeMoneyControl()
		if err != nil {
			log.Printf("Error scraping MoneyControl: %v\n", err)
			errorChan <- err
			mcChan <- nil
			return
		}
		mcChan <- articles
	}()

	go func() {
		log.Println("Starting Groww scraping...")
		articles, err := ScrapeGroww()
		if err != nil {
			log.Printf("Error scraping Groww: %v\n", err)
			errorChan <- err
			growwChan <- nil
			return
		}
		growwChan <- articles
	}()

	go func() {
		log.Println("Starting Business Standard scraping...")
		articles, err := ScrapeBusinessStandard()
		if err != nil {
			log.Printf("Error scraping Business Standard: %v\n", err)
			errorChan <- err
			bsChan <- nil
			return
		}
		bsChan <- articles
	}()

	go func() {
		log.Println("Starting India Today scraping...")
		articles, err := ScrapeIndiaToday()
		if err != nil {
			log.Printf("Error scraping India Today: %v\n", err)
			errorChan <- err
			indiaTodayChan <- nil
			return
		}
		indiaTodayChan <- articles
	}()

	// Collect results
	livemintArticles := <-livemintChan
	etArticles := <-etChan
	mcArticles := <-mcChan
	growwArticles := <-growwChan
	bsArticles := <-bsChan
	indiaTodayArticles := <-indiaTodayChan

	// Store all articles in the database
	var totalStored int
	var totalSkipped int

	storeArticles := func(articles []models.Article, source string) {
		if articles == nil {
			return
		}
		for _, article := range articles {
			exists, err := database.IsArticleScraped(article.URL)
			if err != nil {
				log.Printf("Error checking article existence from %s: %v", source, err)
				continue
			}

			if !exists {
				err = database.InsertArticle(
					article.Title,
					article.URL,
					article.Source.Name,
					article.Content,
					article.Description,
					article.PublishedAt,
				)
				if err != nil {
					log.Printf("Error storing article from %s: %v", source, err)
				} else {
					totalStored++
					log.Printf("Stored new article from %s: %s", source, article.Title)
				}
			} else {
				totalSkipped++
			}
		}
	}

	// Store articles from each source
	storeArticles(livemintArticles, "Livemint")
	storeArticles(etArticles, "Economic Times")
	storeArticles(mcArticles, "MoneyControl")
	storeArticles(growwArticles, "Groww")
	storeArticles(bsArticles, "Business Standard")
	storeArticles(indiaTodayArticles, "India Today")

	log.Printf("Scraping completed. Total articles stored: %d, skipped (already exists): %d", totalStored, totalSkipped)
	return nil
} 