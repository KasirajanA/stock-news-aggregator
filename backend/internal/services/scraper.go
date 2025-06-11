package services

import (
	"fmt"
	"log"
	"math/rand"
	"strings"
	"time"

	"github.com/gocolly/colly/v2"
	"stock-news-aggregator/internal/models"
)

func ScrapeLivemint() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("www.livemint.com", "livemint.com"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Visiting %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Error scraping %s: %s\n", r.Request.URL, err)
	})

	c.OnHTML("div.listingNew", func(e *colly.HTMLElement) {
		e.ForEach("div.listtostory", func(_ int, el *colly.HTMLElement) {
		article := models.Article{
				Title: strings.TrimSpace(el.ChildText("h2")),
				Description: strings.TrimSpace(el.ChildText("p")),
				URL: el.ChildAttr("a", "href"),
			Source: models.Source{
				Name: "Livemint",
			},
			PublishedAt: time.Now(),
		}

			// Make URL absolute if it's relative
			if !strings.HasPrefix(article.URL, "http") {
				article.URL = "https://www.livemint.com" + article.URL
			}

			// Get image URL
			imageURL := el.ChildAttr("img", "src")
			if imageURL != "" {
				article.ImageURL = imageURL
			}

			if article.Title != "" {
		articles = append(articles, article)
				log.Printf("Found Livemint article: %s\n", article.Title)
			}
		})
	})

	// Visit multiple pages (up to 5 pages)
	baseURL := "https://www.livemint.com/market/stock-market-news"
	for page := 1; page <= 5; page++ {
		pageURL := baseURL
		if page > 1 {
			pageURL = fmt.Sprintf("%s/page-%d", baseURL, page)
		}
		
		err := c.Visit(pageURL)
	if err != nil {
			log.Printf("Error visiting Livemint page %d: %v", page, err)
			break // Stop if we can't access the next page
		}
		
		// Add a small delay between page visits to be polite
		time.Sleep(1 * time.Second)
	}

	log.Printf("Found %d articles from Livemint\n", len(articles))
	return articles, nil
}

func ScrapeEconomicTimes() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("economictimes.indiatimes.com"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Visiting %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Error scraping %s: %s\n", r.Request.URL, err)
	})

	c.OnHTML("div.eachStory", func(e *colly.HTMLElement) {
		article := models.Article{
			Title: strings.TrimSpace(e.ChildText("h3")),
			Description: strings.TrimSpace(e.ChildText("p")),
			URL: "https://economictimes.indiatimes.com" + e.ChildAttr("a", "href"),
			Source: models.Source{
				Name: "Economic Times",
			},
			PublishedAt: time.Now(),
		}

		// Get image URL if available
		imageURL := e.ChildAttr("img", "src")
		if imageURL != "" {
			article.ImageURL = imageURL
		}

		if article.Title != "" {
			articles = append(articles, article)
			log.Printf("Found Economic Times article: %s\n", article.Title)
		}
	})

	// Visit multiple pages (up to 5 pages)
	baseURL := "https://economictimes.indiatimes.com/markets/stocks/news"
	for page := 1; page <= 5; page++ {
		pageURL := baseURL
		if page > 1 {
			pageURL = fmt.Sprintf("%s/%d", baseURL, page)
		}
		
		err := c.Visit(pageURL)
		if err != nil {
			log.Printf("Error visiting Economic Times page %d: %v", page, err)
			break // Stop if we can't access the next page
		}
		
		// Add a small delay between page visits to be polite
		time.Sleep(1 * time.Second)
	}

	log.Printf("Found %d articles from Economic Times\n", len(articles))
	return articles, nil
}

