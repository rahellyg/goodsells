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
        # Check if it's an affiliate link and normalize it
        if 'tag=' in product_url or 'linkId=' in product_url or 'ref=' in product_url:
            print("[AFFILIATE] Detected affiliate link, normalizing...")
            original_url = product_url
            product_url = self._normalize_affiliate_link(product_url)
            if product_url != original_url:
                print(f"[OK] Normalized affiliate link to: {product_url[:80]}...")
        
        # Handle Amazon short URLs (amzn.to)
        if 'amzn.to' in product_url or 'amazon.com/shorturl' in product_url:
            print("[RESOLVE] Resolving Amazon short URL...")
            resolved_url = self._resolve_amazon_short_url(product_url)
            if not resolved_url:
                print("[X] Failed to resolve short URL or URL doesn't point to a product")
                return None
            product_url = resolved_url
            print(f"[OK] Using resolved URL: {product_url[:100]}...")
        
        # Check if URL is a category/browse page - if so, handle it differently
        if self._is_category_page(product_url):
            # This will be handled by fetch_products_from_category
            return None
        
        # Check if it's a VDP (Video Detail Page) link
        is_vdp = '/vdp/' in product_url
        if is_vdp:
            print("[VDP] Detected Video Detail Page link")
        
        # Extract ASIN from URL
        asin = self._extract_asin(product_url)
        if not asin:
            print("[X] Could not extract ASIN from URL")
            print(f"[INFO] URL received: {product_url}")
            print("\n[INFO] Supported product URL formats:")
            print("       • https://www.amazon.com/dp/B08N5WRWNW")
            print("       • https://www.amazon.com/gp/product/B08N5WRWNW")
            print("       • https://www.amazon.com/vdp/...?product=B0D1G7XF9X (VDP link)")
            print("       • https://amzn.to/XXXXX (short URL)")
            print("\n[INFO] Make sure you're using a direct product page URL, not a category or search page")
            return None
        
        print(f"[SCRAPE] Scraping Amazon product page for ASIN: {asin}")
        
        # If it's a VDP link, try to extract video from VDP page first
        vdp_video_url = None
        if is_vdp:
            print("[VDP] Attempting to extract video from VDP page...")
            vdp_video_url = self._extract_video_from_vdp_page(product_url)
            if vdp_video_url:
                print(f"[OK] Found video on VDP page:")
                print(f"     VIDEO URL: {vdp_video_url}")
            else:
                print("[!] Could not extract video from VDP page")
        
        # Get the regular product page URL
        regular_product_url = f'https://www.amazon.com/dp/{asin}'
        
        # Try to scrape the product page
        product_data = self._scrape_amazon_product(regular_product_url, asin, vdp_video_url)
        
        # If we found a video on VDP page and product page doesn't have one, use VDP video
        if vdp_video_url and product_data and not product_data.get('video_url'):
            product_data['video_url'] = vdp_video_url
            print(f"[OK] Using video from VDP page")
        
        if product_data:
            return product_data
        else:
            print("[!] Scraping failed, using mock data")
            return self._get_mock_product(asin)
    
    def fetch_products_from_category(self, category_url: str, max_products: int = 20) -> List[Dict]:
        """משיכת כל המוצרים מדף קטגוריה"""
        print(f"[CATEGORY] Extracting products from category page...")
        
        try:
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = self.session.get(category_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all product URLs from the page
            product_urls = self._extract_product_urls_from_category(soup)
            
            if not product_urls:
                print("[!] No product URLs found on category page")
                return []
            
            print(f"[OK] Found {len(product_urls)} product links")
            
            # Limit to max_products
            product_urls = product_urls[:max_products]
            
            # Fetch each product
            products = []
            for i, url in enumerate(product_urls, 1):
                print(f"\n[PRODUCT] [{i}/{len(product_urls)}] Fetching: {url}")
                asin = self._extract_asin(url)
                if asin:
                    product = self._scrape_amazon_product(url, asin)
                    if product:
                        products.append(product)
                    else:
                        print(f"[!] Failed to scrape product {asin}, skipping...")
                else:
                    print(f"[!] Could not extract ASIN from {url}, skipping...")
                
                # Small delay to avoid being blocked
                time.sleep(1)
            
            print(f"\n[OK] Successfully fetched {len(products)} products from category")
            return products
            
        except Exception as e:
            print(f"[X] Error fetching products from category: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_product_urls_from_category(self, soup: BeautifulSoup) -> List[str]:
        """חילוץ כל קישורי המוצרים מדף קטגוריה"""
        product_urls = []
        seen_asins = set()
        
        # Multiple selectors for product links on category pages
        selectors = [
            'a[href*="/dp/"]',
            'a[href*="/gp/product/"]',
            'a[href*="/product/"]',
            'div[data-asin] a[href*="/dp/"]',
            'div[data-asin] a[href*="/gp/product/"]',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = f'https://www.amazon.com{href}'
                elif not href.startswith('http'):
                    continue
                
                # Extract ASIN to avoid duplicates
                asin = self._extract_asin(href)
                if asin and asin not in seen_asins:
                    seen_asins.add(asin)
                    product_urls.append(href)
        
        # Also try to find ASINs in data attributes
        items_with_asin = soup.find_all(attrs={'data-asin': True})
        for item in items_with_asin:
            asin = item.get('data-asin', '').strip()
            if asin and len(asin) == 10 and asin not in seen_asins:
                seen_asins.add(asin)
                product_url = f'https://www.amazon.com/dp/{asin}'
                product_urls.append(product_url)
        
        return product_urls
    
    def _is_category_page(self, url: str) -> bool:
        """בדיקה אם ה-URL הוא דף קטגוריה ולא דף מוצר"""
        category_patterns = [
            r'/gp/(?:bestsellers|new-releases|movers-and-shakers|most-wished-for|most-gifted)',
            r'/s\?',
            r'/s/ref=',
            r'/b/',
            r'/gp/search',
            r'/s/field-keywords=',
        ]
        
        for pattern in category_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _resolve_amazon_short_url(self, short_url: str) -> Optional[str]:
        """פתרון קישור קצר של Amazon (amzn.to) לקישור המלא"""
        try:
            print(f"[RESOLVE] Resolving short URL: {short_url}")
            
            # Set headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Follow redirects to get the full URL
            response = self.session.get(short_url, headers=headers, allow_redirects=True, timeout=15)
            final_url = response.url
            
            print(f"[RESOLVE] Final URL after redirects: {final_url}")
            
            # Check if resolved URL is a category page or "Keep shopping" page
            if self._is_category_page(final_url):
                print(f"[!] Warning: Short URL resolved to a category page: {final_url}")
                print("[INFO] You need a direct product URL. Please use a product page link instead.")
                return None
            
            # Check for "Keep shopping" or other non-product pages
            if 'keep shopping' in response.text.lower() or 'browse' in final_url.lower():
                print(f"[!] Warning: Short URL resolved to a browse/shopping page, not a product page")
                print("[INFO] This short link doesn't point to a specific product. Please use a direct product URL.")
                return None
            
            # Try to extract ASIN from the final URL
            asin = self._extract_asin(final_url)
            if not asin:
                print(f"[!] Warning: Could not extract ASIN from resolved URL: {final_url}")
                print("[INFO] The short link may not point to a valid product page.")
                # Still return the URL - let the caller try to handle it
                return final_url
            
            print(f"[OK] Successfully resolved short URL to product: {final_url}")
            print(f"[OK] Extracted ASIN: {asin}")
            return final_url
            
        except requests.exceptions.TooManyRedirects:
            print(f"[X] Error: Too many redirects for short URL")
            return None
        except requests.exceptions.Timeout:
            print(f"[X] Error: Timeout while resolving short URL")
            return None
        except Exception as e:
            print(f"[X] Error resolving short URL: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_asin(self, url: str) -> Optional[str]:
        """חילוץ ASIN מ-URL של Amazon - כולל VDP links"""
        # First, check if it's a VDP (Video Detail Page) link
        if '/vdp/' in url:
            # Extract ASIN from query parameter: product=B0D1G7XF9X
            match = re.search(r'[?&]product=([A-Z0-9]{10})', url, re.IGNORECASE)
            if match:
                asin = match.group(1).upper()
                if len(asin) == 10 and re.match(r'^[A-Z0-9]{10}$', asin):
                    return asin
        
        # Try multiple URL patterns
        patterns = [
            r'/dp/([A-Z0-9]{10})',           # Standard format: /dp/ASIN
            r'/gp/product/([A-Z0-9]{10})',    # Alternative: /gp/product/ASIN
            r'/product/([A-Z0-9]{10})',      # Another format: /product/ASIN
            r'/dp/([A-Z0-9]{10})/',          # With trailing slash
            r'/dp/([A-Z0-9]{10})\?',         # With query string
            r'asin=([A-Z0-9]{10})',          # Query parameter format
            r'product=([A-Z0-9]{10})',       # Product query parameter (for VDP)
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
    
    def _scrape_amazon_product(self, url: str, asin: str, existing_video_url: Optional[str] = None) -> Optional[Dict]:
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
            
            # Extract product video (if available)
            # Use existing video URL from VDP if provided, otherwise try to extract from page
            video_url = existing_video_url
            if not video_url:
                video_url = self._extract_product_video(soup)
                if video_url:
                    print(f"[OK] Found product video on product page:")
                    print(f"     VIDEO URL: {video_url}")
                else:
                    print("[INFO] No product video found on product page, will use images")
            else:
                print(f"[OK] Using video from VDP:")
                print(f"     VIDEO URL: {video_url}")
            
            # Extract image URLs (multiple images for slideshow)
            image_urls = self._extract_all_images(soup)
            if not image_urls:
                print("[!] Warning: Could not extract product images from page")
            else:
                print(f"[OK] Found {len(image_urls)} product image(s)")
            
            # Extract main image URL (for backward compatibility)
            image_url = image_urls[0] if image_urls else None
            
            # Extract rating and reviews
            rating_data = self._extract_rating(soup)
            
            # Extract description
            description = self._extract_description(soup)
            
            # Build product dictionary
            product = {
                'title': title or f'Product {asin}',
                'price': price_data.get('current_price', '$0'),
                'original_price': price_data.get('original_price', ''),
                'discount': price_data.get('discount', ''),
                'image_url': image_url or '',  # Main image for backward compatibility
                'image_urls': image_urls if 'image_urls' in locals() else [],  # All images for slideshow
                'video_url': video_url if 'video_url' in locals() else '',  # Product video if available
                'rating': rating_data.get('rating', 0),
                'reviews_count': rating_data.get('reviews_count', 0),
                'affiliate_url': affiliate_url,
                'description': description or 'High quality recommended product'
            }
            
            # Print detailed information
            print(f"\n[OK] Successfully scraped product:")
            print(f"     Title: {product['title']}")
            print(f"     Price: {product['price']}")
            if product['original_price']:
                print(f"     Original Price: {product['original_price']}")
            if product['discount']:
                print(f"     Discount: {product['discount']}")
            print(f"     Rating: {product['rating']} ({product['reviews_count']} reviews)")
            print(f"     Image: {'Found' if image_url else 'Not found - will use placeholder'}")
            if product.get('video_url'):
                print(f"     Video: FOUND")
                print(f"     VIDEO URL: {product['video_url']}")
            else:
                print(f"     Video: Not found - will use images/slideshow")
            if description:
                print(f"     Description: {description[:100]}...")
            
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
        """חילוץ כותרת מוצר - משופר עם JSON-LD ו-selectors נוספים"""
        # First, try JSON-LD structured data (most reliable)
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for name in various formats
                    if 'name' in data:
                        name = data['name']
                        if isinstance(name, str) and len(name) > 5:
                            return name.strip()
                    # Check for @graph array
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') == 'Product' and 'name' in item:
                                return item['name'].strip()
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product' and 'name' in item:
                            return item['name'].strip()
            except:
                continue
        
        # Try multiple selectors for title
        selectors = [
            '#productTitle',
            'h1.a-size-large.product-title-word-break',
            'h1#title',
            'span#productTitle',
            'h1 span.a-size-large',
            'h1.a-size-base-plus',
            '#title_feature_div h1',
            '#titleSection h1',
            'h1[data-automation-id="title"]',
            '.product-title-word-break',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 3:
                    # Clean up title - remove extra whitespace
                    title = re.sub(r'\s+', ' ', title)
                    return title
        
        # Fallback: try to find any h1 with product-related classes
        h1_elements = soup.find_all('h1', class_=re.compile(r'(title|product)', re.I))
        for h1 in h1_elements:
            title = h1.get_text(strip=True)
            if title and len(title) > 3:
                return re.sub(r'\s+', ' ', title)
        
        # Last resort: any h1
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
            if title:
                return re.sub(r'\s+', ' ', title)
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, str]:
        """חילוץ מחיר מוצר - משופר עם JSON-LD ו-selectors נוספים"""
        price_data = {
            'current_price': '',
            'original_price': '',
            'discount': ''
        }
        
        # First, try JSON-LD structured data (most reliable)
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for offers/price
                    if 'offers' in data:
                        offers = data['offers']
                        if isinstance(offers, dict):
                            if 'price' in offers:
                                price = str(offers['price'])
                                currency = offers.get('priceCurrency', 'USD')
                                price_data['current_price'] = f"{currency}{price}"
                        elif isinstance(offers, list) and len(offers) > 0:
                            offer = offers[0]
                            if isinstance(offer, dict) and 'price' in offer:
                                price = str(offer['price'])
                                currency = offer.get('priceCurrency', 'USD')
                                price_data['current_price'] = f"{currency}{price}"
                    # Check for aggregateRating/price
                    if 'aggregateOffer' in data:
                        agg_offer = data['aggregateOffer']
                        if isinstance(agg_offer, dict) and 'lowPrice' in agg_offer:
                            price = str(agg_offer['lowPrice'])
                            currency = agg_offer.get('priceCurrency', 'USD')
                            price_data['current_price'] = f"{currency}{price}"
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'offers' in item:
                            offers = item['offers']
                            if isinstance(offers, dict) and 'price' in offers:
                                price = str(offers['price'])
                                currency = offers.get('priceCurrency', 'USD')
                                price_data['current_price'] = f"{currency}{price}"
                                break
            except:
                continue
        
        # Try to find current price with multiple selectors
        current_price = None
        if not price_data['current_price']:
            price_selectors = [
                'span.a-price-whole',
                'span#priceblock_ourprice',
                'span#priceblock_dealprice',
                'span#priceblock_saleprice',
                '.a-price .a-offscreen',
                'span.a-price.a-text-price .a-offscreen',
                '.a-price[data-a-color="base"] .a-offscreen',
                '#priceblock_dealprice',
                '#price',
                '.a-price-symbol + .a-price-whole',
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    # Better regex for price extraction
                    price_match = re.search(r'([₪$€£¥]?\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', price_text)
                    if price_match:
                        current_price = price_match.group(1).strip()
                        # Add currency if missing
                        if not re.match(r'^[₪$€£¥]', current_price):
                            # Try to find currency symbol nearby
                            parent = element.find_parent()
                            if parent:
                                parent_text = parent.get_text()
                                if '$' in parent_text or 'USD' in parent_text:
                                    current_price = '$' + re.sub(r'[^\d.]', '', current_price)
                                elif '€' in parent_text or 'EUR' in parent_text:
                                    current_price = '€' + re.sub(r'[^\d.]', '', current_price)
                                elif '£' in parent_text or 'GBP' in parent_text:
                                    current_price = '£' + re.sub(r'[^\d.]', '', current_price)
                        break
            
            # Try alternative method - look for price in data attributes
            if not current_price:
                price_elements = soup.find_all(['span', 'div'], attrs={'data-a-color': 'price'})
                for elem in price_elements:
                    text = elem.get_text(strip=True)
                    price_match = re.search(r'([₪$€£¥]?\s*\d+[.,]?\d*)', text)
                    if price_match:
                        current_price = price_match.group(1).strip()
                        break
            
            # Look for price in span with class containing "price"
            if not current_price:
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
            '.a-price.a-text-price .a-offscreen',
            '#priceblock_saleprice + span',
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
        final_current = current_price or price_data.get('current_price', '')
        if final_current and original_price:
            try:
                # Extract numbers - handle different formats
                current_clean = re.sub(r'[^\d.]', '', final_current.replace(',', ''))
                original_clean = re.sub(r'[^\d.]', '', original_price.replace(',', ''))
                current_num = float(current_clean)
                original_num = float(original_clean)
                if original_num > current_num and original_num > 0:
                    discount_pct = int(((original_num - current_num) / original_num) * 100)
                    discount = f'{discount_pct}%'
            except:
                pass
        
        price_data['current_price'] = final_current or current_price or '$0'
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
            '#main-image-container img',
            '#imageBlock_feature_div img',
            '#altImages ul li img',
            '.a-dynamic-image',
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img:
                # Try multiple attributes
                for attr in ['src', 'data-src', 'data-old-src', 'data-a-dynamic-image']:
                    src = img.get(attr, '')
                    if src:
                        # Convert relative URLs to absolute
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://www.amazon.com' + src
                        elif not src.startswith('http'):
                            continue
                        
                        # Filter out placeholder images
                        if 'placeholder' not in src.lower() and 'no-image' not in src.lower():
                            # Try to get high-res version
                            if '_AC_' in src or '._' in src:
                                # Replace with higher resolution if possible
                                src = re.sub(r'_AC_[^_]+_', '_AC_SL1500_', src)
                                src = re.sub(r'\._[^_]+_', '._SL1500_', src)
                            return src
        
        # Try to find image in JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for image in various formats
                    if 'image' in data:
                        img_url = data['image']
                        if isinstance(img_url, str):
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            if img_url.startswith('http'):
                                return img_url
                        elif isinstance(img_url, list) and len(img_url) > 0:
                            img_url = img_url[0]
                            if isinstance(img_url, str) and img_url.startswith('http'):
                                return img_url
            except:
                continue
        
        # Try to find in data attributes
        img_elements = soup.find_all('img', attrs={'data-a-image-name': True})
        for img in img_elements:
            for attr in ['data-src', 'src', 'data-old-src']:
                src = img.get(attr, '')
                if src and 'http' in src and 'placeholder' not in src.lower():
                    if src.startswith('//'):
                        src = 'https:' + src
                    return src
        
        # Fallback: find any large image with Amazon CDN
        images = soup.find_all('img', src=re.compile(r'(images-na|images-amazon|ssl-images-amazon)', re.I))
        for img in images:
            src = img.get('src', '')
            if src and 'http' in src:
                if src.startswith('//'):
                    src = 'https:' + src
                # Get high-res version
                src = re.sub(r'_AC_[^_]+_', '_AC_SL1500_', src)
                src = re.sub(r'\._[^_]+_', '._SL1500_', src)
                return src
        
        # Last resort: find any image with .jpg/.png
        images = soup.find_all('img', src=re.compile(r'\.(jpg|jpeg|png|webp)', re.I))
        for img in images:
            src = img.get('src', '')
            if src and 'http' in src and 'placeholder' not in src.lower() and 'logo' not in src.lower():
                if src.startswith('//'):
                    src = 'https:' + src
                return src
        
        return None
    
    def _extract_video_from_vdp_page(self, vdp_url: str) -> Optional[str]:
        """חילוץ סרטון מדף VDP (Video Detail Page)"""
        print("[VDP] Extracting video from VDP page using requests...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = self.session.get(vdp_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find video source in VDP page
            # VDP pages often have video in specific containers
            video_selectors = [
                'video source[src]',
                'video[src]',
                '#video-player source',
                '.video-player source',
                'video source[data-src]',
                '[data-video-src]',
                '[data-video-url]',
            ]
            
            for selector in video_selectors:
                element = soup.select_one(selector)
                if element:
                    for attr in ['src', 'data-src', 'data-video-src', 'data-video-url']:
                        video_url = element.get(attr, '')
                        if video_url:
                            # Clean and normalize URL
                            if video_url.startswith('//'):
                                video_url = 'https:' + video_url
                            elif video_url.startswith('/'):
                                video_url = 'https://www.amazon.com' + video_url
                            
                            if video_url.startswith('http') and ('mp4' in video_url.lower() or 'video' in video_url.lower() or 'm3u8' in video_url.lower()):
                                return video_url
            
            # Try to find in script tags (Amazon often embeds video URLs in JavaScript)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for video URLs in JavaScript
                    video_patterns = [
                        r'"(https?://[^"]*\.mp4[^"]*)"',
                        r'"(https?://[^"]*video[^"]*\.mp4[^"]*)"',
                        r'videoUrl["\']?\s*[:=]\s*["\']([^"\']+\.mp4[^"\']*)',
                        r'source["\']?\s*[:=]\s*["\']([^"\']+\.mp4[^"\']*)',
                    ]
                    for pattern in video_patterns:
                        matches = re.findall(pattern, script.string, re.IGNORECASE)
                        for match in matches:
                            if match.startswith('http'):
                                return match
            
            # Try JSON-LD structured data
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'video' in data:
                            video_data = data['video']
                            if isinstance(video_data, dict):
                                for key in ['contentUrl', 'embedUrl', 'url']:
                                    if key in video_data:
                                        url = video_data[key]
                                        if isinstance(url, str) and url.startswith('http'):
                                            return url
                except:
                    continue
            
        except Exception as e:
            print(f"[!] Error extracting video from VDP page: {e}")
        
        return None
    
    def _extract_product_video(self, soup: BeautifulSoup) -> Optional[str]:
        """חילוץ סרטון מוצר אם קיים מדף מוצר רגיל"""
        # Try to find video in various formats
        video_selectors = [
            'video source',
            '#dv-action-box video',
            '.videoBlock video',
            'iframe[src*="video"]',
            '[data-video-url]',
            'video source[src]',
            'video[src]',
        ]
        
        for selector in video_selectors:
            element = soup.select_one(selector)
            if element:
                # Try different attributes
                for attr in ['src', 'data-src', 'data-video-url', 'data-video', 'data-video-src']:
                    video_url = element.get(attr, '')
                    if video_url:
                        # Clean and normalize URL
                        if video_url.startswith('//'):
                            video_url = 'https:' + video_url
                        elif video_url.startswith('/'):
                            video_url = 'https://www.amazon.com' + video_url
                        
                        if video_url.startswith('http') and ('mp4' in video_url.lower() or 'video' in video_url.lower() or 'm3u8' in video_url.lower()):
                            return video_url
        
        # Try to find in script tags (Amazon often embeds video URLs in JavaScript)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for video URLs in JavaScript
                video_patterns = [
                    r'"(https?://[^"]*\.mp4[^"]*)"',
                    r'"(https?://[^"]*video[^"]*\.mp4[^"]*)"',
                    r'videoUrl["\']?\s*[:=]\s*["\']([^"\']+\.mp4[^"\']*)',
                ]
                for pattern in video_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        if match.startswith('http'):
                            return match
        
        # Try to find in JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'video' in data:
                        video_data = data['video']
                        if isinstance(video_data, dict):
                            for key in ['contentUrl', 'embedUrl', 'url']:
                                if key in video_data:
                                    url = video_data[key]
                                    if isinstance(url, str) and url.startswith('http'):
                                        return url
            except:
                continue
        
        return None
    
    def _extract_all_images(self, soup: BeautifulSoup) -> List[str]:
        """חילוץ כל תמונות המוצר"""
        image_urls = []
        seen_urls = set()
        
        # Try to find all product images in the image gallery
        image_selectors = [
            '#altImages ul li img',
            '#imageBlock_feature_div img',
            '.a-dynamic-image',
            '#main-image-container img',
            '#landingImage',
            '#imgBlkFront',
        ]
        
        for selector in image_selectors:
            images = soup.select(selector)
            for img in images:
                for attr in ['src', 'data-src', 'data-old-src', 'data-a-dynamic-image']:
                    src = img.get(attr, '')
                    if src:
                        # Convert relative URLs to absolute
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://www.amazon.com' + src
                        elif not src.startswith('http'):
                            continue
                        
                        # Filter out placeholder images and normalize
                        if 'placeholder' not in src.lower() and 'no-image' not in src.lower():
                            # Get high-res version
                            if '_AC_' in src or '._' in src:
                                src = re.sub(r'_AC_[^_]+_', '_AC_SL1500_', src)
                                src = re.sub(r'\._[^_]+_', '._SL1500_', src)
                            
                            # Avoid duplicates
                            if src not in seen_urls:
                                seen_urls.add(src)
                                image_urls.append(src)
        
        # Also try JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'image' in data:
                        img_data = data['image']
                        if isinstance(img_data, list):
                            for img_url in img_data:
                                if isinstance(img_url, str) and img_url.startswith('http'):
                                    if img_url not in seen_urls:
                                        seen_urls.add(img_url)
                                        image_urls.append(img_url)
                        elif isinstance(img_data, str) and img_data.startswith('http'):
                            if img_data not in seen_urls:
                                seen_urls.add(img_data)
                                image_urls.append(img_data)
            except:
                continue
        
        # Limit to first 10 images
        return image_urls[:10]
    
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
        """חילוץ תיאור מוצר - משופר עם JSON-LD ו-selectors נוספים"""
        # First, try JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for description
                    if 'description' in data:
                        desc = data['description']
                        if isinstance(desc, str) and len(desc) > 20:
                            return desc[:300] + '...' if len(desc) > 300 else desc
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'description' in item:
                            desc = item['description']
                            if isinstance(desc, str) and len(desc) > 20:
                                return desc[:300] + '...' if len(desc) > 300 else desc
            except:
                continue
        
        # Try to find product description with multiple selectors
        desc_selectors = [
            '#productDescription',
            '#feature-bullets',
            '.product-description',
            '#aplus_feature_div',
            '#productDescription_feature_div',
            '.a-unordered-list.a-vertical.a-spacing-mini',
            '#feature-bullets ul',
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    # Clean up text
                    text = re.sub(r'\s+', ' ', text)
                    # Take first 300 characters
                    return text[:300] + '...' if len(text) > 300 else text
        
        # Try bullet points (most common format)
        bullets = soup.select('#feature-bullets li span.a-list-item')
        if bullets:
            descriptions = []
            for b in bullets[:5]:  # Get up to 5 bullet points
                bullet_text = b.get_text(strip=True)
                if bullet_text and len(bullet_text) > 10:
                    # Skip common non-descriptive bullets
                    if not re.match(r'^(Make sure|Visit|See|Click)', bullet_text, re.I):
                        descriptions.append(bullet_text)
            if descriptions:
                return ' | '.join(descriptions)
        
        # Try alternative bullet point selectors
        alt_bullets = soup.select('ul.a-unordered-list li span')
        if alt_bullets:
            descriptions = []
            for b in alt_bullets[:5]:
                bullet_text = b.get_text(strip=True)
                if bullet_text and len(bullet_text) > 15:
                    descriptions.append(bullet_text)
            if descriptions:
                return ' | '.join(descriptions)
        
        # Try meta description as last resort
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            if len(desc) > 20:
                return desc[:300] + '...' if len(desc) > 300 else desc
        
        return None
    
    def _normalize_affiliate_link(self, affiliate_link: str) -> str:
        """ניקוי ונרמול קישור שותפים לקישור מוצר רגיל"""
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            # Parse URL
            parsed = urlparse(affiliate_link)
            
            # Remove affiliate parameters
            query_params = parse_qs(parsed.query)
            
            # Remove common affiliate parameters
            affiliate_params = ['tag', 'linkId', 'ref', 'creative', 'creativeASIN', 
                              'ascsubtag', 'psc', 'keywords', 'sr']
            for param in affiliate_params:
                query_params.pop(param, None)
            
            # Rebuild URL without affiliate parameters
            new_query = urlencode(query_params, doseq=True) if query_params else ''
            
            # Construct clean URL
            clean_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                ''  # fragment
            ))
            
            return clean_url
        except Exception as e:
            print(f"[!] Error normalizing affiliate link: {e}")
            return affiliate_link
    
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
                'title': 'Advanced Electronic Product',
                'price': '$29.99',
                'original_price': '$39.99',
                'discount': '25%',
                'image_url': 'https://via.placeholder.com/800x800?text=Product+1',
                'rating': 4.5,
                'reviews_count': 1234,
                'affiliate_url': 'https://amazon.com/dp/EXAMPLE123',
                'description': 'High quality product with excellent reviews'
            },
            {
                'title': 'Innovative Gadget',
                'price': '$14.99',
                'original_price': '$19.99',
                'discount': '25%',
                'image_url': 'https://via.placeholder.com/800x800?text=Product+2',
                'rating': 4.8,
                'reviews_count': 567,
                'affiliate_url': 'https://amazon.com/dp/EXAMPLE456',
                'description': 'The perfect solution for your needs'
            }
        ]
    
    def _get_mock_product(self, asin: str) -> Dict:
        """מוצר דמה בודד"""
        return {
            'title': f'Product {asin}',
            'price': '$19.99',
            'original_price': '$24.99',
            'discount': '20%',
            'image_url': 'https://via.placeholder.com/800x800?text=Product',
            'rating': 4.6,
            'reviews_count': 890,
            'affiliate_url': f'https://amazon.com/dp/{asin}',
            'description': 'Recommended product with high quality'
        }


class AliExpressProductFetcher(ProductFetcher):
    """משיכת מוצרים מ-AliExpress Affiliate"""
    
    def __init__(self):
        super().__init__()
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        # AliExpress affiliate tracking parameter
        self.affiliate_tracking = os.getenv('ALIEXPRESS_AFFILIATE_TRACKING', '')
    
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """חיפוש מוצרים ב-AliExpress"""
        try:
            # Use web scraping for AliExpress search
            search_url = f"https://www.aliexpress.com/wholesale?SearchText={quote(keywords)}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try to find product cards in search results
            product_cards = soup.find_all('div', class_=re.compile(r'product-card|item-card|list-item', re.I))
            
            if not product_cards:
                # Fallback: try different selectors
                product_cards = soup.find_all('a', href=re.compile(r'/item/.*\.html'))
            
            for i, card in enumerate(product_cards[:max_results]):
                try:
                    product = self._extract_product_from_card(card)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"[!] Error extracting product {i+1}: {e}")
                    continue
            
            if products:
                return products
            else:
                print("[!] No products found via scraping, using mock data")
                return self._get_mock_products()
                
        except Exception as e:
            print(f"[X] Error fetching from AliExpress: {e}")
            return self._get_mock_products()
    
    def fetch_product_by_url(self, product_url: str) -> Optional[Dict]:
        """משיכת מוצר לפי URL"""
        try:
            # Clean URL and add affiliate tracking if needed
            clean_url = self._clean_affiliate_url(product_url)
            
            print(f"[FETCH] Fetching AliExpress product from: {clean_url}")
            
            # Set better headers for AliExpress
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            response = self.session.get(clean_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Print page title to verify we got the right page
            page_title = soup.find('title')
            if page_title:
                print(f"[DEBUG] Page title: {page_title.get_text(strip=True)[:100]}")
            
            # Extract product information
            product = self._scrape_aliexpress_product(soup, clean_url)
            
            if product:
                print(f"[OK] Successfully scraped AliExpress product: {product.get('title', 'Unknown')}")
                print(f"[OK] Price extracted: {product.get('price', 'N/A')}")
                if not product.get('price') or product.get('price') == '$0':
                    print("[!] WARNING: Price extraction may have failed. Price is missing or $0.")
                return product
            else:
                print("[!] Failed to extract product data, using fallback")
                product_id = self._extract_product_id(clean_url)
                if product_id:
                    return self._get_mock_product(product_id)
                return None
                
        except Exception as e:
            print(f"[X] Error fetching AliExpress product: {e}")
            product_id = self._extract_product_id(product_url)
            if product_id:
                return self._get_mock_product(product_id)
            return None
    
    def _scrape_aliexpress_product(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """חילוץ מידע מוצר מ-AliExpress"""
        try:
            # Extract title
            title = None
            title_selectors = [
                'h1.product-title-text',
                'h1[data-pl="product-title"]',
                'h1',
                '.product-title',
                'meta[property="og:title"]'
            ]
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True) or element.get('content', '')
                    if title:
                        break
            
            # Extract price - AliExpress uses various selectors
            price = None
            
            # Method 1: Try common AliExpress price selectors
            price_selectors = [
                '.price-current',
                '.price-current .notranslate',
                '.price .notranslate',
                '.product-price-value',
                '[data-pl="product-price"]',
                '.price-current-notrans',
                '.price-current .price',
                'span.price',
                '.product-price-current',
                'meta[property="product:price:amount"]',
                'meta[property="og:price:amount"]'
            ]
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True) or element.get('content', '')
                    if price_text:
                        # Extract price value - handle various formats
                        price_match = re.search(r'([\d,]+\.?\d*)', price_text.replace(',', ''))
                        if price_match:
                            price_val = price_match.group(1)
                            # Check for currency symbol
                            if '$' in price_text or 'USD' in price_text.upper():
                                price = f"${price_val}"
                            elif '€' in price_text or 'EUR' in price_text.upper():
                                price = f"€{price_val}"
                            elif '£' in price_text or 'GBP' in price_text.upper():
                                price = f"£{price_val}"
                            else:
                                price = f"${price_val}"  # Default to USD
                        else:
                            price = price_text
                        if price:
                            break
            
            # Method 2: Look for price in script tags (JSON data)
            if not price:
                scripts = soup.find_all('script', type='application/json')
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        # Search recursively for price
                        price = self._find_price_in_json(data)
                        if price:
                            break
                    except:
                        continue
            
            # Method 3: Look for price in window.runParams or similar JavaScript variables
            if not price:
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for price patterns in JavaScript
                        price_patterns = [
                            r'price["\']?\s*[:=]\s*["\']?([\d.]+)',
                            r'currentPrice["\']?\s*[:=]\s*["\']?([\d.]+)',
                            r'productPrice["\']?\s*[:=]\s*["\']?([\d.]+)',
                            r'"price"\s*:\s*"([\d.]+)"',
                            r'"currentPrice"\s*:\s*"([\d.]+)"'
                        ]
                        for pattern in price_patterns:
                            match = re.search(pattern, script.string, re.IGNORECASE)
                            if match:
                                price = f"${match.group(1)}"
                                break
                        if price:
                            break
            
            # Method 4: Look for price in data attributes
            if not price:
                price_elements = soup.find_all(attrs={'data-pl': re.compile(r'price', re.I)})
                for elem in price_elements:
                    price_text = elem.get_text(strip=True)
                    if price_text:
                        price_match = re.search(r'([\d.]+)', price_text.replace(',', ''))
                        if price_match:
                            price = f"${price_match.group(1)}"
                            break
            
            # Method 5: Look for JSON-LD structured data
            if not price:
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                for script in json_ld_scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'offers' in data:
                            offers = data['offers']
                            if isinstance(offers, dict) and 'price' in offers:
                                price_val = offers['price']
                                if isinstance(price_val, (int, float)):
                                    price = f"${price_val:.2f}"
                                elif isinstance(price_val, str):
                                    price_match = re.search(r'([\d.]+)', price_val.replace(',', ''))
                                    if price_match:
                                        price = f"${price_match.group(1)}"
                                break
                    except:
                        continue
            
            # Method 6: Look for price in span/div with specific classes used by AliExpress
            if not price:
                # AliExpress often uses these patterns
                price_patterns = [
                    soup.find('span', class_=re.compile(r'price.*current|current.*price', re.I)),
                    soup.find('span', class_=re.compile(r'product.*price', re.I)),
                    soup.find('div', class_=re.compile(r'price.*current|current.*price', re.I)),
                    soup.find('span', {'id': re.compile(r'price', re.I)}),
                ]
                for elem in price_patterns:
                    if elem:
                        price_text = elem.get_text(strip=True)
                        if price_text:
                            # Remove currency symbols and extract number
                            price_match = re.search(r'([\d,]+\.?\d*)', price_text.replace(',', ''))
                            if price_match:
                                price = f"${price_match.group(1)}"
                                break
            
            # Method 7: Search in all text for price patterns (last resort)
            if not price:
                # Look for common price patterns in the page
                page_text = soup.get_text()
                # Pattern: $XX.XX or USD XX.XX or just numbers that look like prices
                price_patterns = [
                    r'\$\s*(\d+\.?\d*)',
                    r'USD\s*(\d+\.?\d*)',
                    r'(\d+\.\d{2})\s*(?:USD|dollars?)',
                ]
                for pattern in price_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        # Take the first reasonable price (between 0.01 and 10000)
                        for match in matches:
                            try:
                                price_val = float(match)
                                if 0.01 <= price_val <= 10000:
                                    price = f"${price_val:.2f}"
                                    break
                            except:
                                continue
                        if price:
                            break
            
            # Extract original price
            original_price = None
            original_price_selectors = [
                '.price-original',
                '.price-was',
                '[data-pl="product-original-price"]'
            ]
            for selector in original_price_selectors:
                element = soup.select_one(selector)
                if element:
                    original_price_text = element.get_text(strip=True)
                    if original_price_text:
                        price_match = re.search(r'[\d,]+\.?\d*', original_price_text.replace(',', ''))
                        if price_match:
                            original_price = f"${price_match.group()}"
                        break
            
            # Extract image
            image_url = None
            image_selectors = [
                'meta[property="og:image"]',
                '.product-image img',
                'img[data-pl="product-image"]',
                '.images-view img'
            ]
            for selector in image_selectors:
                element = soup.select_one(selector)
                if element:
                    image_url = element.get('content') or element.get('src') or element.get('data-src')
                    if image_url and image_url.startswith('http'):
                        break
            
            # Extract rating
            rating = 0
            rating_element = soup.select_one('.rating-value, .overview-rating-average, [data-pl="rating"]')
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract reviews count
            reviews_count = 0
            reviews_element = soup.select_one('.reviews-count, .review-count, [data-pl="reviews-count"]')
            if reviews_element:
                reviews_text = reviews_element.get_text(strip=True)
                reviews_match = re.search(r'([\d,]+)', reviews_text.replace(',', ''))
                if reviews_match:
                    reviews_count = int(reviews_match.group(1).replace(',', ''))
            
            # Extract description
            description = None
            desc_selectors = [
                'meta[name="description"]',
                'meta[property="og:description"]',
                '.product-description',
                '.detail-desc'
            ]
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element:
                    description = element.get('content') or element.get_text(strip=True)
                    if description:
                        break
            
            # Build affiliate URL
            affiliate_url = self._add_affiliate_tracking(url)
            
            # Debug: Print what we found
            if not price:
                print("[!] WARNING: Could not extract price using any method")
                print(f"[DEBUG] Title found: {title is not None}")
                print(f"[DEBUG] Image found: {image_url is not None}")
                # Try to find any price-like text in the page for debugging
                all_text = soup.get_text()[:500]  # First 500 chars
                print(f"[DEBUG] Sample page text: {all_text[:200]}...")
            
            # Build product dictionary
            product = {
                'title': title or 'AliExpress Product',
                'price': price or '$0',
                'original_price': original_price or '',
                'discount': '',
                'image_url': image_url or '',
                'image_urls': [],
                'video_url': '',
                'rating': rating,
                'reviews_count': reviews_count,
                'affiliate_url': affiliate_url,
                'description': description or 'High quality product from AliExpress'
            }
            
            # Calculate discount if both prices exist
            if original_price and price:
                try:
                    orig_val = float(re.search(r'[\d.]+', original_price.replace(',', '')).group())
                    curr_val = float(re.search(r'[\d.]+', price.replace(',', '')).group())
                    if orig_val > curr_val:
                        discount_pct = int(((orig_val - curr_val) / orig_val) * 100)
                        product['discount'] = f'{discount_pct}%'
                except:
                    pass
            
            return product
            
        except Exception as e:
            print(f"[!] Error scraping AliExpress product: {e}")
            return None
    
    def _find_price_in_json(self, data, depth=0):
        """חיפוש מחיר ב-JSON באופן רקורסיבי"""
        if depth > 5:  # Limit recursion depth
            return None
        
        if isinstance(data, dict):
            # Check common price keys
            for key in ['price', 'currentPrice', 'productPrice', 'salePrice', 'amount']:
                if key in data:
                    val = data[key]
                    if isinstance(val, (int, float)):
                        return f"${val:.2f}"
                    elif isinstance(val, str):
                        price_match = re.search(r'([\d.]+)', val.replace(',', ''))
                        if price_match:
                            return f"${price_match.group(1)}"
            
            # Recursively search in nested dicts
            for value in data.values():
                result = self._find_price_in_json(value, depth + 1)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_price_in_json(item, depth + 1)
                if result:
                    return result
        
        return None
    
    def _extract_product_from_card(self, card) -> Optional[Dict]:
        """חילוץ מידע מוצר מכרטיס מוצר בתוצאות חיפוש"""
        try:
            # This is a simplified extraction - can be improved
            title_elem = card.find(['h3', 'h4', 'a'], class_=re.compile(r'title|name', re.I))
            title = title_elem.get_text(strip=True) if title_elem else None
            
            price_elem = card.find(class_=re.compile(r'price', re.I))
            price = price_elem.get_text(strip=True) if price_elem else None
            
            link_elem = card.find('a', href=re.compile(r'/item/'))
            link = link_elem.get('href') if link_elem else None
            if link and not link.startswith('http'):
                link = f"https://www.aliexpress.com{link}"
            
            if title and link:
                return {
                    'title': title,
                    'price': price or '$0',
                    'affiliate_url': self._add_affiliate_tracking(link) if link else '',
                    'image_url': '',
                    'rating': 0,
                    'reviews_count': 0,
                    'description': ''
                }
        except:
            pass
        return None
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """חילוץ ID מוצר מ-URL של AliExpress"""
        # AliExpress URLs: /item/1234567890.html or /item/1234567890.html?spm=...
        match = re.search(r'/item/(\d+)\.html', url)
        if match:
            return match.group(1)
        return None
    
    def _clean_affiliate_url(self, url: str) -> str:
        """ניקוי URL מקישור שותפים"""
        # Remove affiliate tracking parameters but keep product ID
        parsed = urlparse(url)
        # Keep only essential query parameters
        clean_params = {}
        for key, value in parse_qs(parsed.query).items():
            if key.lower() in ['spm', 'aff_platform', 'aff_trace_key']:
                clean_params[key] = value[0]
        
        clean_query = '&'.join([f"{k}={v}" for k, v in clean_params.items()])
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            clean_url += f"?{clean_query}"
        
        return clean_url
    
    def _add_affiliate_tracking(self, url: str) -> str:
        """הוספת פרמטר שותפים ל-URL"""
        if not self.affiliate_tracking:
            return url
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params['aff_platform'] = ['aff_platform']
        params['aff_trace_key'] = [self.affiliate_tracking]
        
        query = '&'.join([f"{k}={v[0]}" for k, v in params.items()])
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"
    
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
