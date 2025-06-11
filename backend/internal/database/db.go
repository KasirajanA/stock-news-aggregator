package database

import (
	"database/sql"
	"time"
	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func InitDB(dbPath string) error {
	var err error
	db, err = sql.Open("sqlite3", dbPath)
	if err != nil {
		return err
	}

	// Create articles table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS articles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			url TEXT UNIQUE NOT NULL,
			source TEXT NOT NULL,
			content TEXT,
			description TEXT,
			published_at DATETIME,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			last_scraped_at DATETIME
		)
	`)
	if err != nil {
		return err
	}

	return nil
}

func GetDB() *sql.DB {
	return db
}

func InsertArticle(title, url, source, content, description string, publishedAt time.Time) error {
	_, err := db.Exec(`
		INSERT OR IGNORE INTO articles (
			title, url, source, content, description, published_at, last_scraped_at
		) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	`, title, url, source, content, description, publishedAt)
	return err
}

func GetArticles(page, pageSize int, search string) ([]Article, int, error) {
	var articles []Article
	var totalCount int

	// Get total count with search condition
	countQuery := `SELECT COUNT(*) FROM articles`
	whereClause := ""
	args := []interface{}{}
	
	if search != "" {
		// Search in both title and content fields
		whereClause = ` WHERE (title LIKE ? OR content LIKE ? OR description LIKE ?)`
		searchTerm := "%" + search + "%"
		args = append(args, searchTerm, searchTerm, searchTerm)
	}
	
	err := db.QueryRow(countQuery+whereClause, args...).Scan(&totalCount)
	if err != nil {
		return nil, 0, err
	}

	// Get paginated results with search
	query := `
		SELECT id, title, url, source, content, description, published_at, created_at, last_scraped_at 
		FROM articles` + whereClause + `
		ORDER BY published_at DESC
		LIMIT ? OFFSET ?`

	args = append(args, pageSize, (page-1)*pageSize)
	rows, err := db.Query(query, args...)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	for rows.Next() {
		var article Article
		err := rows.Scan(
			&article.ID,
			&article.Title,
			&article.URL,
			&article.Source,
			&article.Content,
			&article.Description,
			&article.PublishedAt,
			&article.CreatedAt,
			&article.LastScrapedAt,
		)
		if err != nil {
			return nil, 0, err
		}
		articles = append(articles, article)
	}

	return articles, totalCount, nil
}

func IsArticleScraped(url string) (bool, error) {
	var exists bool
	err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM articles WHERE url = ?)", url).Scan(&exists)
	return exists, err
}

type Article struct {
	ID            int64      `json:"id"`
	Title         string     `json:"title"`
	URL           string     `json:"url"`
	Source        string     `json:"source"`
	Content       string     `json:"content"`
	Description   string     `json:"description"`
	PublishedAt   time.Time  `json:"publishedAt"`
	CreatedAt     time.Time  `json:"createdAt"`
	LastScrapedAt time.Time  `json:"lastScrapedAt"`
} 