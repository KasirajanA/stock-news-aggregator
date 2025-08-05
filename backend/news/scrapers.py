"""
Web scraping functionality for news sources.
"""
import requests
import time
import logging
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.utils import timezone
from django.conf import settings
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import random

from .models import NewsSource, Article

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for web scrapers."""
    
    def __init__(self, source: NewsSource):
        self.source = source
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
    
    def scrape(self) -> List[Dict]:
        """Scrape articles from the source."""
        try:
            logger.info(f"Starting scrape for {self.source.name}")
            
            # Try RSS feed first if available
            rss_articles = self.scrape_rss_feed()
            if rss_articles:
                logger.info(f"Found {len(rss_articles)} articles via RSS for {self.source.name}")
                return rss_articles
            
            # Fallback to web scraping
            return self.scrape_web()
            
        except Exception as e:
            logger.error(f"Error scraping {self.source.name}: {e}")
            return []
    
    def scrape_rss_feed(self) -> List[Dict]:
        """Scrape articles from RSS feed if available."""
        rss_urls = self.get_rss_urls()
        
        for rss_url in rss_urls:
            try:
                logger.info(f"Trying RSS feed: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                if feed.entries:
                    articles = []
                    for entry in feed.entries[:15]:  # Limit to 15 articles
                        try:
                            article_data = self.parse_rss_entry(entry)
                            if article_data:
                                articles.append(article_data)
                        except Exception as e:
                            logger.error(f"Error parsing RSS entry: {e}")
                            continue
                    
                    if articles:
                        return articles
                        
            except Exception as e:
                logger.error(f"Error parsing RSS feed {rss_url}: {e}")
                continue
        
        return []
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for the source. Override in subclasses."""
        return []
    
    def parse_rss_entry(self, entry) -> Optional[Dict]:
        """Parse RSS entry to article data."""
        try:
            # Extract title
            title = self.clean_text(entry.get('title', ''))
            if not title:
                return None
            
            # Extract description
            description = self.clean_text(entry.get('description', ''))
            
            # Extract content
            content = self.clean_text(entry.get('content', [{}])[0].get('value', '')) if entry.get('content') else description
            
            # Extract URL
            url = entry.get('link', '')
            if not url:
                return None
            
            # Extract publication date
            published_at = self.parse_rss_date(entry)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    def parse_rss_date(self, entry) -> datetime:
        """Parse publication date from RSS entry."""
        try:
            # Try different date fields
            date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
            for field in date_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    naive_date = datetime(*getattr(entry, field)[:6])
                    # Make timezone-aware
                    return timezone.make_aware(naive_date)
        except:
            pass
        
        return timezone.now()
    
    def scrape_web(self) -> List[Dict]:
        """Scrape articles from the web page."""
        try:
            # Get the main page with retry logic
            response = self.get_page_with_retry(self.source.base_url)
            if not response:
                return []
            
            # Parse the page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article links
            article_links = self.extract_article_links(soup)
            
            # Scrape individual articles
            articles = []
            for link in article_links[:15]:  # Increased limit to 15 articles
                try:
                    article_data = self.scrape_article(link)
                    if article_data:
                        articles.append(article_data)
                    time.sleep(random.uniform(0.5, 1.5))  # Random delay
                except Exception as e:
                    logger.error(f"Error scraping article {link}: {e}")
                    continue
            
            # Update last scraped timestamp
            self.source.last_scraped_at = timezone.now()
            self.source.save()
            
            logger.info(f"Successfully scraped {len(articles)} articles from {self.source.name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping {self.source.name}: {e}")
            return []
    
    def get_page_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Get page with retry logic and rotating user agents."""
        for attempt in range(max_retries):
            try:
                # Rotate user agent on each attempt
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                ]
                self.session.headers['User-Agent'] = random.choice(user_agents)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))  # Random delay between retries
                continue
        
        return None
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from the page. Override in subclasses."""
        raise NotImplementedError
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article. Override in subclasses."""
        raise NotImplementedError
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        
        return text
    
    def extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date from article. Override in subclasses."""
        # Common date selectors
        date_selectors = [
            'time',
            '.date',
            '.published',
            '.timestamp',
            '[datetime]',
            '.article-date',
            '.post-date',
            '.story-date',
            '.publish-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                # Try to get datetime attribute
                datetime_attr = element.get('datetime')
                if datetime_attr:
                    try:
                        return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    except:
                        pass
                
                # Try to parse text content
                date_text = element.get_text().strip()
                if date_text:
                    try:
                        # Common date formats
                        for fmt in ['%Y-%m-%d', '%B %d, %Y', '%d %B %Y', '%Y/%m/%d']:
                            try:
                                return datetime.strptime(date_text, fmt)
                            except:
                                continue
                    except:
                        pass
        
        # Default to current time if no date found
        return timezone.now()


class LiveMintScraper(BaseScraper):
    """Scraper for LiveMint news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for LiveMint."""
        return [
            'https://www.livemint.com/rss/markets',
            'https://www.livemint.com/rss/companies',
            'https://www.livemint.com/rss/industry'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from LiveMint homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/markets/"]',
            'a[href*="/companies/"]',
            'a[href*="/industry/"]',
            'a[href*="/money/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/markets/', '/companies/', '/industry/', '/money/', '/news/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'livemint.com' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from LiveMint."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class EconomicTimesScraper(BaseScraper):
    """Scraper for Economic Times news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for Economic Times."""
        return [
            'https://economictimes.indiatimes.com/rss.cms',
            'https://economictimes.indiatimes.com/markets/rss.cms',
            'https://economictimes.indiatimes.com/companies/rss.cms'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from Economic Times homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/markets/"]',
            'a[href*="/companies/"]',
            'a[href*="/news/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/markets/', '/companies/', '/news/', '/economy/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'economictimes.indiatimes.com' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from Economic Times."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class MoneyControlScraper(BaseScraper):
    """Scraper for MoneyControl news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for MoneyControl."""
        return [
            'https://www.moneycontrol.com/rss/business.xml',
            'https://www.moneycontrol.com/rss/markets.xml',
            'https://www.moneycontrol.com/rss/news.xml'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from MoneyControl homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/news/"]',
            'a[href*="/markets/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/news/', '/markets/', '/business/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'moneycontrol.com' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from MoneyControl."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class BusinessTodayScraper(BaseScraper):
    """Scraper for Business Today news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for Business Today."""
        return [
            'https://www.businesstoday.in/rss.xml',
            'https://www.businesstoday.in/rss/markets.xml',
            'https://www.businesstoday.in/rss/companies.xml'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from Business Today homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/markets/"]',
            'a[href*="/companies/"]',
            'a[href*="/news/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/markets/', '/companies/', '/news/', '/business/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'businesstoday.in' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from Business Today."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class BusinessLineScraper(BaseScraper):
    """Scraper for Business Line news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for Business Line."""
        return [
            'https://www.thehindubusinessline.com/news/national/?service=rss',
            'https://www.thehindubusinessline.com/markets/?service=rss',
            'https://www.thehindubusinessline.com/companies/?service=rss'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from Business Line homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/markets/"]',
            'a[href*="/companies/"]',
            'a[href*="/news/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/markets/', '/companies/', '/news/', '/business/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'thehindubusinessline.com' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from Business Line."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class BusinessStandardScraper(BaseScraper):
    """Scraper for Business Standard news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for Business Standard."""
        return [
            'https://www.business-standard.com/rss/current/rss.xml',
            'https://www.business-standard.com/rss/markets.xml',
            'https://www.business-standard.com/rss/companies.xml'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from Business Standard homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/markets/"]',
            'a[href*="/companies/"]',
            'a[href*="/news/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/markets/', '/companies/', '/news/', '/business/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'business-standard.com' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from Business Standard."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


class IndiaTodayScraper(BaseScraper):
    """Scraper for India Today news source."""
    
    def get_rss_urls(self) -> List[str]:
        """Get RSS feed URLs for India Today."""
        return [
            'https://www.indiatoday.in/rss/1206514',
            'https://www.indiatoday.in/rss/1206515',
            'https://www.indiatoday.in/rss/1206516'
        ]
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from India Today homepage."""
        links = []
        
        # Look for article links with more specific selectors
        article_selectors = [
            'a[href*="/business/"]',
            'a[href*="/markets/"]',
            'a[href*="/news/"]',
            '.storyCard a',
            '.article-link',
            '.listingPage a',
            '.story-list a',
            'h2 a',
            'h3 a',
            '.story-title a',
            '.headline a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Filter for actual article URLs
                    if any(keyword in href for keyword in ['/business/', '/markets/', '/news/', '/economy/']):
                        full_url = urljoin(self.source.base_url, href)
                        if full_url not in links and 'indiatoday.in' in full_url:
                            links.append(full_url)
        
        return links[:15]
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article from India Today."""
        try:
            response = self.get_page_with_retry(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title with multiple selectors
            title_selectors = ['h1', '.article-title', '.story-title', '.headline', '.title']
            title = None
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = self.clean_text(title_element.get_text())
                    break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = ['.article-summary', '.description', '.subhead', '.lead', '.summary']
            description = ""
            for selector in description_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    description = self.clean_text(desc_element.get_text())
                    break
            
            # Extract content with multiple selectors
            content_selectors = [
                '.article-content p',
                '.story-content p',
                '.content p',
                '.article-body p',
                '.story-body p',
                '.article-text p'
            ]
            
            content_parts = []
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts.extend([self.clean_text(p.get_text()) for p in elements])
                    break
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                return None
            
            # Extract publication date
            published_at = self.extract_date(soup)
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None


def get_scraper_for_source(source: NewsSource) -> BaseScraper:
    """Get appropriate scraper for a news source."""
    scraper_map = {
        'livemint.com': LiveMintScraper,
        'economictimes.indiatimes.com': EconomicTimesScraper,
        'moneycontrol.com': MoneyControlScraper,
        'businesstoday.in': BusinessTodayScraper,
        'thehindubusinessline.com': BusinessLineScraper,
        'business-standard.com': BusinessStandardScraper,
        'indiatoday.in': IndiaTodayScraper,
    }
    
    domain = source.domain.lower()
    scraper_class = scraper_map.get(domain, BaseScraper)
    
    return scraper_class(source)


def scrape_source(source: NewsSource) -> int:
    """Scrape articles from a specific source."""
    try:
        # Check if source should be scraped
        if not source.should_scrape():
            logger.info(f"Source {source.name} was recently scraped, skipping")
            return 0
        
        # Get appropriate scraper
        scraper = get_scraper_for_source(source)
        
        # Scrape articles
        articles_data = scraper.scrape()
        
        # Save articles to database
        saved_count = 0
        for article_data in articles_data:
            try:
                # Check if article already exists
                existing_article = Article.objects.filter(url=article_data['url']).first()
                if existing_article:
                    continue
                
                # Create new article
                article = Article.objects.create(
                    url=article_data['url'],
                    title=article_data['title'],
                    description=article_data['description'],
                    content=article_data['content'],
                    published_at=article_data['published_at'],
                    source=source
                )
                
                saved_count += 1
                logger.info(f"Saved article: {article.title}")
                
            except Exception as e:
                logger.error(f"Error saving article {article_data.get('title', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Successfully scraped {saved_count} new articles from {source.name}")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error scraping source {source.name}: {e}")
        return 0


def scrape_all_sources() -> Dict[str, int]:
    """Scrape all active news sources."""
    results = {}
    
    active_sources = NewsSource.objects.filter(is_active=True)
    
    for source in active_sources:
        try:
            count = scrape_source(source)
            results[source.name] = count
        except Exception as e:
            logger.error(f"Error scraping source {source.name}: {e}")
            results[source.name] = 0
    
    return results 