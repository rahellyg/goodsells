"""
Product Manager - ניהול מוצרים שמורים
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class ProductManager:
    """מחלקה לניהול מוצרים שמורים"""
    
    def __init__(self, storage_file: str = 'products.json'):
        self.storage_file = storage_file
        self.products = []
        self.load_products()
    
    def load_products(self):
        """טעינת מוצרים מקובץ"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.products = data.get('products', [])
            except Exception as e:
                print(f"[!] Error loading products: {e}")
                self.products = []
        else:
            self.products = []
    
    def save_products(self):
        """שמירת מוצרים לקובץ"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'products': self.products
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[!] Error saving products: {e}")
            return False
    
    def add_product(self, product: Dict) -> bool:
        """הוספת מוצר חדש"""
        # בדיקה אם המוצר כבר קיים (לפי ASIN או URL)
        asin = self._extract_asin_from_product(product)
        if asin:
            existing = self.get_product_by_asin(asin)
            if existing:
                # עדכון מוצר קיים - שמירה על נתונים קיימים שלא עודכנו
                index = self.products.index(existing)
                # שמירה על תאריכים
                product['added_at'] = existing.get('added_at', datetime.now().isoformat())
                product['updated_at'] = datetime.now().isoformat()
                # שמירה על נתונים ידניים אם לא עודכנו
                if 'custom_images' in existing and 'custom_images' not in product:
                    product['custom_images'] = existing.get('custom_images', [])
                if 'custom_video' in existing and 'custom_video' not in product:
                    product['custom_video'] = existing.get('custom_video', '')
                if 'custom_description' in existing and 'custom_description' not in product:
                    product['custom_description'] = existing.get('custom_description', '')
                if 'description_hebrew' in existing and 'description_hebrew' not in product:
                    product['description_hebrew'] = existing.get('description_hebrew', '')
                if 'custom_description_hebrew' in existing and 'custom_description_hebrew' not in product:
                    product['custom_description_hebrew'] = existing.get('custom_description_hebrew', '')
                self.products[index] = product
                return self.save_products()
        
        # הוספת מוצר חדש
        product['added_at'] = datetime.now().isoformat()
        product['updated_at'] = datetime.now().isoformat()
        self.products.append(product)
        return self.save_products()
    
    def update_product(self, asin: str, updates: Dict) -> bool:
        """עדכון מוצר קיים"""
        product = self.get_product_by_asin(asin)
        if not product:
            return False
        
        index = self.products.index(product)
        
        # עדכון שדות
        for key, value in updates.items():
            if value is not None and value != '':
                product[key] = value
        
        product['updated_at'] = datetime.now().isoformat()
        self.products[index] = product
        return self.save_products()
    
    def remove_product(self, asin: str) -> bool:
        """הסרת מוצר"""
        product = self.get_product_by_asin(asin)
        if product:
            self.products.remove(product)
            return self.save_products()
        return False
    
    def get_all_products(self) -> List[Dict]:
        """קבלת כל המוצרים"""
        return self.products
    
    def get_product_by_asin(self, asin: str) -> Optional[Dict]:
        """קבלת מוצר לפי ASIN"""
        for product in self.products:
            if self._extract_asin_from_product(product) == asin:
                return product
        return None
    
    def search_products(self, query: str) -> List[Dict]:
        """חיפוש מוצרים"""
        query_lower = query.lower()
        results = []
        for product in self.products:
            title = product.get('title', '').lower()
            description = product.get('description', '').lower()
            if query_lower in title or query_lower in description:
                results.append(product)
        return results
    
    def _extract_asin_from_product(self, product: Dict) -> Optional[str]:
        """חילוץ ASIN ממוצר"""
        # Try from affiliate_url
        affiliate_url = product.get('affiliate_url', '')
        if affiliate_url:
            import re
            match = re.search(r'/dp/([A-Z0-9]{10})', affiliate_url)
            if match:
                return match.group(1)
        
        # Try from ASIN field if exists
        return product.get('asin')
    
    def import_from_file(self, file_path: str) -> int:
        """ייבוא מוצרים מקובץ JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                products_to_import = data if isinstance(data, list) else data.get('products', [])
                
                count = 0
                for product in products_to_import:
                    if self.add_product(product):
                        count += 1
                
                return count
        except Exception as e:
            print(f"[!] Error importing products: {e}")
            return 0
    
    def export_to_file(self, file_path: str) -> bool:
        """ייצוא מוצרים לקובץ JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'count': len(self.products),
                    'products': self.products
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[!] Error exporting products: {e}")
            return False
