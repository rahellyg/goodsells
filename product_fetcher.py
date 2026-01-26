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
from urllib.parse import quote

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
        """משיכת מוצר לפי URL"""
        # Extract ASIN from URL
        asin = self._extract_asin(product_url)
        if not asin:
            return None
        
        # In a real implementation, you would use Amazon API here
        # For now, return mock data
        return self._get_mock_product(asin)
    
    def _extract_asin(self, url: str) -> Optional[str]:
        """חילוץ ASIN מ-URL של Amazon"""
        import re
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        match = re.search(r'/gp/product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        return None
    
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


def get_fetcher(store: str = 'amazon') -> ProductFetcher:
    """Factory function לקבלת fetcher לפי חנות"""
    if store.lower() == 'amazon':
        return AmazonProductFetcher()
    elif store.lower() == 'aliexpress':
        return AliExpressProductFetcher()
    else:
        raise ValueError(f"Unknown store: {store}. Supported: 'amazon', 'aliexpress'")
