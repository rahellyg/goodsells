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
    AudioFileClip, concatenate_videoclips, ColorClip, VideoClip
)
from moviepy.video.fx.all import fadein, fadeout
from typing import Dict, Optional, List
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
        if not url or 'placeholder' in url.lower():
            print("[!] Invalid or placeholder image URL, creating placeholder image...")
            return self._create_placeholder_image()
        
        try:
            # Set headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Referer': 'https://www.amazon.com/',
            }
            
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"[!] URL does not point to an image (content-type: {content_type}), creating placeholder...")
                return self._create_placeholder_image()
            
            # שמירה זמנית
            temp_path = os.path.join(self.temp_dir, f"product_{abs(hash(url))}.jpg")
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify the file was created and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path
            else:
                print("[!] Downloaded file is empty, creating placeholder...")
                return self._create_placeholder_image()
                
        except Exception as e:
            print(f"[!] Error downloading image from {url}: {e}")
            print("[!] Creating placeholder image instead...")
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
        
        text = "Product"
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
            
            # Check if product has a video
            video_url = product.get('video_url', '')
            if video_url:
                print("[VIDEO] Using product video from Amazon")
                return self._create_video_from_product_video(product, video_url, output_filename)
            
            # Check if product has multiple images for slideshow
            image_urls = product.get('image_urls', [])
            if not image_urls:
                # Fallback to single image
                image_urls = [product.get('image_url', '')]
            
            if len(image_urls) > 1:
                print(f"[VIDEO] Creating slideshow from {len(image_urls)} product images")
                return self._create_video_from_images_slideshow(product, image_urls, output_filename)
            else:
                print("[VIDEO] Creating video from single product image")
                return self._create_video_from_single_image(product, image_urls[0] if image_urls else '', output_filename)
        except Exception as e:
            print(f"[X] Error creating product video: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_video_from_product_video(self, product: Dict, video_url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """יצירת סרטון מסרטון המוצר"""
        try:
            from moviepy.editor import VideoFileClip
            
            # Download product video
            print(f"[DOWNLOAD] Downloading product video...")
            video_path = self.download_video(video_url)
            if not video_path:
                print("[!] Failed to download product video, falling back to images")
                return self._create_video_from_images_slideshow(product, product.get('image_urls', []), output_filename)
            
            # Load video clip
            product_video = VideoFileClip(video_path)
            
            # Resize and crop to fit vertical format
            product_video = product_video.resize(height=self.video_size[1])
            if product_video.w > self.video_size[0]:
                product_video = product_video.crop(x_center=product_video.w/2, width=self.video_size[0])
            
            # Limit duration to 8 seconds
            if product_video.duration > self.video_duration:
                product_video = product_video.subclip(0, self.video_duration)
            else:
                # Loop video if shorter than 8 seconds
                loops_needed = int(self.video_duration / product_video.duration) + 1
                product_video = concatenate_videoclips([product_video] * loops_needed).subclip(0, self.video_duration)
            
            product_video = product_video.set_fps(30)
            
            # Add text overlays (same as image version)
            clips = [product_video]
            clips.extend(self._create_text_overlays(product))
            
            # Create final video
            final_video = CompositeVideoClip(clips, size=self.video_size).set_duration(self.video_duration).set_fps(30)
            
            # Save video
            if not output_filename:
                safe_title = "".join(c for c in product.get('title', 'product')[:30] if c.isalnum() or c in (' ', '-', '_'))
                output_filename = f"{safe_title.replace(' ', '_')}.mp4"
            
            output_path = os.path.join(self.output_dir, output_filename)
            final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='medium', threads=4, logger=None)
            
            # Cleanup
            final_video.close()
            product_video.close()
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass
            
            print(f"[OK] Video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[!] Error using product video: {e}")
            print("[!] Falling back to images")
            return self._create_video_from_images_slideshow(product, product.get('image_urls', []), output_filename)
    
    def _create_video_from_images_slideshow(self, product: Dict, image_urls: List[str], output_filename: Optional[str] = None) -> Optional[str]:
        """יצירת סרטון מסליידשואו של תמונות"""
        try:
            # Download all images
            image_paths = []
            for i, url in enumerate(image_urls[:5]):  # Limit to 5 images
                print(f"[DOWNLOAD] Downloading image {i+1}/{min(len(image_urls), 5)}...")
                img_path = self.download_image(url)
                if img_path:
                    image_paths.append(img_path)
            
            if not image_paths:
                print("[X] Failed to download any images")
                return None
            
            # Create clips from images
            clips = []
            duration_per_image = self.video_duration / len(image_paths)
            
            for i, img_path in enumerate(image_paths):
                clip = self._create_product_image_clip_with_zoom(img_path, duration=duration_per_image)
                clip = clip.set_start(i * duration_per_image)
                clips.append(clip)
            
            # Add text overlays
            text_clips = self._create_text_overlays(product)
            clips.extend(text_clips)
            
            # Create final video
            final_video = CompositeVideoClip(clips, size=self.video_size).set_duration(self.video_duration).set_fps(30)
            
            # Save video
            if not output_filename:
                safe_title = "".join(c for c in product.get('title', 'product')[:30] if c.isalnum() or c in (' ', '-', '_'))
                output_filename = f"{safe_title.replace(' ', '_')}.mp4"
            
            output_path = os.path.join(self.output_dir, output_filename)
            final_video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='medium', threads=4, logger=None)
            
            # Cleanup
            final_video.close()
            for clip in clips:
                if hasattr(clip, 'close'):
                    try:
                        clip.close()
                    except:
                        pass
            
            print(f"[OK] Video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[X] Error creating slideshow: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_video_from_single_image(self, product: Dict, image_url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """יצירת סרטון מתמונה בודדת (השיטה הישנה)"""
        try:
            print(f"[VIDEO] Creating video for: {product.get('title', 'Unknown Product')}")
            
            # Download product image
            image_path = self.download_image(image_url)
            if not image_path:
                print("[X] Failed to download product image")
                return None
            
            # יצירת תמונות עם טקסט באמצעות PIL
            title_img_path = self._create_title_image(product.get('title', 'Recommended Product'))
            price_img_path = self._create_price_image(
                price=product.get('price', '₪0'),
                original_price=product.get('original_price', ''),
                discount=product.get('discount', ''),
                rating=product.get('rating', 0),
                reviews_count=product.get('reviews_count', 0)
            )
            cta_img_path = self._create_cta_image("Shop Now!")
            
            # יצירת קליפים מתמונות
            clips = []
            
            # 1. תמונת מוצר עם אנימציית זום (0-8 שניות) - רקע לכל הסרטון
            product_clip = self._create_product_image_clip_with_zoom(image_path, duration=self.video_duration)
            clips.append(product_clip)
            
            # 2. Sales hook text (0-2 seconds) - Attention grabber
            hook_text = self._create_sales_hook_text(product)
            if hook_text:
                hook_clip = ImageClip(hook_text, duration=2).set_start(0).set_position(('center', 150)).set_fps(30)
                hook_clip = fadein(hook_clip, 0.5)
                hook_clip = fadeout(hook_clip, 0.5)
                clips.append(hook_clip)
            
            # 3. Product title (1.5-4 seconds) - Top, appears over product image
            title_clip = ImageClip(title_img_path, duration=2.5).set_start(1.5).set_position(('center', 100)).set_fps(30)
            title_clip = fadein(title_clip, 0.3)
            title_clip = fadeout(title_clip, 0.3)
            clips.append(title_clip)
            
            # 4. Price and discount (3.5-7 seconds) - Bottom, appears over product image
            price_clip = ImageClip(price_img_path, duration=3.5).set_start(3.5).set_position(('center', self.video_size[1] - 400)).set_fps(30)
            price_clip = fadein(price_clip, 0.4)
            price_clip = fadeout(price_clip, 0.4)
            clips.append(price_clip)
            
            # 5. Call to action (6.5-8 seconds) - Bottom, with animation
            cta_clip = ImageClip(cta_img_path, duration=1.5).set_start(6.5).set_position(('center', self.video_size[1] - 200)).set_fps(30)
            cta_clip = fadein(cta_clip, 0.3)
            clips.append(cta_clip)
            
            # 6. Urgency text (6-8 seconds) - Limited time offer
            urgency_text = self._create_urgency_text()
            if urgency_text:
                urgency_clip = ImageClip(urgency_text, duration=2).set_start(6).set_position(('center', 250)).set_fps(30)
                urgency_clip = fadein(urgency_clip, 0.3)
                clips.append(urgency_clip)
            
            # יצירת רקע (לא נחוץ כי תמונת המוצר כבר מכסה)
            # background = ColorClip(size=self.video_size, color=(0, 0, 0), duration=self.video_duration).set_fps(30)
            
            # חיבור כל הקליפים
            final_video = CompositeVideoClip(
                clips,  # No background needed - product image is the background
                size=self.video_size
            ).set_duration(self.video_duration).set_fps(30)
            
            # שמירת הסרטון
            if not output_filename:
                safe_title = "".join(c for c in product.get('title', 'product')[:30] if c.isalnum() or c in (' ', '-', '_'))
                output_filename = f"{safe_title.replace(' ', '_')}.mp4"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Ensure all clips are properly sized and have fps
            for clip in clips:
                if hasattr(clip, 'size') and clip.size != self.video_size:
                    clip = clip.resize(self.video_size)
            
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4,
                logger=None  # Suppress verbose output
            )
            
            # Close the video to free resources
            final_video.close()
            for clip in clips:
                if hasattr(clip, 'close'):
                    try:
                        clip.close()
                    except:
                        pass
            
            # Cleanup temporary files
            temp_files = [image_path, title_img_path, price_img_path, cta_img_path]
            # Add hook and urgency text files if they exist
            hook_path = self._create_sales_hook_text(product) if product else None
            urgency_path = self._create_urgency_text()
            if hook_path:
                temp_files.append(hook_path)
            if urgency_path:
                temp_files.append(urgency_path)
            
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
    
    def _create_text_overlays(self, product: Dict) -> List:
        """יצירת כל הטקסטים העל-גבייים"""
        clips = []
        
        # Create text images
        title_img_path = self._create_title_image(product.get('title', 'Recommended Product'))
        price_img_path = self._create_price_image(
            price=product.get('price', '$0'),
            original_price=product.get('original_price', ''),
            discount=product.get('discount', ''),
            rating=product.get('rating', 0),
            reviews_count=product.get('reviews_count', 0)
        )
        cta_img_path = self._create_cta_image("Shop Now!")
        
        # Sales hook text
        hook_text = self._create_sales_hook_text(product)
        if hook_text:
            hook_clip = ImageClip(hook_text, duration=2).set_start(0).set_position(('center', 150)).set_fps(30)
            hook_clip = fadein(hook_clip, 0.5)
            hook_clip = fadeout(hook_clip, 0.5)
            clips.append(hook_clip)
        
        # Product title
        title_clip = ImageClip(title_img_path, duration=2.5).set_start(1.5).set_position(('center', 100)).set_fps(30)
        title_clip = fadein(title_clip, 0.3)
        title_clip = fadeout(title_clip, 0.3)
        clips.append(title_clip)
        
        # Price and discount
        price_clip = ImageClip(price_img_path, duration=3.5).set_start(3.5).set_position(('center', self.video_size[1] - 400)).set_fps(30)
        price_clip = fadein(price_clip, 0.4)
        price_clip = fadeout(price_clip, 0.4)
        clips.append(price_clip)
        
        # Call to action
        cta_clip = ImageClip(cta_img_path, duration=1.5).set_start(6.5).set_position(('center', self.video_size[1] - 200)).set_fps(30)
        cta_clip = fadein(cta_clip, 0.3)
        clips.append(cta_clip)
        
        # Urgency text
        urgency_text = self._create_urgency_text()
        if urgency_text:
            urgency_clip = ImageClip(urgency_text, duration=2).set_start(6).set_position(('center', 250)).set_fps(30)
            urgency_clip = fadein(urgency_clip, 0.3)
            clips.append(urgency_clip)
        
        return clips
    
    def download_video(self, url: str) -> Optional[str]:
        """הורדת סרטון מוצר"""
        if not url:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.amazon.com/',
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if it's actually a video
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('video/'):
                print(f"[!] URL does not point to a video (content-type: {content_type})")
                return None
            
            # Save temporarily
            temp_path = os.path.join(self.temp_dir, f"product_video_{abs(hash(url))}.mp4")
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path
            else:
                return None
                
        except Exception as e:
            print(f"[!] Error downloading video: {e}")
            return None
    
    def _create_product_image_clip_with_zoom(self, image_path: str, duration: float) -> ImageClip:
        """יצירת קליפ תמונת מוצר עם אנימציית זום"""
        # טעינת תמונה
        img = Image.open(image_path)
        
        # יצירת תמונה גדולה יותר לזום
        zoom_factor = 1.2  # 20% zoom in
        large_width = int(self.video_size[0] * zoom_factor)
        large_height = int(self.video_size[1] * zoom_factor)
        
        # שינוי גודל תוך שמירה על יחס גובה-רוחב
        img.thumbnail((large_width, large_height), Image.Resampling.LANCZOS)
        
        # יצירת תמונה גדולה עם רקע שחור
        bg = Image.new('RGB', (large_width, large_height), color=(20, 20, 20))
        x = (bg.width - img.width) // 2
        y = (bg.height - img.height) // 2 - 100
        bg.paste(img, (x, y))
        
        # שמירה זמנית
        temp_path = os.path.join(self.temp_dir, f"product_bg_{abs(hash(image_path))}.jpg")
        bg.save(temp_path)
        
        # יצירת קליפ עם אנימציית זום
        base_clip = ImageClip(temp_path).set_duration(duration).set_fps(30)
        
        # אנימציית זום - מתחיל גדול ומתקרב (Ken Burns effect)
        # Use resize with a function that changes over time
        def zoom_func(t):
            # Start at 1.0, end at 0.85 (zooms in 15% over duration)
            return 1.0 - (t / duration) * 0.15
        
        # Apply zoom effect
        zoom_clip = base_clip.resize(zoom_func)
        zoom_clip = zoom_clip.set_position('center')
        
        return zoom_clip
    
    def _create_product_image_clip(self, image_path: str, duration: float) -> ImageClip:
        """יצירת קליפ תמונת מוצר עם אנימציה (legacy method)"""
        return self._create_product_image_clip_with_zoom(image_path, duration)
    
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
        
        # Current price
        price_text = f"Price: {price}"
        if original_price:
            price_text += f"\nWas {original_price}"
        if discount:
            price_text += f" ({discount} OFF!)"
        
        lines = price_text.split('\n')
        for line in lines:
            # Outline
            for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((50 + adj[0], y_pos + adj[1]), line, font=font_large, fill=(0, 0, 0, 255))
            # טקסט ירוק
            draw.text((50, y_pos), line, font=font_large, fill=(0, 255, 0, 255))
            y_pos += 60
        
        # Rating (if available)
        if rating > 0:
            rating_text = f"⭐ {rating} ({reviews_count:,} reviews)"
            # Outline
            for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((50 + adj[0], y_pos + adj[1]), rating_text, font=font_small, fill=(0, 0, 0, 255))
            # טקסט צהוב
            draw.text((50, y_pos), rating_text, font=font_small, fill=(255, 255, 0, 255))
        
        # שמירה
        temp_path = os.path.join(self.temp_dir, f"price_{hash(price)}.png")
        img.save(temp_path)
        return temp_path
    
    def _create_sales_hook_text(self, product: Dict) -> Optional[str]:
        """יצירת טקסט למשיכת תשומת לב"""
        hooks = [
            "🔥 HOT DEAL!",
            "⚡ LIMITED TIME!",
            "💥 BEST PRICE!",
            "🎯 DON'T MISS OUT!",
        ]
        
        # Choose hook based on discount
        discount = product.get('discount', '')
        if discount:
            hook = hooks[0] if '25' in discount or '30' in discount or '40' in discount else hooks[1]
        else:
            hook = hooks[2]
        
        # Create image with hook text
        img = Image.new('RGBA', (self.video_size[0] - 200, 120), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 55)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 55)
            except:
                font = ImageFont.load_default()
        
        # Red background with white text
        bbox = draw.textbbox((0, 0), hook, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw background rectangle
        padding = 15
        draw.rectangle(
            [(100 - padding, 20 - padding), (100 + text_width + padding, 20 + text_height + padding)],
            fill=(255, 0, 0, 230),  # Red with transparency
            outline=(255, 255, 255, 255),
            width=3
        )
        
        # Draw text
        for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((100 + adj[0], 20 + adj[1]), hook, font=font, fill=(0, 0, 0, 255))
        draw.text((100, 20), hook, font=font, fill=(255, 255, 255, 255))
        
        temp_path = os.path.join(self.temp_dir, f"hook_{abs(hash(hook))}.png")
        img.save(temp_path)
        return temp_path
    
    def _create_urgency_text(self) -> Optional[str]:
        """יצירת טקסט דחיפות"""
        urgency_text = "⏰ LIMITED TIME OFFER!"
        
        img = Image.new('RGBA', (self.video_size[0] - 200, 100), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 45)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 45)
            except:
                font = ImageFont.load_default()
        
        # Yellow/orange background
        bbox = draw.textbbox((0, 0), urgency_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        padding = 12
        draw.rectangle(
            [(100 - padding, 30 - padding), (100 + text_width + padding, 30 + text_height + padding)],
            fill=(255, 165, 0, 220),  # Orange with transparency
            outline=(255, 255, 255, 255),
            width=2
        )
        
        # Draw text
        for adj in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            draw.text((100 + adj[0], 30 + adj[1]), urgency_text, font=font, fill=(0, 0, 0, 255))
        draw.text((100, 30), urgency_text, font=font, fill=(255, 255, 255, 255))
        
        temp_path = os.path.join(self.temp_dir, f"urgency_{abs(hash(urgency_text))}.png")
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
    
