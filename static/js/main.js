// Main JavaScript for product showcase

// Search products function
async function searchProducts() {
    const searchInput = document.getElementById('searchInput');
    const keywords = searchInput.value.trim();
    const searchType = document.querySelector('input[name="searchType"]:checked')?.value || 'keywords';
    
    if (!keywords) {
        alert('אנא הזן מילות חיפוש');
        return;
    }
    
    const loading = document.getElementById('loading');
    const productsGrid = document.getElementById('productsGrid');
    const productsSection = document.getElementById('productsSection');
    
    if (loading) loading.style.display = 'block';
    if (productsGrid) productsGrid.innerHTML = '';
    if (productsSection) productsSection.style.display = 'block';
    
    try {
        let response;
        
        if (searchType === 'url') {
            response = await fetch('/api/product/url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: keywords })
            });
        } else if (searchType === 'category') {
            response = await fetch('/api/category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: keywords, max_products: 20 })
            });
        } else {
            response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    keywords: keywords,
                    store: 'amazon',
                    count: 20
                })
            });
        }
        
        const data = await response.json();
        
        if (loading) loading.style.display = 'none';
        
        if (data.success && data.products) {
            displayProducts(data.products);
        } else if (data.product) {
            // Single product result
            displayProducts([data.product]);
        } else {
            alert('לא נמצאו מוצרים');
        }
    } catch (error) {
        console.error('Error searching products:', error);
        if (loading) loading.style.display = 'none';
        alert('שגיאה בחיפוש מוצרים');
    }
}

// Display products in grid
function displayProducts(products) {
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) return;
    
    productsGrid.innerHTML = '';
    
    products.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}

// Extract ASIN from product
function extractASIN(product) {
    const url = product.affiliate_url || '';
    const match = url.match(/\/dp\/([A-Z0-9]{10})/);
    return match ? match[1] : '';
}

// Create product card element
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const imageUrl = product.image_url || 'https://via.placeholder.com/300x300?text=No+Image';
    const title = product.title || 'מוצר ללא שם';
    // השתמש במחיר המקורי של אמזון אם קיים, אחרת במחיר הנוכחי
    const price = product.amazon_original_price || product.price || '$0';
    const originalPrice = product.original_price || '';
    const discount = product.discount || '';
    const rating = product.rating || 0;
    const reviewsCount = product.reviews_count || 0;
    const affiliateUrl = product.affiliate_url || '#';
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${title}" class="product-image" onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
        <div class="product-info">
            <h3 class="product-title">${title}</h3>
            <div class="product-price">
                <span class="price-current">${price}</span>
                ${originalPrice ? `<span class="price-original">${originalPrice}</span>` : ''}
                ${discount ? `<span class="discount-badge">${discount} הנחה</span>` : ''}
            </div>
            ${rating > 0 ? `
                <div class="product-rating">
                    <i class="fas fa-star"></i>
                    <span>${rating} (${reviewsCount.toLocaleString()} ביקורות)</span>
                </div>
            ` : ''}
            <div class="product-actions">
                <a href="${affiliateUrl}" target="_blank" class="btn btn-success affiliate-link" onclick="logCommission(event, ${JSON.stringify(product).replace(/"/g, '&quot;')})" style="flex: 1; text-align: center; text-decoration: none;">
                    <i class="fas fa-shopping-cart"></i> קנה עכשיו
                </a>
                <button onclick="generateVideo('${product.title}', ${JSON.stringify(product).replace(/'/g, "&#39;")})" class="btn btn-secondary">
                    <i class="fas fa-video"></i> צור סרטון
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Generate video for product
async function generateVideo(productTitle, product) {
    if (!product) {
        alert('שגיאה: אין נתוני מוצר');
        return;
    }
    
    const confirmed = confirm(`ליצור סרטון שיווק עבור "${productTitle}"?\nזה עשוי לקחת כמה דקות.`);
    if (!confirmed) return;
    
    try {
        const response = await fetch('/api/video/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product: product })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('יצירת הסרטון החלה! זה עשוי לקחת כמה דקות.\nתוכל לבדוק את הסטטוס מאוחר יותר.');
            // Optionally poll for status
            checkVideoStatus(data.video_id);
        } else {
            alert('שגיאה ביצירת הסרטון: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error generating video:', error);
        alert('שגיאה ביצירת הסרטון');
    }
}

// Check video generation status
async function checkVideoStatus(videoId) {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;
    
    const checkInterval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`/api/video/status/${videoId}`);
            const status = await response.json();
            
            if (status.status === 'completed') {
                clearInterval(checkInterval);
                alert(`הסרטון נוצר בהצלחה!\n${status.filename}`);
            } else if (status.status === 'failed') {
                clearInterval(checkInterval);
                alert('יצירת הסרטון נכשלה: ' + status.message);
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                alert('זמן יצירת הסרטון פג. נסה שוב מאוחר יותר.');
            }
        } catch (error) {
            console.error('Error checking video status:', error);
        }
    }, 5000); // Check every 5 seconds
}

// Allow Enter key to trigger search
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProducts();
            }
        });
    }
});

/**
 * Log commission information when clicking on a product
 */
function logCommission(event, product) {
    // Calculate commission based on store and price
    const price = parseFloat((product.price || product.amazon_original_price || '0').replace(/[^\d.]/g, ''));
    const url = product.affiliate_url || '';
    
    let commissionRate = 0;
    let store = 'Unknown';
    let affiliateId = 'NOT FOUND';
    let hasAffiliateId = false;
    
    if (url.includes('amazon.com')) {
        commissionRate = 3;
        store = 'Amazon';
        const tagMatch = url.match(/[?&]tag=([^&]+)/);
        if (tagMatch) {
            affiliateId = decodeURIComponent(tagMatch[1]);
            hasAffiliateId = true;
        }
    } else if (url.includes('aliexpress.com')) {
        commissionRate = 8;
        store = 'AliExpress';
        const trackingMatch = url.match(/[?&]aff_trace_key=([^&]+)/);
        if (trackingMatch) {
            affiliateId = decodeURIComponent(trackingMatch[1]);
            hasAffiliateId = true;
        }
    }
    
    const commissionAmount = (price * commissionRate / 100).toFixed(2);
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎯 AFFILIATE COMMISSION INFO');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log(`📦 Product: ${product.title || 'N/A'}`);
    console.log(`🏪 Store: ${store}`);
    console.log(`💰 Price: $${price.toFixed(2)}`);
    console.log(`📊 Commission Rate: ${commissionRate}%`);
    console.log(`✅ Estimated Commission: $${commissionAmount}`);
    console.log('');
    console.log('🔑 AFFILIATE ID CHECK:');
    
    if (hasAffiliateId) {
        console.log(`✅ Affiliate ID Found: ${affiliateId}`);
        console.log(`💵 You WILL receive commission when user buys!`);
        console.log(`🔗 URL contains your tracking ID`);
    } else {
        console.log(`❌ NO Affiliate ID Found!`);
        console.log(`⚠️ You will NOT receive commission!`);
        console.log(`🔧 Check your .env file and make sure:`);
        if (store === 'Amazon') {
            console.log(`   AMAZON_ASSOCIATE_TAG is set correctly`);
        } else if (store === 'AliExpress') {
            console.log(`   ALIEXPRESS_AFFILIATE_TRACKING is set correctly`);
        }
    }
    
    console.log('');
    console.log('📋 Full URL:');
    console.log(url);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
}
