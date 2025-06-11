package main

import (
	"log"
	"net/http"
	"strconv"
	"time"
	"path/filepath"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"stock-news-aggregator/internal/services"
	"stock-news-aggregator/internal/models"
	"stock-news-aggregator/internal/database"
)

type PaginatedResponse struct {
	Articles    []models.Article `json:"articles"`
	TotalCount  int             `json:"totalCount"`
	CurrentPage int             `json:"currentPage"`
	PageSize    int             `json:"pageSize"`
	TotalPages  int             `json:"totalPages"`
}

// SummarizeRequest represents the request body for article summarization
type SummarizeRequest struct {
	URL string `json:"url" binding:"required"`
}

// SummarizeResponse represents the response for article summarization
type SummarizeResponse struct {
	Summary string `json:"summary"`
}

func main() {
	// Load .env file
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found or error loading it: %v", err)
	}

	// Initialize database
	dbPath := filepath.Join("data", "news.db")
	if err := database.InitDB(dbPath); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Initialize text summarizer
	summarizer := services.NewTextSummarizer(5) // 5 sentences max

	// Run initial scraping
	log.Println("Starting initial news scraping...")
	if err := services.ScrapeAndStoreNews(); err != nil {
		log.Printf("Error during initial scraping: %v", err)
	}

	router := gin.Default()

	// Configure CORS with more permissive settings
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5173"},
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{
			"Origin",
			"Content-Type",
			"Accept",
			"Authorization",
			"Cache-Control",
			"X-Requested-With",
		},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Routes
	router.GET("/api/news", getNews)           // Keep old endpoint for compatibility
	router.GET("/api/news/db", getNewsFromDB)  // New endpoint for database-backed news
	router.GET("/api/market-indices", getMarketIndices)
	router.POST("/api/summarize", func(c *gin.Context) {
		var req SummarizeRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		summary, err := summarizer.SummarizeURL(req.URL)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, SummarizeResponse{Summary: summary})
	})

	// Start periodic scraping in background
	go startPeriodicScraping()

	log.Printf("Starting server on :8080")
	log.Fatal(router.Run(":8080"))
}

func getNews(c *gin.Context) {
	// Get pagination parameters from query
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "10"))

	// Ensure valid pagination values
	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 10
	}
	if pageSize > 50 {
		pageSize = 50 // Maximum page size
	}

	// Fetch all news
	allNews, err := services.FetchAllNews()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Calculate pagination
	totalCount := len(allNews)
	totalPages := (totalCount + pageSize - 1) / pageSize

	// Ensure page number is within bounds
	if page > totalPages {
		page = totalPages
	}
	if page < 1 {
		page = 1
	}

	// Calculate start and end indices for the current page
	start := (page - 1) * pageSize
	end := start + pageSize
	if end > totalCount {
		end = totalCount
	}

	// Get the articles for the current page
	var pagedArticles []models.Article
	if start < totalCount {
		pagedArticles = allNews[start:end]
	}

	// Return paginated response
	c.JSON(http.StatusOK, PaginatedResponse{
		Articles:    pagedArticles,
		TotalCount:  totalCount,
		CurrentPage: page,
		PageSize:    pageSize,
		TotalPages:  totalPages,
	})
}

func getNewsFromDB(c *gin.Context) {
	// Get pagination and search parameters from query
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "10"))
	search := c.Query("search")

	// Ensure valid pagination values
	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 10
	}
	if pageSize > 50 {
		pageSize = 50 // Maximum page size
	}

	// Fetch news from database with search
	articles, totalCount, err := services.GetNewsFromDB(page, pageSize, search)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Calculate total pages
	totalPages := (totalCount + pageSize - 1) / pageSize

	// Return paginated response
	c.JSON(http.StatusOK, PaginatedResponse{
		Articles:    articles,
		TotalCount:  totalCount,
		CurrentPage: page,
		PageSize:    pageSize,
		TotalPages:  totalPages,
	})
}

func startPeriodicScraping() {
	ticker := time.NewTicker(15 * time.Minute)
	defer ticker.Stop()

	for {
		if err := services.ScrapeAndStoreNews(); err != nil {
			log.Printf("Error during periodic scraping: %v", err)
		}
		<-ticker.C
	}
}

func getMarketIndices(c *gin.Context) {
	indices, err := services.FetchMarketIndices()
	if err != nil {
		log.Printf("Error fetching market indices: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to fetch market indices",
			"details": err.Error(),
		})
		return
	}

	if len(indices) == 0 {
		log.Printf("No market indices data received")
		c.JSON(http.StatusNotFound, gin.H{
			"error": "No market data available",
		})
		return
	}

	c.JSON(http.StatusOK, indices)
} 