"""
Flask Web Application for Amazon Affiliate Product Showcase
"""
# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from product_fetcher import get_fetcher

def detect_store_from_url(url: str) -> str:
    """זיהוי אוטומטי של חנות לפי URL"""
    if not url:
        return 'amazon'
    
    url_lower = url.lower()
    if 'aliexpress.com' in url_lower or 'aliexpress' in url_lower:
        return 'aliexpress'
    elif 'ebay.com' in url_lower or 'ebay' in url_lower:
        return 'ebay'
    elif 'amazon.com' in url_lower or 'amazon.' in url_lower or 'amzn.to' in url_lower:
        return 'amazon'
    else:
        # Default to Amazon
        return 'amazon'
from video_generator import VideoGenerator
from product_manager import ProductManager

import threading
import time

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'output_videos'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize components
video_generator = VideoGenerator()
product_fetcher = None
product_manager = ProductManager()


# Video generation queue
video_queue = {}
video_status = {}


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/products')
def products():
    """Products listing page"""
    return render_template('products.html')


@app.route('/manage')
def manage_products():
    """Product management page"""
    return render_template('manage.html')


@app.route('/featured')
def featured_products():
    """Featured products page - מוצרים מומלצים"""
    return render_template('featured.html')


@app.route('/callback-config')
def callback_config():
    """Affiliate callback configuration page"""
    return render_template('callback_config.html')


@app.route('/product/<asin>')
def product_detail(asin):
    """Product detail page"""
    return render_template('product_detail.html', asin=asin)