func ScrapeBusinessToday() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("www.businesstoday.in", "businesstoday.in"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Business Today - Visiting URL: %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Business Today - Error scraping %s: %s\n", r.Request.URL, err)
		log.Printf("Business Today - Response status: %d\n", r.StatusCode)
		log.Printf("Business Today - Response headers: %v\n", r.Headers)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Printf("Business Today - Got response from %s: %d bytes\n", r.Request.URL, len(r.Body))
	})

	c.OnHTML(".BT_story_tab, .BT_story_listing", func(e *colly.HTMLElement) {
		log.Printf("Business Today - Found potential article container with classes: %s\n", e.Attr("class"))
		
		// Try multiple selectors for title
		title := e.ChildText(".BT_story_title, .BT_story_heading")
		if title == "" {
			title = e.ChildText("h1, h2, h3")
		}
		log.Printf("Business Today - Found title: %s\n", title)

		// Try multiple selectors for link
		link := e.ChildAttr("a", "href")
		if link == "" {
			link = e.ChildAttr(".BT_story_title a, .BT_story_heading a", "href")
		}
		log.Printf("Business Today - Found link: %s\n", link)

		// Try multiple selectors for description
		description := e.ChildText(".BT_story_desc, .BT_story_summary")
		log.Printf("Business Today - Found description: %s\n", description)

		// Try multiple selectors for image
		imageURL := e.ChildAttr("img", "data-src")
		if imageURL == "" {
			imageURL = e.ChildAttr("img", "src")
		}
		log.Printf("Business Today - Found image URL: %s\n", imageURL)

		// Skip if no title or link
		if title == "" || link == "" {
			log.Printf("Business Today - Skipping article due to missing title or link\n")
			return
		}

		// Ensure link is absolute
		if !strings.HasPrefix(link, "http") {
			link = "https://www.businesstoday.in" + link
		}

		// Only include stock market related articles
		if !strings.Contains(strings.ToLower(title), "stock") &&
			!strings.Contains(strings.ToLower(title), "market") &&
			!strings.Contains(strings.ToLower(title), "sensex") &&
			!strings.Contains(strings.ToLower(title), "nifty") &&
			!strings.Contains(strings.ToLower(link), "markets/") &&
			!strings.Contains(strings.ToLower(link), "stocks/") {
			log.Printf("Business Today - Skipping non-stock market article: %s\n", title)
			return
		}

		articles = append(articles, models.Article{
			Title:       title,
			URL:         link,
			Description: description,
			ImageURL:    imageURL,
			Source: models.Source{
				Name: "Business Today",
			},
			PublishedAt: time.Now(),
		})

		log.Printf("Business Today - Successfully added article: %s\n", title)
	})

	// Visit both the stocks and markets pages
	err := c.Visit("https://www.businesstoday.in/markets/stocks")
	if err != nil {
		log.Printf("Business Today - Error visiting stocks page: %s\n", err)
	}

	err = c.Visit("https://www.businesstoday.in/markets")
	if err != nil {
		log.Printf("Business Today - Error visiting markets page: %s\n", err)
	}

	if len(articles) == 0 {
		return nil, fmt.Errorf("no articles found from Business Today")
	}

	return articles, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func ScrapeMoneyControl() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("www.moneycontrol.com", "moneycontrol.com"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("MoneyControl - Visiting URL: %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("MoneyControl - Error scraping %s: %s\n", r.Request.URL, err)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Printf("MoneyControl - Got response from %s: %d bytes\n", r.Request.URL, len(r.Body))
	})

	c.OnHTML("li.clearfix", func(e *colly.HTMLElement) {
		log.Printf("MoneyControl - Found article element\n")
		
		title := strings.TrimSpace(e.ChildText("h2"))
		if title == "" {
			title = strings.TrimSpace(e.ChildText("h3"))
		}
		
		url := e.ChildAttr("a", "href")
		description := strings.TrimSpace(e.ChildText("p"))

		log.Printf("MoneyControl - Raw data - Title: %s, URL: %s\n", title, url)

		if title == "" || url == "" {
			log.Printf("MoneyControl - Skipping article due to missing title or URL\n")
			return
		}

		// Skip non-stock market articles
		if !strings.Contains(strings.ToLower(url), "markets") && 
		   !strings.Contains(strings.ToLower(url), "stocks") {
			log.Printf("MoneyControl - Skipping non-stock market article: %s\n", title)
			return
		}

		article := models.Article{
			Title: title,
			Description: description,
			URL: url,
			Source: models.Source{
				Name: "MoneyControl",
			},
			PublishedAt: time.Now(),
		}

		// Make URL absolute if it's relative
		if !strings.HasPrefix(article.URL, "http") {
			article.URL = "https://www.moneycontrol.com" + article.URL
		}

		// Get image URL
		imageURL := e.ChildAttr("img", "data-src")
		if imageURL == "" {
			imageURL = e.ChildAttr("img", "src")
		}
		if imageURL != "" {
			article.ImageURL = imageURL
		}

		articles = append(articles, article)
		log.Printf("MoneyControl - Successfully added article: %s\n", article.Title)
	})

	// Visit multiple pages for both markets and stocks sections
	sections := []string{
		"https://www.moneycontrol.com/news/business/markets/",
		"https://www.moneycontrol.com/news/business/stocks/",
	}

	for _, baseURL := range sections {
		for page := 1; page <= 5; page++ {
			pageURL := baseURL
			if page > 1 {
				pageURL = fmt.Sprintf("%spage-%d.html", baseURL, page)
			}
			
			err := c.Visit(pageURL)
			if err != nil {
				log.Printf("MoneyControl - Error visiting page %d of %s: %v", page, baseURL, err)
				break // Stop if we can't access the next page
			}
			
			// Add a small delay between page visits to be polite
			time.Sleep(1 * time.Second)
		}
	}

	log.Printf("Found %d articles from MoneyControl\n", len(articles))
	return articles, nil
}

// shuffleArticles randomly shuffles the array of articles
func shuffleArticles(articles []models.Article) {
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(articles), func(i, j int) {
		articles[i], articles[j] = articles[j], articles[i]
	})
}

