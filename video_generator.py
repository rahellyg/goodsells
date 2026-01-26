"""
מודול ליצירת סרטוני שיווק אוטומטיים
Automated Marketing Video Generator Module
"""
# -*- coding: utf-8 -*-
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import (
    ImageClip, TextClip, CompositeVideoClip, 
    AudioFileClip, concatenate_videoclips, ColorClip
)
from typing import Dict, Optional
import tempfile
from io import BytesIO
import textwrap


class VideoGenerator:
    """מחלקה ליצירת סרטוני שיווק אוטומטיים"""
    
    def __init__(self, output_dir: str = 'output_videos', temp_dir: str = 'temp_files'):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.video_duration = 8  # 8 שניות
        self.video_size = (1080, 1920)  # פורמט אנכי (TikTok/Instagram Reels)
        
        # יצירת תיקיות אם לא קיימות
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def download_image(self, url: str) -> Optional[str]:
        """הורדת תמונת מוצר או יצירת תמונה דמה"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # שמירה זמנית
            temp_path = os.path.join(self.temp_dir, f"product_{hash(url)}.jpg")
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return temp_path
        except Exception as e:
            print(f"[!] Error downloading image from {url}, creating placeholder...")
            # יצירת תמונה דמה במקום
            return self._create_placeholder_image()
    
    def _create_placeholder_image(self) -> str:
        """יצירת תמונת דמה מעניינת יותר"""
        # יצירת תמונה גדולה יותר עם גרדיאנט
        width, height = 1000, 1000
        img = Image.new('RGB', (width, height), color=(40, 40, 60))
        draw = ImageDraw.Draw(img)
        
        # ציור מלבן עם מסגרת
        border = 50
        draw.rectangle(
            [border, border, width - border, height - border],
            fill=(60, 80, 120),
            outline=(200, 200, 220),
            width=10
        )
        
        # ציור אייקון מוצר (מלבן עם קווים)
        center_x, center_y = width // 2, height // 2
        box_size = 300
        draw.rectangle(
            [center_x - box_size//2, center_y - box_size//2, 
             center_x + box_size//2, center_y + box_size//2],
            fill=(100, 120, 160),
            outline=(255, 255, 255),
            width=5
        )
        
        # קווים פנימיים
        draw.line([center_x - box_size//2, center_y, center_x + box_size//2, center_y], 
                  fill=(255, 255, 255), width=3)
        draw.line([center_x, center_y - box_size//2, center_x, center_y + box_size//2], 
                  fill=(255, 255, 255), width=3)
        
        # הוספת טקסט
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 50)
            except:
                font = ImageFont.load_default()
        
        text = "מוצר"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_y = center_y + box_size//2 + 40
        position = ((width - text_width) // 2, text_y)
        
        # Outline לטקסט
        for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((position[0] + adj[0], position[1] + adj[1]), text, 
                     font=font, fill=(0, 0, 0))
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        # שמירה
        temp_path = os.path.join(self.temp_dir, "placeholder_product.jpg")
        img.save(temp_path)
        return temp_path
    
    def create_product_video(self, product: Dict, output_filename: Optional[str] = None) -> Optional[str]:
        """יצירת סרטון שיווק למוצר"""
        try:
            print(f"[VIDEO] Creating video for: {product.get('title', 'Unknown Product')}")
            
            # הורדת תמונת מוצר
            image_path = self.download_image(product.get('image_url', ''))
            if not image_path:
                print("[X] Failed to download product image")
                return None
            
            # יצירת תמונות עם טקסט באמצעות PIL
            title_img_path = self._create_title_image(product.get('title', 'מוצר מומלץ'))
            price_img_path = self._create_price_image(
                price=product.get('price', '₪0'),
                original_price=product.get('original_price', ''),
                discount=product.get('discount', ''),
                rating=product.get('rating', 0),
                reviews_count=product.get('reviews_count', 0)
            )
            cta_img_path = self._create_cta_image("לחץ עכשיו!")
            
            # יצירת קליפים מתמונות
            clips = []
            
            # 1. תמונת מוצר עם אנימציה (0-5 שניות) - מוצגת יותר זמן
            product_clip = self._create_product_image_clip(image_path, duration=5)
            clips.append(product_clip)
            
            # 2. כותרת מוצר (2-4 שניות) - למעלה, מופיעה על תמונת המוצר
            title_clip = ImageClip(title_img_path).set_duration(2).set_start(2).set_position(('center', 100))
            clips.append(title_clip)
            
            # 3. מחיר והנחה (4-7 שניות) - למטה, מופיע על תמונת המוצר
            price_clip = ImageClip(price_img_path).set_duration(3).set_start(4).set_position(('center', self.video_size[1] - 400))
            clips.append(price_clip)
            
            # 4. קריאה לפעולה (7-8 שניות) - למטה מאוד
            cta_clip = ImageClip(cta_img_path).set_duration(1).set_start(7).set_position(('center', self.video_size[1] - 200))
            clips.append(cta_clip)
            
            # יצירת רקע
            background = ColorClip(size=self.video_size, color=(0, 0, 0), duration=self.video_duration)
            
            # חיבור כל הקליפים
            final_video = CompositeVideoClip(
                [background] + clips,
                size=self.video_size
            ).set_duration(self.video_duration)
            
            # שמירת הסרטון
            if not output_filename:
                safe_title = "".join(c for c in product.get('title', 'product')[:30] if c.isalnum() or c in (' ', '-', '_'))
                output_filename = f"{safe_title.replace(' ', '_')}.mp4"
            
            output_path = os.path.join(self.output_dir, output_filename)
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4
            )
            
            # ניקוי קבצים זמניים
            temp_files = [image_path, title_img_path, price_img_path, cta_img_path]
            for temp_file in temp_files:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            print(f"[OK] Video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[X] Error creating video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_product_image_clip(self, image_path: str, duration: float) -> ImageClip:
        """יצירת קליפ תמונת מוצר עם אנימציה"""
        # טעינת תמונה
        img = Image.open(image_path)
        
        # שינוי גודל תוך שמירה על יחס גובה-רוחב - גדול יותר כדי שיהיה בולט
        max_width = self.video_size[0] - 200
        max_height = self.video_size[1] - 600  # משאיר מקום לטקסטים
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # יצירת תמונה בגודל הסרטון עם רקע שחור
        bg = Image.new('RGB', self.video_size, color=(20, 20, 20))  # רקע כהה
        x = (bg.width - img.width) // 2
        y = (bg.height - img.height) // 2 - 100  # מעט למעלה מהמרכז
        bg.paste(img, (x, y))
        
        # שמירה זמנית
        temp_path = os.path.join(self.temp_dir, f"product_bg_{hash(image_path)}.jpg")
        bg.save(temp_path)
        
        # יצירת קליפ
        clip = ImageClip(temp_path).set_duration(duration).set_position('center')
        
        return clip
    
    def _create_title_image(self, title: str) -> str:
        """יצירת תמונת כותרת באמצעות PIL"""
        # פיצול טקסט לשורות
        max_chars_per_line = 25
        wrapped_title = '\n'.join(textwrap.wrap(title, width=max_chars_per_line))
        
        # יצירת תמונה
        img = Image.new('RGBA', (self.video_size[0] - 100, 200), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # טעינת פונט
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
        
        # ציור טקסט עם outline
        lines = wrapped_title.split('\n')
        y_offset = 20
        for line in lines:
            # Outline (שחור)
            for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((50 + adj[0], y_offset + adj[1]), line, font=font, fill=(0, 0, 0, 255))
            # טקסט (לבן)
            draw.text((50, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += 70
        
        # שמירה
        temp_path = os.path.join(self.temp_dir, f"title_{hash(title)}.png")
        img.save(temp_path)
        return temp_path
    
    def _create_price_image(self, price: str, original_price: str, discount: str,
                           rating: float = 0, reviews_count: int = 0) -> str:
        """יצירת תמונת מחיר באמצעות PIL"""
        # יצירת תמונה
        img = Image.new('RGBA', (self.video_size[0] - 100, 300), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # טעינת פונט
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
            font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
        except:
            try:
                font_large = ImageFont.truetype("arial.ttf", 50)
                font_small = ImageFont.truetype("arial.ttf", 40)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        y_pos = 20
        
        # מחיר נוכחי
        price_text = f"מחיר: {price}"
        if original_price:
            price_text += f"\nבמקום {original_price}"
        if discount:
            price_text += f" ({discount} הנחה!)"
        
        lines = price_text.split('\n')
        for line in lines:
            # Outline
            for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((50 + adj[0], y_pos + adj[1]), line, font=font_large, fill=(0, 0, 0, 255))
            # טקסט ירוק
            draw.text((50, y_pos), line, font=font_large, fill=(0, 255, 0, 255))
            y_pos += 60
        
        # דירוג (אם קיים)
        if rating > 0:
            rating_text = f"* {rating} ({reviews_count} ביקורות)"
            # Outline
            for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((50 + adj[0], y_pos + adj[1]), rating_text, font=font_small, fill=(0, 0, 0, 255))
            # טקסט צהוב
            draw.text((50, y_pos), rating_text, font=font_small, fill=(255, 255, 0, 255))
        
        # שמירה
        temp_path = os.path.join(self.temp_dir, f"price_{hash(price)}.png")
        img.save(temp_path)
        return temp_path
    
    def _create_cta_image(self, text: str) -> str:
        """יצירת תמונת קריאה לפעולה באמצעות PIL"""
        # יצירת תמונה
        img = Image.new('RGBA', (self.video_size[0] - 100, 150), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # טעינת פונט
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 70)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 70)
            except:
                font = ImageFont.load_default()
        
        # Outline (לבן)
        for adj in [(-3,-3), (-3,3), (3,-3), (3,3)]:
            draw.text((50 + adj[0], 40 + adj[1]), text, font=font, fill=(255, 255, 255, 255))
        
        # טקסט (אדום)
        draw.text((50, 40), text, font=font, fill=(255, 0, 0, 255))
        
        # שמירה
        temp_path = os.path.join(self.temp_dir, f"cta_{hash(text)}.png")
        img.save(temp_path)
        return temp_path
    