@app.route('/api/search', methods=['POST'])
def search_products():
    """Search for products"""
    try:
        data = request.json
        keywords = data.get('keywords', '')
        store = data.get('store', 'amazon')
        count = data.get('count', 10)
        
        if not keywords:
            return jsonify({'error': 'Keywords required'}), 400
        
        print(f"[API] Searching {store} for: {keywords}")
        
        try:
            fetcher = get_fetcher(store)
        except Exception as fetcher_error:
            print(f"[API] Error creating fetcher for {store}: {fetcher_error}")
            return jsonify({
                'error': f'Store "{store}" is not available: {str(fetcher_error)}',
                'store': store
            }), 400
        
        products = fetcher.search_products(keywords, max_results=count)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        print(f"[API] Error in search_products: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/product/<asin>')
def get_product(asin):
    """Get product by ASIN - first try saved products, then fetch from Amazon"""
    try:
        # First try to get from saved products
        product = product_manager.get_product_by_asin(asin)
        if product:
            return jsonify({
                'success': True,
                'product': product
            })
        
        # If not found in saved products, try to fetch from Amazon
        fetcher = get_fetcher('amazon')
        product_url = f'https://www.amazon.com/dp/{asin}'
        product = fetcher.fetch_product_by_url(product_url)
        
        if product:
            return jsonify({
                'success': True,
                'product': product
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/product/url', methods=['POST'])
def get_product_by_url():
    """Get product by URL - auto-detects store"""
    try:
        data = request.json
        product_url = data.get('url', '')
        store = data.get('store', '')  # Allow manual store selection
        
        if not product_url:
            return jsonify({'error': 'URL required'}), 400
        
        # Auto-detect store if not provided
        if not store:
            store = detect_store_from_url(product_url)
            print(f"[API] Auto-detected store: {store}")
        
        fetcher = get_fetcher(store)
        product = fetcher.fetch_product_by_url(product_url)
        
        if product:
            return jsonify({
                'success': True,
                'product': product,
                'store': store
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/generate', methods=['POST'])
def generate_video():
    """Generate video for a product"""
    try:
        data = request.json
        product = data.get('product')
        asin = data.get('asin')
        
        if not product and not asin:
            return jsonify({'error': 'Product data or ASIN required'}), 400
        
        # If only ASIN provided, fetch product
        if not product and asin:
            fetcher = get_fetcher('amazon')
            product_url = f'https://www.amazon.com/dp/{asin}'
            product = fetcher.fetch_product_by_url(product_url)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
        
        # Generate unique ID for this video generation
        video_id = f"{product.get('title', 'product')}_{int(time.time())}"
        video_id = "".join(c for c in video_id[:50] if c.isalnum() or c in (' ', '-', '_'))
        video_id = video_id.replace(' ', '_')
        
        # Set status to processing
        video_status[video_id] = {
            'status': 'processing',
            'message': 'Video generation started...'
        }
        
        # Generate video in background thread
        def generate():
            try:
                video_path = video_generator.create_product_video(product)
                if video_path:
                    filename = os.path.basename(video_path)
                    video_status[video_id] = {
                        'status': 'completed',
                        'message': 'Video generated successfully',
                        'filename': filename,
                        'path': video_path
                    }
                else:
                    video_status[video_id] = {
                        'status': 'failed',
                        'message': 'Video generation failed'
                    }
            except Exception as e:
                video_status[video_id] = {
                    'status': 'failed',
                    'message': f'Error: {str(e)}'
                }
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'message': 'Video generation started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/status/<video_id>')
def video_status_check(video_id):
    """Check video generation status"""
    status = video_status.get(video_id, {'status': 'not_found'})
    return jsonify(status)


@app.route('/api/videos')
def list_videos():
    """List all generated videos"""
    try:
        videos_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(videos_dir):
            return jsonify({'videos': []})
        
        videos = []
        for filename in os.listdir(videos_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(videos_dir, filename)
                file_size = os.path.getsize(filepath)
                videos.append({
                    'filename': filename,
                    'size': file_size,
                    'url': url_for('serve_video', filename=filename)
                })
        
        return jsonify({'videos': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve video files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/category', methods=['POST'])
def get_category_products():
    """Get products from category page"""
    try:
        data = request.json
        category_url = data.get('url', '')
        max_products = data.get('max_products', 20)
        
        if not category_url:
            return jsonify({'error': 'Category URL required'}), 400
        
        fetcher = get_fetcher('amazon')
        products = fetcher.fetch_products_from_category(category_url, max_products=max_products)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/recommended', methods=['POST'])
def get_recommended_products():
    """Get smart recommended products with good commissions from AliExpress"""
    try:
        data = request.json or {}
        category = data.get('category', 'electronics')
        count = min(int(data.get('count', 20)), 50)
        
        print(f"[SMART AGENT] Searching for recommended {category} products...")
        
        # Keywords for different categories with high commission potential
        category_keywords = {
            'electronics': ['wireless earbuds', 'smart watch', 'phone accessories', 'bluetooth speaker'],
            'fashion': ['sunglasses', 'jewelry', 'watch', 'bag'],
            'home': ['led lights', 'kitchen gadgets', 'home decor', 'organizer'],
            'sports': ['fitness tracker', 'yoga mat', 'sports bottle', 'resistance bands'],
            'beauty': ['makeup brush', 'skincare', 'hair accessories', 'nail art'],
            'toys': ['educational toys', 'puzzle', 'building blocks', 'remote control'],
        }
        
        keywords_list = category_keywords.get(category, ['popular items', 'trending', 'best seller'])
        
        # Use AliExpress API to get products
        try:
            fetcher = get_fetcher('aliexpress')
            all_products = []
            
            # Search multiple keywords to get variety
            for keyword in keywords_list[:2]:  # Limit to 2 keywords to avoid API limits
                print(f"[SMART AGENT] Searching: {keyword}")
                products = fetcher.search_products(keyword, max_results=count // 2)
                all_products.extend(products)
            
            # Smart filtering: prefer products with good metrics
            scored_products = []
            for product in all_products:
                score = 0
                
                # Get price
                price_str = product.get('price', '$0')
                try:
                    price = float(price_str.replace('$', '').replace(',', ''))
                except:
                    price = 0
                
                # Scoring logic for commission potential
                # 1. Price range (sweet spot: $10-$100)
                if 10 <= price <= 100:
                    score += 30
                elif 5 <= price < 10 or 100 < price <= 200:
                    score += 20
                elif price > 200:
                    score += 10
                
                # 2. Discount (higher discount = better deal)
                discount_str = product.get('discount', '0%')
                try:
                    discount = int(discount_str.replace('%', ''))
                    score += min(discount, 40)  # Max 40 points for discount
                except:
                    pass
                
                # 3. Has image (quality indicator)
                if product.get('image_url'):
                    score += 10
                
                # 4. Has original price (shows deal)
                if product.get('original_price'):
                    score += 10
                
                scored_products.append({
                    'product': product,
                    'score': score
                })
            
            # Sort by score
            scored_products.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top products
            recommended = [item['product'] for item in scored_products[:count]]
            
            print(f"[SMART AGENT] Found {len(recommended)} recommended products")
            
            return jsonify({
                'success': True,
                'products': recommended,
                'count': len(recommended),
                'category': category
            })
            
        except Exception as api_error:
            print(f"[SMART AGENT] API Error: {api_error}")
            return jsonify({
                'error': f'Could not fetch recommended products: {str(api_error)}',
                'success': False
            }), 500
            
    except Exception as e:
        print(f"[SMART AGENT] Error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


# Product Management API
@app.route('/api/products/saved', methods=['GET'])
def get_saved_products():
    """Get all saved products"""
    try:
        products = product_manager.get_all_products()
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/add', methods=['POST'])
def add_product():
    """Add product to saved list - supports regular URLs and affiliate links"""
    try:
        data = request.json
        product_url = data.get('url', '')
        affiliate_link = data.get('affiliate_link', '')  # Support affiliate_link parameter
        product_data = data.get('product')
        
        # Use affiliate_link if provided, otherwise use url
        if affiliate_link and not product_url:
            product_url = affiliate_link
            print("[API] Received affiliate link")
        
        # If URL provided, fetch product
        if product_url and not product_data:
            # Auto-detect store from URL
            store = detect_store_from_url(product_url)
            print(f"[API] Auto-detected store: {store} for URL: {product_url[:50]}...")
            
            fetcher = get_fetcher(store)
            
            # Check if it's an affiliate link
            is_affiliate = False
            if store == 'amazon':
                is_affiliate = 'tag=' in product_url or 'linkId=' in product_url or 'ref=' in product_url
            elif store == 'aliexpress':
                is_affiliate = 'aff_platform' in product_url or 'aff_trace_key' in product_url
            
            if is_affiliate:
                print("[API] Processing affiliate link...")
            
            product_data = fetcher.fetch_product_by_url(product_url)
            if not product_data:
                return jsonify({'error': f'Failed to fetch product from {store}. Make sure the URL is valid.'}), 400
        
        if not product_data:
            return jsonify({'error': 'Product data or URL required'}), 400
        
        # Add product
        success = product_manager.add_product(product_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Product added successfully',
                'product': product_data,
                'is_affiliate': 'tag=' in (product_url or '') or 'linkId=' in (product_url or '')
            })
        else:
            return jsonify({'error': 'Failed to save product'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/remove/<asin>', methods=['DELETE'])
def remove_product(asin):
    """Remove product from saved list"""
    try:
        success = product_manager.remove_product(asin)
        if success:
            return jsonify({'success': True, 'message': 'Product removed'})
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/search', methods=['POST'])
def search_saved_products():
    """Search saved products"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            products = product_manager.get_all_products()
        else:
            products = product_manager.search_products(query)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/import', methods=['POST'])
def import_products():
    """Import products from file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        # Import products
        count = product_manager.import_from_file(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return jsonify({
            'success': True,
            'message': f'Imported {count} products',
            'count': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/export', methods=['GET'])
def export_products():
    """Export products to file"""
    try:
        import tempfile
        tmp_path = tempfile.mktemp(suffix='.json')
        
        success = product_manager.export_to_file(tmp_path)
        
        if success:
            from flask import send_file
            return send_file(tmp_path, as_attachment=True, download_name='products_export.json')
        else:
            return jsonify({'error': 'Failed to export products'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/update/<asin>', methods=['PUT', 'PATCH'])
def update_product(asin):
    """Update product fields (name, description, images, video)"""
    try:
        data = request.json
        
        # Prepare updates
        updates = {}
        
        if 'title' in data:
            updates['title'] = data['title']
        if 'description' in data:
            updates['description'] = data['description']
        if 'custom_description' in data:
            updates['custom_description'] = data['custom_description']
        if 'description_hebrew' in data:
            updates['description_hebrew'] = data['description_hebrew']
        if 'custom_description_hebrew' in data:
            updates['custom_description_hebrew'] = data['custom_description_hebrew']
        if 'image_url' in data:
            updates['image_url'] = data['image_url']
        if 'custom_images' in data:
            updates['custom_images'] = data['custom_images']
        if 'video_url' in data:
            updates['video_url'] = data['video_url']
        if 'custom_video' in data:
            updates['custom_video'] = data['custom_video']
        if 'price' in data:
            updates['price'] = data['price']
        if 'original_price' in data:
            updates['original_price'] = data['original_price']
        if 'discount' in data:
            updates['discount'] = data['discount']
        
        success = product_manager.update_product(asin, updates)
        
        if success:
            updated_product = product_manager.get_product_by_asin(asin)
            return jsonify({
                'success': True,
                'message': 'Product updated successfully',
                'product': updated_product
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/upload-image', methods=['POST'])
def upload_image():
    """Upload product image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create uploads directory
        uploads_dir = 'static/uploads/images'
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        import uuid
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)
        
        # Return URL
        image_url = url_for('static', filename=f'uploads/images/{filename}')
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/upload-video', methods=['POST'])
def upload_video():
    """Upload product video"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
            return jsonify({'error': 'Invalid video format. Supported: mp4, mov, avi, webm'}), 400
        
        # Create uploads directory
        uploads_dir = 'static/uploads/videos'
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        import uuid
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)
        
        # Return URL
        video_url = url_for('static', filename=f'uploads/videos/{filename}')
        
        return jsonify({
            'success': True,
            'url': video_url,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text to Hebrew using Google Translate API (free)"""
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target', 'he')  # Hebrew
        
        if not text:
            return jsonify({'error': 'Text required'}), 400
        
        # Use Google Translate API (free tier)
        # You can also use other translation services
        import requests
        
        # Using LibreTranslate (free and open source)
        # Alternative: use Google Cloud Translate API (requires API key)
        
        # Simple approach: Use a free translation service
        translate_url = 'https://libretranslate.de/translate'
        
        try:
            response = requests.post(translate_url, json={
                'q': text,
                'source': 'en',
                'target': 'he',
                'format': 'text'
            }, timeout=10)
            
            if response.status_code == 200:
                translated = response.json().get('translatedText', '')
                return jsonify({
                    'success': True,
                    'original': text,
                    'translated': translated
                })
        except:
            pass
        
        # Fallback: Use a simple translation service or return placeholder
        # For production, use Google Cloud Translate API with API key
        return jsonify({
            'success': False,
            'error': 'Translation service unavailable. Please enter Hebrew description manually.',
            'message': 'אנא הזן תיאור בעברית ידנית'
        }), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aliexpress/callback', methods=['GET', 'POST'])
def aliexpress_callback():
    """
    AliExpress Affiliate API Callback Endpoint
    
    This endpoint receives callbacks from AliExpress affiliate system.
    Use this URL in your AliExpress affiliate app configuration.
    
    URL Format: https://yourdomain.com/api/aliexpress/callback
    """
    try:
        # Log the callback for debugging
        print("[ALIEXPRESS CALLBACK] Received callback from AliExpress")
        
        if request.method == 'POST':
            data = request.json or request.form.to_dict()
            print(f"[CALLBACK DATA] {data}")
        else:  # GET
            data = request.args.to_dict()
            print(f"[CALLBACK PARAMS] {data}")
        
        # Extract common AliExpress callback parameters
        order_id = data.get('order_id') or data.get('orderId')
        commission = data.get('commission')
        status = data.get('status')
        
        # Store or process the callback data as needed
        callback_log = {
            'timestamp': time.time(),
            'method': request.method,
            'data': data,
            'order_id': order_id,
            'commission': commission,
            'status': status
        }
        
        # You can save this to a database or file
        print(f"[CALLBACK LOG] {callback_log}")
        
        return jsonify({
            'success': True,
            'message': 'Callback received successfully',
            'callback_id': str(int(time.time()))
        }), 200
        
    except Exception as e:
        print(f"[ERROR] AliExpress callback error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/aliexpress/webhook', methods=['POST'])
def aliexpress_webhook():
    """
    AliExpress Webhook Endpoint for order notifications
    
    URL Format: https://yourdomain.com/api/aliexpress/webhook
    """
    try:
        data = request.json or {}
        
        print("[ALIEXPRESS WEBHOOK] Received webhook")
        print(f"[WEBHOOK DATA] {data}")
        
        # Process webhook data
        event_type = data.get('event_type') or data.get('type')
        
        return jsonify({
            'success': True,
            'message': 'Webhook processed',
            'event_type': event_type
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Webhook error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/callback-url', methods=['GET'])
def get_callback_url():
    """
    Get the callback URLs for affiliate programs
    
    Returns the full callback URLs based on the current domain
    """
    try:
        # Get the base URL from the request
        base_url = request.url_root.rstrip('/')
        
        # If running locally, provide ngrok instructions
        is_local = 'localhost' in base_url or '127.0.0.1' in base_url
        
        callback_urls = {
            'aliexpress': {
                'callback': f"{base_url}/api/aliexpress/callback",
                'webhook': f"{base_url}/api/aliexpress/webhook"
            },
            'base_url': base_url,
            'is_local': is_local
        }
        
        if is_local:
            callback_urls['note'] = 'You are running locally. For testing with real callbacks, use ngrok or deploy to a public server.'
            callback_urls['ngrok_example'] = 'Run: ngrok http 5000, then use the https URL provided'
        
        return jsonify(callback_urls), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('output_videos', exist_ok=True)
    os.makedirs('temp_files', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/uploads/images', exist_ok=True)
    os.makedirs('static/uploads/videos', exist_ok=True)
    
    print("=" * 60)
    print("Amazon Affiliate Product Showcase")
    print("=" * 60)
    print("\nStarting web server...")
    
    # Support for deployment platforms (Render, Railway, Heroku, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    if port == 5000:
        print("Open your browser and go to: http://localhost:5000")
    else:
        print(f"Server running on port: {port}")
    
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=debug, host='0.0.0.0', port=port)


