package models

import "time"

type Article struct {
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Content     string    `json:"content"`
	URL         string    `json:"url"`
	ImageURL    string    `json:"urlToImage,omitempty"`
	Source      Source    `json:"source"`
	PublishedAt time.Time `json:"publishedAt"`
}

type Source struct {
	Name string `json:"name"`
} 