package services

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"time"
)

type MarketIndex struct {
	Symbol     string    `json:"symbol"`
	Name       string    `json:"name"`
	Price      float64   `json:"price"`
	Change     float64   `json:"change"`
	ChangePerc float64   `json:"changePercentage"`
	UpdatedAt  time.Time `json:"updatedAt"`
	IsDelayed  bool      `json:"isDelayed"`
}

type YahooResponse struct {
	Chart struct {
		Result []struct {
			Meta struct {
				Symbol             string  `json:"symbol"`
				RegularMarketPrice float64 `json:"regularMarketPrice"`
				ChartPreviousClose float64 `json:"chartPreviousClose"`
				PreviousClose      float64 `json:"previousClose"`
				RegularMarketTime  int64   `json:"regularMarketTime"`
			} `json:"meta"`
			Timestamp []int64   `json:"timestamp"`
			Indicators struct {
				Quote []struct {
					Close []float64 `json:"close"`
					Open  []float64 `json:"open"`
				} `json:"quote"`
			} `json:"indicators"`
		} `json:"result"`
		Error *struct {
			Code        string `json:"code"`
			Description string `json:"description"`
		} `json:"error"`
	} `json:"chart"`
}

func isValidNumber(n float64) bool {
	return !math.IsNaN(n) && !math.IsInf(n, 0)
}

func calculateChange(currentPrice, previousClose float64) (change, changePerc float64) {
	if !isValidNumber(currentPrice) || !isValidNumber(previousClose) {
		return 0, 0
	}

	change = currentPrice - previousClose
	
	// Handle division by zero or very small numbers
	if previousClose == 0 || math.Abs(previousClose) < 0.000001 {
		changePerc = 0
	} else {
		changePerc = (change / previousClose) * 100
		// Validate the result
		if !isValidNumber(changePerc) {
			changePerc = 0
		}
	}

	// Round to 2 decimal places to avoid floating point precision issues
	change = math.Round(change*100) / 100
	changePerc = math.Round(changePerc*100) / 100

	return change, changePerc
}

func fetchSingleIndex(symbol string) (*MarketIndex, error) {
	// Using the chart endpoint to get both current and historical data
	url := fmt.Sprintf("https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=2d", symbol)
	
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %v", err)
	}

	// Add headers to mimic browser request
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Referer", "https://finance.yahoo.com")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error fetching data for %s: %v", symbol, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("received non-200 status code: %d for symbol %s", resp.StatusCode, symbol)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %v", err)
	}

	var yahooResp YahooResponse
	if err := json.Unmarshal(body, &yahooResp); err != nil {
		return nil, fmt.Errorf("error decoding response: %v, body: %s", err, string(body))
	}

	// Check for API error response
	if yahooResp.Chart.Error != nil {
		return nil, fmt.Errorf("yahoo API error: %s - %s",
			yahooResp.Chart.Error.Code,
			yahooResp.Chart.Error.Description)
	}

	if len(yahooResp.Chart.Result) == 0 {
		return nil, fmt.Errorf("no data received for symbol %s", symbol)
	}

	result := yahooResp.Chart.Result[0]
	meta := result.Meta
	
	// Get current price and calculate changes
	var currentPrice, previousClose float64
	var marketTime time.Time
	var isDelayed bool

	// Try to get current price from meta
	currentPrice = meta.RegularMarketPrice
	previousClose = meta.PreviousClose

	// Validate current price and previous close
	if !isValidNumber(currentPrice) {
		currentPrice = 0
	}
	if !isValidNumber(previousClose) {
		previousClose = 0
	}

	// If current price is not available or invalid, try to get from historical data
	if currentPrice == 0 && len(result.Indicators.Quote) > 0 && len(result.Indicators.Quote[0].Close) > 0 {
		lastIdx := len(result.Indicators.Quote[0].Close) - 1
		historicalPrice := result.Indicators.Quote[0].Close[lastIdx]
		
		// Validate historical price
		if isValidNumber(historicalPrice) {
			currentPrice = historicalPrice
			
			// If we have at least 2 data points, get the previous close
			if lastIdx > 0 {
				prevPrice := result.Indicators.Quote[0].Close[lastIdx-1]
				if isValidNumber(prevPrice) {
					previousClose = prevPrice
				}
			}
			isDelayed = true
		}
	}

	if currentPrice == 0 {
		return nil, fmt.Errorf("no valid price data available for %s", symbol)
	}

	// Calculate changes with validation
	change, changePerc := calculateChange(currentPrice, previousClose)

	// Get market time
	if meta.RegularMarketTime > 0 {
		marketTime = time.Unix(meta.RegularMarketTime, 0)
	} else if len(result.Timestamp) > 0 {
		marketTime = time.Unix(result.Timestamp[len(result.Timestamp)-1], 0)
	} else {
		marketTime = time.Now()
	}

	return &MarketIndex{
		Symbol:     symbol,
		Name:       getIndexName(symbol),
		Price:      currentPrice,
		Change:     change,
		ChangePerc: changePerc,
		UpdatedAt:  marketTime,
		IsDelayed:  isDelayed,
	}, nil
}

func getIndexName(symbol string) string {
	switch symbol {
	case "^NSEI":
		return "NIFTY 50"
	case "^BSESN":
		return "BSE SENSEX"
	default:
		return symbol
	}
}

func FetchMarketIndices() ([]MarketIndex, error) {
	symbols := []string{"^NSEI", "^BSESN"}
	var indices []MarketIndex

	for _, symbol := range symbols {
		index, err := fetchSingleIndex(symbol)
		if err != nil {
			log.Printf("Error fetching %s: %v", symbol, err)
			continue
		}
		indices = append(indices, *index)

		// Add a small delay between requests
		time.Sleep(500 * time.Millisecond)
	}

	if len(indices) == 0 {
		return nil, fmt.Errorf("no valid market indices data found")
	}

	return indices, nil
} 