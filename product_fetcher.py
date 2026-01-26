"""
מודול למשיכת מוצרים מחנויות שותפים
Product Fetcher Module for Affiliate Programs
"""
# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import json
import time
import hashlib
import hmac
import base64
from urllib.parse import quote, urlparse, parse_qs
from bs4 import BeautifulSoup
import re

load_dotenv()


class ProductFetcher:
    """מחלקה בסיסית למשיכת מוצרים"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """משיכת מידע מוצר - צריך להיות מיושם בכל מחלקה יורשת"""
        raise NotImplementedError


class AmazonProductFetcher(ProductFetcher):
    """משיכת מוצרים מ-Amazon Associates"""
    
    def __init__(self):
        super().__init__()
        self.access_key = os.getenv('AMAZON_ACCESS_KEY')
        self.secret_key = os.getenv('AMAZON_SECRET_KEY')
        self.associate_tag = os.getenv('AMAZON_ASSOCIATE_TAG', 'your-tag')
        self.region = os.getenv('AMAZON_REGION', 'US')
        
        # Amazon Product Advertising API endpoints
        self.endpoints = {
            'US': 'webservices.amazon.com',
            'UK': 'webservices.amazon.co.uk',
            'DE': 'webservices.amazon.de',
            'FR': 'webservices.amazon.fr',
            'IT': 'webservices.amazon.it',
            'ES': 'webservices.amazon.es',
            'CA': 'webservices.amazon.ca',
            'JP': 'webservices.amazon.co.jp'
        }
    
    def _generate_signature(self, params: Dict, secret_key: str) -> str:
        """יצירת חתימה עבור Amazon API"""
        sorted_params = sorted(params.items())
        query_string = '&'.join([f"{quote(k, safe='')}={quote(str(v), safe='')}" 
                                 for k, v in sorted_params])
        string_to_sign = f"GET\n{self.endpoints.get(self.region, 'webservices.amazon.com')}\n/paapi5/searchitems\n{query_string}"
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), string_to_sign.encode(), hashlib.sha256).digest()
        ).decode()
        return signature
    
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """חיפוש מוצרים ב-Amazon"""
        if not self.access_key or not self.secret_key:
            print("[!] Amazon API credentials not configured. Using mock data.")
            return self._get_mock_products()
        
        try:
            # Amazon Product Advertising API 5.0
            params = {
                'Keywords': keywords,
                'SearchIndex': 'All',
                'ItemCount': min(max_results, 10),
                'PartnerType': 'Associates',
                'PartnerTag': self.associate_tag,
                'Marketplace': f'www.amazon.{self.region.lower() if self.region != "US" else "com"}',
                'Operation': 'SearchItems'
            }
            
            # Note: This is a simplified version. Full implementation requires proper API 5.0 setup
            # For now, we'll use a web scraping fallback or mock data
            return self._get_mock_products()
            
        except Exception as e:
            print(f"[X] Error fetching from Amazon: {e}")
            return self._get_mock_products()
    
    def fetch_product_by_url(self, product_url: str) -> Optional[Dict]:
        """משיכת מוצר לפי URL - משתמש ב-web scraping"""
        # Handle Amazon short URLs (amzn.to)
        if 'amzn.to' in product_url or 'amazon.com/shorturl' in product_url:
            print("[RESOLVE] Resolving Amazon short URL...")
            product_url = self._resolve_amazon_short_url(product_url)
            if not product_url:
                print("[X] Failed to resolve short URL")
                return None
        
        # Extract ASIN from URL
        asin = self._extract_asin(product_url)
        if not asin:
            print("[X] Could not extract ASIN from URL")
            print(f"[INFO] URL format: {product_url}")
            print("[INFO] Supported formats: amazon.com/dp/ASIN, amazon.com/gp/product/ASIN, amzn.to/XXXXX")
            return None
        
        print(f"[SCRAPE] Scraping Amazon product page for ASIN: {asin}")
        
        # Try to scrape the product page
        product_data = self._scrape_amazon_product(product_url, asin)
        
        if product_data:
            return product_data
        else:
            print("[!] Scraping failed, using mock data")
            return self._get_mock_product(asin)
    
    def _resolve_amazon_short_url(self, short_url: str) -> Optional[str]:
        """פתרון קישור קצר של Amazon (amzn.to) לקישור המלא"""
        try:
            # Follow redirects to get the full URL
            response = self.session.get(short_url, allow_redirects=True, timeout=10)
            final_url = response.url
            print(f"[OK] Resolved to: {final_url}")
            return final_url
        except Exception as e:
            print(f"[X] Error resolving short URL: {e}")
            return None
    
    def _extract_asin(self, url: str) -> Optional[str]:
        """חילוץ ASIN מ-URL של Amazon"""
        # Try multiple URL patterns
        patterns = [
            r'/dp/([A-Z0-9]{10})',           # Standard format: /dp/ASIN
            r'/gp/product/([A-Z0-9]{10})',    # Alternative: /gp/product/ASIN
            r'/product/([A-Z0-9]{10})',      # Another format: /product/ASIN
            r'/dp/([A-Z0-9]{10})/',          # With trailing slash
            r'/dp/([A-Z0-9]{10})\?',         # With query string
            r'asin=([A-Z0-9]{10})',          # Query parameter format
            r'/d/([A-Z0-9]{10})',             # Short format: /d/ASIN
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                asin = match.group(1).upper()
                # Validate ASIN format (10 alphanumeric characters)
                if len(asin) == 10 and re.match(r'^[A-Z0-9]{10}$', asin):
                    return asin
        
        return None
    
    def _scrape_amazon_product(self, url: str, asin: str) -> Optional[Dict]:
        """גריפת מידע מוצר מדף Amazon"""
        try:
            # Normalize URL
            if not url.startswith('http'):
                url = f'https://www.amazon.com{url}'
            
            # Add associate tag to URL if not present
            affiliate_url = self._create_affiliate_url(url, asin)
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product title
            title = self._extract_title(soup)
            
            # Extract price information
            price_data = self._extract_price(soup)
            
            # Extract image URL
            image_url = self._extract_image(soup)
            
            # Extract rating and reviews
            rating_data = self._extract_rating(soup)
            
            # Extract description
            description = self._extract_description(soup)
            
            # Build product dictionary
            product = {
                'title': title or f'Product {asin}',
                'price': price_data.get('current_price', '₪0'),
                'original_price': price_data.get('original_price', ''),
                'discount': price_data.get('discount', ''),
                'image_url': image_url or 'https://via.placeholder.com/800x800?text=Product',
                'rating': rating_data.get('rating', 0),
                'reviews_count': rating_data.get('reviews_count', 0),
                'affiliate_url': affiliate_url,
                'description': description or 'מוצר איכותי מומלץ'
            }
            
            print(f"[OK] Successfully scraped: {product['title']}")
            return product
            
        except requests.exceptions.RequestException as e:
            print(f"[X] Network error scraping Amazon: {e}")
            return None
        except Exception as e:
            print(f"[X] Error scraping Amazon product: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """חילוץ כותרת מוצר"""
        # Try multiple selectors for title
        selectors = [
            '#productTitle',
            'h1.a-size-large.product-title-word-break',
            'h1#title',
            'span#productTitle',
            'h1 span.a-size-large',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title:
                    return title
        
        # Fallback: try to find any h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, str]:
        """חילוץ מחיר מוצר"""
        price_data = {
            'current_price': '',
            'original_price': '',
            'discount': ''
        }
        
        # Try to find current price
        price_selectors = [
            'span.a-price-whole',
            'span#priceblock_ourprice',
            'span#priceblock_dealprice',
            'span#priceblock_saleprice',
            '.a-price .a-offscreen',
            'span.a-price.a-text-price .a-offscreen',
        ]
        
        current_price = None
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Extract price with currency symbol
                price_match = re.search(r'([₪$€£¥]?\s*\d+[.,]?\d*)', price_text)
                if price_match:
                    current_price = price_match.group(1).strip()
                    break
        
        # Try alternative method - look for price in JSON-LD or data attributes
        if not current_price:
            # Look for price in span with class containing "price"
            price_spans = soup.find_all('span', class_=re.compile('price', re.I))
            for span in price_spans:
                text = span.get_text(strip=True)
                price_match = re.search(r'([₪$€£¥]?\s*\d+[.,]?\d*)', text)
                if price_match:
                    current_price = price_match.group(1).strip()
                    break
        
        # Try to find original/list price
        original_price = None
        original_selectors = [
            'span.a-price.a-text-price span.a-offscreen',
            'span.basisPrice span.a-offscreen',
            '.a-text-strike',
        ]
        
        for selector in original_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price_match = re.search(r'([₪$€£¥]?\s*\d+[.,]?\d*)', price_text)
                if price_match:
                    original_price = price_match.group(1).strip()
                    break
        
        # Calculate discount if both prices exist
        discount = ''
        if current_price and original_price:
            try:
                # Extract numbers
                current_num = float(re.sub(r'[^\d.]', '', current_price.replace(',', '.')))
                original_num = float(re.sub(r'[^\d.]', '', original_price.replace(',', '.')))
                if original_num > current_num:
                    discount_pct = int(((original_num - current_num) / original_num) * 100)
                    discount = f'{discount_pct}%'
            except:
                pass
        
        price_data['current_price'] = current_price or '₪0'
        price_data['original_price'] = original_price or ''
        price_data['discount'] = discount
        
        return price_data
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """חילוץ תמונת מוצר"""
        # Try multiple selectors for main product image
        selectors = [
            '#landingImage',
            '#imgBlkFront',
            '#main-image',
            'img#productImage',
            'img[data-a-image-name="landingImage"]',
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                return img['src']
            if img and img.get('data-src'):
                return img['data-src']
            if img and img.get('data-old-src'):
                return img['data-old-src']
        
        # Fallback: find any large image
        images = soup.find_all('img', src=re.compile(r'\.(jpg|jpeg|png)', re.I))
        for img in images:
            src = img.get('src', '')
            if 'media' in src.lower() or 'images' in src.lower():
                if 'http' in src:
                    return src
        
        return None
    
    def _extract_rating(self, soup: BeautifulSoup) -> Dict[str, any]:
        """חילוץ דירוג וביקורות"""
        rating_data = {
            'rating': 0,
            'reviews_count': 0
        }
        
        # Try to find rating
        rating_selectors = [
            'span.a-icon-alt',
            '#acrPopover',
            'span.a-icon.a-icon-star',
            '[data-hook="rating-out-of-text"]',
        ]
        
        for selector in rating_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Look for pattern like "4.5 out of 5" or "4.5"
                rating_match = re.search(r'(\d+\.?\d*)\s*(?:out of|\s*stars?)?', text, re.I)
                if rating_match:
                    try:
                        rating_data['rating'] = float(rating_match.group(1))
                        break
                    except:
                        pass
        
        # Try to find reviews count
        reviews_selectors = [
            '#acrCustomerReviewText',
            '#acrCustomerReviewLink',
            'a[data-hook="see-all-reviews-link-foot"]',
            'span[data-hook="total-review-count"]',
        ]
        
        for selector in reviews_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Look for numbers in text like "1,234 ratings" or "1,234 reviews"
                reviews_match = re.search(r'([\d,]+)', text.replace(',', ''))
                if reviews_match:
                    try:
                        rating_data['reviews_count'] = int(reviews_match.group(1).replace(',', ''))
                        break
                    except:
                        pass
        
        return rating_data
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """חילוץ תיאור מוצר"""
        # Try to find product description
        desc_selectors = [
            '#productDescription',
            '#feature-bullets',
            '.product-description',
            '#aplus_feature_div',
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    # Take first 200 characters
                    return text[:200] + '...' if len(text) > 200 else text
        
        # Try bullet points
        bullets = soup.select('#feature-bullets li span.a-list-item')
        if bullets:
            descriptions = [b.get_text(strip=True) for b in bullets[:3] if b.get_text(strip=True)]
            if descriptions:
                return ' | '.join(descriptions)
        
        return None
    
    def _create_affiliate_url(self, url: str, asin: str) -> str:
        """יצירת קישור שותפים עם associate tag"""
        if not self.associate_tag or self.associate_tag == 'your-tag':
            return url
        
        # Parse URL
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Add or update tag parameter
        query_params['tag'] = [self.associate_tag]
        
        # Rebuild URL with proper query string
        if query_params:
            # Build query string properly
            query_parts = []
            for k, v_list in query_params.items():
                for v in v_list:
                    query_parts.append(f"{quote(k)}={quote(str(v))}")
            new_query = '&'.join(query_parts)
            affiliate_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        else:
            # No existing query params, add tag
            affiliate_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?tag={quote(self.associate_tag)}"
        
        return affiliate_url
    
    def _get_mock_products(self) -> List[Dict]:
        """נתוני דמה לבדיקה"""
        return [
            {
                'title': 'מוצר אלקטרוני מתקדם',
                'price': '₪299',
                'original_price': '₪399',
                'discount': '25%',
                'image_url': 'https://via.placeholder.com/800x800?text=Product+1',
                'rating': 4.5,
                'reviews_count': 1234,
                'affiliate_url': 'https://amazon.com/dp/EXAMPLE123',
                'description': 'מוצר איכותי עם ביקורות מעולות'
            },
            {
                'title': 'גאדג\'ט חדשני',
                'price': '₪149',
                'original_price': '₪199',
                'discount': '25%',
                'image_url': 'https://via.placeholder.com/800x800?text=Product+2',
                'rating': 4.8,
                'reviews_count': 567,
                'affiliate_url': 'https://amazon.com/dp/EXAMPLE456',
                'description': 'הפתרון המושלם לצרכים שלך'
            }
        ]
    
    def _get_mock_product(self, asin: str) -> Dict:
        """מוצר דמה בודד"""
        return {
            'title': f'מוצר {asin}',
            'price': '₪199',
            'original_price': '₪249',
            'discount': '20%',
            'image_url': 'https://via.placeholder.com/800x800?text=Product',
            'rating': 4.6,
            'reviews_count': 890,
            'affiliate_url': f'https://amazon.com/dp/{asin}',
            'description': 'מוצר מומלץ עם איכות גבוהה'
        }


class AliExpressProductFetcher(ProductFetcher):
    """משיכת מוצרים מ-AliExpress Affiliate"""
    
    def __init__(self):
        super().__init__()
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
    
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """חיפוש מוצרים ב-AliExpress"""
        if not self.app_key or not self.app_secret:
            print("[!] AliExpress API credentials not configured. Using mock data.")
            return self._get_mock_products()
        
        try:
            # AliExpress Affiliate API implementation
            # This requires proper API setup with signature generation
            return self._get_mock_products()
        except Exception as e:
            print(f"[X] Error fetching from AliExpress: {e}")
            return self._get_mock_products()
    
    def fetch_product_by_url(self, product_url: str) -> Optional[Dict]:
        """משיכת מוצר לפי URL"""
        # Extract product ID from AliExpress URL
        product_id = self._extract_product_id(product_url)
        if not product_id:
            return None
        
        return self._get_mock_product(product_id)
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """חילוץ ID מוצר מ-URL של AliExpress"""
        import re
        match = re.search(r'/item/(\d+)\.html', url)
        if match:
            return match.group(1)
        return None
    
    def _get_mock_products(self) -> List[Dict]:
        """נתוני דמה לבדיקה"""
        return [
            {
                'title': 'מוצר מיוחד מ-AliExpress',
                'price': '₪89',
                'original_price': '₪129',
                'discount': '31%',
                'image_url': 'https://via.placeholder.com/800x800?text=AliExpress+Product',
                'rating': 4.3,
                'reviews_count': 2345,
                'affiliate_url': 'https://aliexpress.com/item/EXAMPLE789',
                'description': 'משלוח מהיר ואיכות מעולה'
            }
        ]
    
    def _get_mock_product(self, product_id: str) -> Dict:
        """מוצר דמה בודד"""
        return {
            'title': f'מוצר AliExpress {product_id}',
            'price': '₪79',
            'original_price': '₪119',
            'discount': '34%',
            'image_url': 'https://via.placeholder.com/800x800?text=AliExpress',
            'rating': 4.4,
            'reviews_count': 1567,
            'affiliate_url': f'https://aliexpress.com/item/{product_id}',
            'description': 'איכות מעולה במחיר מצוין'
        }


class eBayProductFetcher(ProductFetcher):
    """משיכת מוצרים מ-eBay Partner Network"""
    
    def __init__(self):
        super().__init__()
        self.app_id = os.getenv('EBAY_APP_ID')
        self.cert_id = os.getenv('EBAY_CERT_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID')
        self.affiliate_campaign_id = os.getenv('EBAY_AFFILIATE_CAMPAIGN_ID', '')
    
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """חיפוש מוצרים ב-eBay"""
        if not self.app_id:
            print("[!] eBay API credentials not configured. Using mock data.")
            return self._get_mock_products()
        
        try:
            # eBay Finding API or Browse API implementation
            # This requires proper API setup with OAuth or API keys
            # For now, we'll use mock data
            return self._get_mock_products()
        except Exception as e:
            print(f"[X] Error fetching from eBay: {e}")
            return self._get_mock_products()
    
    def fetch_product_by_url(self, product_url: str) -> Optional[Dict]:
        """משיכת מוצר לפי URL"""
        # Extract item ID from eBay URL
        item_id = self._extract_item_id(product_url)
        if not item_id:
            return None
        
        return self._get_mock_product(item_id)
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        """חילוץ ID מוצר מ-URL של eBay"""
        import re
        # eBay URLs can be: /itm/123456789 or /p/123456789
        match = re.search(r'/(?:itm|p)/(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def _get_mock_products(self) -> List[Dict]:
        """נתוני דמה לבדיקה"""
        return [
            {
                'title': 'מוצר eBay איכותי',
                'price': '₪159',
                'original_price': '₪199',
                'discount': '20%',
                'image_url': 'https://via.placeholder.com/800x800?text=eBay+Product',
                'rating': 4.7,
                'reviews_count': 3456,
                'affiliate_url': 'https://ebay.com/itm/EXAMPLE123',
                'description': 'מוצר מעולה עם משלוח מהיר'
            }
        ]
    
    def _get_mock_product(self, item_id: str) -> Dict:
        """מוצר דמה בודד"""
        return {
            'title': f'מוצר eBay {item_id}',
            'price': '₪149',
            'original_price': '₪189',
            'discount': '21%',
            'image_url': 'https://via.placeholder.com/800x800?text=eBay',
            'rating': 4.6,
            'reviews_count': 2345,
            'affiliate_url': f'https://ebay.com/itm/{item_id}',
            'description': 'איכות גבוהה במחיר תחרותי'
        }


def get_fetcher(store: str = 'amazon') -> ProductFetcher:
    """Factory function לקבלת fetcher לפי חנות"""
    if store.lower() == 'amazon':
        return AmazonProductFetcher()
    elif store.lower() == 'aliexpress':
        return AliExpressProductFetcher()
    elif store.lower() == 'ebay':
        return eBayProductFetcher()
    else:
        raise ValueError(f"Unknown store: {store}. Supported: 'amazon', 'aliexpress', 'ebay'")