func ScrapeGroww() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("groww.in"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Groww - Visiting URL: %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Groww - Error scraping %s: %s\n", r.Request.URL, err)
		log.Printf("Groww - Response status: %d\n", r.StatusCode)
		log.Printf("Groww - Response headers: %v\n", r.Headers)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Printf("Groww - Got response from %s: %d bytes\n", r.Request.URL, len(r.Body))
		log.Printf("Groww - Response body: %s\n", string(r.Body))
	})

	c.OnHTML("div.newsCard, div.news-card, div.news-item", func(e *colly.HTMLElement) {
		log.Printf("Groww - Found article element\n")
		
		title := e.ChildText("h1, h2, h3, h4, .title, [class*='title']")
		link := e.ChildAttr("a", "href")
		description := e.ChildText("p, .description, [class*='description']")
		imageURL := e.ChildAttr("img", "src")

		log.Printf("Groww - Raw data - Title: %s, URL: %s\n", title, link)

		if title != "" && link != "" {
			if !strings.HasPrefix(link, "http") {
				link = "https://groww.in" + link
			}

			articles = append(articles, models.Article{
				Title:       title,
				URL:        link,
				Source:     models.Source{Name: "Groww"},
				ImageURL:   imageURL,
				Description: description,
			})
			log.Printf("Groww - Successfully added article: %s\n", title)
		}
	})

	err := c.Visit("https://groww.in/market-news/stocks")
	if err != nil {
		return nil, fmt.Errorf("error visiting Groww: %v", err)
	}

	log.Printf("Groww - Found %d articles\n", len(articles))
	return articles, nil
}

func ScrapeBusinessStandard() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("www.business-standard.com", "business-standard.com"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Business Standard - Visiting URL: %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Business Standard - Error scraping %s: %s\n", r.Request.URL, err)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Printf("Business Standard - Got response from %s: %d bytes\n", r.Request.URL, len(r.Body))
	})

	c.OnHTML("div[class*='article'], div[class*='listing'], .story-box", func(e *colly.HTMLElement) {
		title := e.ChildText("h1, h2, h3, h4, .title, [class*='title']")
		link := e.ChildAttr("a", "href")
		description := e.ChildText("p, .description, [class*='description'], .story-excerpt")
		imageURL := e.ChildAttr("img", "src")

		if title != "" && link != "" {
			if !strings.HasPrefix(link, "http") {
				link = "https://www.business-standard.com" + link
			}

			articles = append(articles, models.Article{
				Title:       title,
				URL:        link,
				Source:     models.Source{Name: "Business Standard"},
				ImageURL:   imageURL,
				Description: description,
			})
		}
	})

	err := c.Visit("https://www.business-standard.com/markets/news")
	if err != nil {
		return nil, fmt.Errorf("error visiting Business Standard: %v", err)
	}

	log.Printf("Business Standard - Found %d articles\n", len(articles))
	return articles, nil
}

func ScrapeIndiaToday() ([]models.Article, error) {
	var articles []models.Article
	c := colly.NewCollector(
		colly.AllowedDomains("www.indiatoday.in", "indiatoday.in"),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
	)

	// Debug logging
	c.OnRequest(func(r *colly.Request) {
		log.Printf("India Today - Visiting URL: %s\n", r.URL.String())
	})

	c.OnError(func(r *colly.Response, err error) {
		log.Printf("India Today - Error scraping %s: %s\n", r.Request.URL, err)
		log.Printf("India Today - Response status: %d\n", r.StatusCode)
		log.Printf("India Today - Response headers: %v\n", r.Headers)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Printf("India Today - Got response from %s: %d bytes\n", r.Request.URL, len(r.Body))
	})

	c.OnHTML("div.story__grid, div.story-list-item", func(e *colly.HTMLElement) {
		log.Printf("India Today - Found article element\n")
		
		title := strings.TrimSpace(e.ChildText("h2, h3, .story__title"))
		link := e.ChildAttr("a", "href")
		description := strings.TrimSpace(e.ChildText("p, .story__desc"))
		imageURL := e.ChildAttr("img", "src")

		log.Printf("India Today - Raw data - Title: %s, URL: %s\n", title, link)

		if title == "" || link == "" {
			log.Printf("India Today - Skipping article due to missing title or URL\n")
			return
		}

		// Make URL absolute if it's relative
		if !strings.HasPrefix(link, "http") {
			link = "https://www.indiatoday.in" + link
		}

		// Skip non-stock market articles
		if !strings.Contains(strings.ToLower(title), "stock") &&
			!strings.Contains(strings.ToLower(title), "market") &&
			!strings.Contains(strings.ToLower(title), "sensex") &&
			!strings.Contains(strings.ToLower(title), "nifty") &&
			!strings.Contains(strings.ToLower(link), "market") {
			log.Printf("India Today - Skipping non-stock market article: %s\n", title)
			return
		}

		article := models.Article{
			Title:       title,
			Description: description,
			URL:         link,
			Source: models.Source{
				Name: "India Today",
			},
			PublishedAt: time.Now(),
		}

		if imageURL != "" {
			article.ImageURL = imageURL
		}

		articles = append(articles, article)
		log.Printf("India Today - Successfully added article: %s\n", title)
	})

	err := c.Visit("https://www.indiatoday.in/business/market")
	if err != nil {
		return nil, fmt.Errorf("error visiting India Today: %v", err)
	}

	log.Printf("Found %d articles from India Today\n", len(articles))
	return articles, nil
} 