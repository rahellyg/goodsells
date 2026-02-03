/**
 * Featured Products Page JavaScript
 * מוצרים מומלצים
 */

let allProducts = [];
let filteredProducts = [];
let isSmartMode = false; // Track if we're showing smart recommendations

// Load featured products when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadFeaturedProducts();
    
    // Add event listeners for filters
    document.getElementById('storeFilter').addEventListener('change', applyFilters);
    document.getElementById('sortFilter').addEventListener('change', applyFilters);
    document.getElementById('priceFilter').addEventListener('change', applyFilters);
});

/**
 * Load smart recommendations from AI agent
 * Gets top 50 recommended products for affiliate program
 */
async function loadSmartRecommendations() {
    const loading = document.getElementById('loading');
    const grid = document.getElementById('featuredProductsGrid');
    const noProducts = document.getElementById('noProducts');
    
    loading.style.display = 'block';
    grid.innerHTML = '';
    noProducts.style.display = 'none';
    isSmartMode = true;
    
    try {
        const response = await fetch('/api/products/recommended', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                count: 50
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.products && data.products.length > 0) {
            allProducts = data.products;
            filteredProducts = [...allProducts];
            applyFilters();
            updateStats();
            
            // Show success message
            showNotification(`✨ נמצאו ${data.products.length} מוצרים מומלצים לתוכנית השותפים!`, 'success');
        } else {
            noProducts.style.display = 'block';
            showNotification('לא נמצאו מוצרים מומלצים. נסה שוב מאוחר יותר.', 'warning');
        }
    } catch (error) {
        console.error('Error loading smart recommendations:', error);
        showNotification('שגיאה בטעינת מוצרים מומלצים: ' + error.message, 'error');
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #e74c3c;"><i class="fas fa-exclamation-triangle"></i> שגיאה בטעינת המוצרים</div>';
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Get category name in Hebrew
 */
function getCategoryName(category) {
    const names = {
        'electronics': 'אלקטרוניקה',
        'fashion': 'אופנה',
        'home': 'בית ומטבח',
        'sports': 'ספורט',
        'beauty': 'יופי',
        'toys': 'צעצועים'
    };
    return names[category] || category;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideDown 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

/**
 * Load all saved products
 */
async function loadFeaturedProducts() {
    const loading = document.getElementById('loading');
    const grid = document.getElementById('featuredProductsGrid');
    const noProducts = document.getElementById('noProducts');
    
    loading.style.display = 'block';
    grid.innerHTML = '';
    noProducts.style.display = 'none';
    isSmartMode = false;
    
    try {
        const response = await fetch('/api/products/saved');
        const data = await response.json();
        
        if (data.products && data.products.length > 0) {
            allProducts = data.products;
            filteredProducts = [...allProducts];
            applyFilters();
            updateStats();
        } else {
            noProducts.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading products:', error);
        grid.innerHTML = '<div style="text-align: center; padding: 2rem; color: #e74c3c;"><i class="fas fa-exclamation-triangle"></i> שגיאה בטעינת המוצרים</div>';
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Apply filters and sorting
 */
function applyFilters() {
    const storeFilter = document.getElementById('storeFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    const priceFilter = document.getElementById('priceFilter').value;
    
    // Filter by store
    filteredProducts = allProducts.filter(product => {
        if (storeFilter === 'all') return true;
        
        const url = product.affiliate_url || '';
        if (storeFilter === 'amazon') {
            return url.includes('amazon.com');
        } else if (storeFilter === 'aliexpress') {
            return url.includes('aliexpress.com');
        }
        return true;
    });
    
    // Filter by price
    if (priceFilter !== 'all') {
        filteredProducts = filteredProducts.filter(product => {
            const price = parseFloat((product.price || '0').replace(/[^0-9.]/g, ''));
            
            if (priceFilter === '0-20') return price >= 0 && price <= 20;
            if (priceFilter === '20-50') return price > 20 && price <= 50;
            if (priceFilter === '50-100') return price > 50 && price <= 100;
            if (priceFilter === '100+') return price > 100;
            return true;
        });
    }
    
    // Sort products
    filteredProducts.sort((a, b) => {
        const priceA = parseFloat((a.price || '0').replace(/[^0-9.]/g, ''));
        const priceB = parseFloat((b.price || '0').replace(/[^0-9.]/g, ''));
        
        switch(sortFilter) {
            case 'price-low':
                return priceA - priceB;
            case 'price-high':
                return priceB - priceA;
            case 'rating':
                return (b.rating || 0) - (a.rating || 0);
            case 'discount':
                const discountA = parseFloat((a.discount || '0').replace('%', ''));
                const discountB = parseFloat((b.discount || '0').replace('%', ''));
                return discountB - discountA;
            default:
                return 0;
        }
    });
    
    renderProducts();
}

/**
 * Render products to the grid
 */
function renderProducts() {
    const grid = document.getElementById('featuredProductsGrid');
    const noProducts = document.getElementById('noProducts');
    
    if (filteredProducts.length === 0) {
        grid.innerHTML = '';
        noProducts.style.display = 'block';
        return;
    }
    
    noProducts.style.display = 'none';
    grid.innerHTML = '';
    
    filteredProducts.forEach(product => {
        const card = createProductCard(product);
        grid.appendChild(card);
    });
}

/**
 * Create a product card element
 */
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const imageUrl = product.image_url || 'https://via.placeholder.com/300x300?text=No+Image';
    const price = product.price || '$0';
    const originalPrice = product.original_price || '';
    const discount = product.discount || '';
    const rating = product.rating || 0;
    const reviews = product.reviews_count || 0;
    
    // Determine store
    const url = product.affiliate_url || '';
    let storeBadge = '';
    if (url.includes('amazon.com')) {
        storeBadge = '<span class="store-badge" style="background: #FF9900; color: white; padding: 0.25rem 0.5rem; border-radius: 3px; font-size: 0.75rem;"><i class="fab fa-amazon"></i> Amazon</span>';
    } else if (url.includes('aliexpress.com')) {
        storeBadge = '<span class="store-badge" style="background: #FF6A00; color: white; padding: 0.25rem 0.5rem; border-radius: 3px; font-size: 0.75rem;"><i class="fas fa-shopping-cart"></i> AliExpress</span>';
    }
    
    card.innerHTML = `
        <div class="product-image">
            <img src="${imageUrl}" alt="${product.title || 'Product'}" onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
            ${discount ? `<span class="discount-badge">${discount}</span>` : ''}
            <div style="position: absolute; top: 10px; left: 10px;">
                ${storeBadge}
            </div>
        </div>
        <div class="product-info">
            <h3 class="product-title">${product.title || 'Untitled Product'}</h3>
            <div class="product-price">
                <span class="current-price">${price}</span>
                ${originalPrice ? `<span class="original-price">${originalPrice}</span>` : ''}
            </div>
            ${rating > 0 ? `
            <div class="product-rating">
                <i class="fas fa-star" style="color: #ffd700;"></i> ${rating.toFixed(1)}
                ${reviews > 0 ? `<span style="color: #999;">(${reviews.toLocaleString()} ביקורות)</span>` : ''}
            </div>
            ` : ''}
            ${product.description ? `
            <p class="product-description" style="font-size: 0.9rem; color: #666; margin: 0.5rem 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                ${product.description.substring(0, 100)}...
            </p>
            ` : ''}
            <a href="${product.affiliate_url || '#'}" 
               class="btn btn-primary" 
               target="_blank" 
               rel="nofollow sponsored"
               onclick="logCommission(event, ${JSON.stringify(product).replace(/"/g, '&quot;')})"
               style="width: 100%; margin-top: 1rem;">
                <i class="fas fa-shopping-cart"></i> קנה עכשיו
            </a>
        </div>
    `;
    
    return card;
}

/**
 * Update statistics
 */
function updateStats() {
    const totalProducts = document.getElementById('totalProducts');
    const avgDiscount = document.getElementById('avgDiscount');
    const avgRating = document.getElementById('avgRating');
    
    // Total products
    totalProducts.textContent = allProducts.length;
    
    // Average discount
    const discounts = allProducts
        .filter(p => p.discount)
        .map(p => parseFloat(p.discount.replace('%', '')));
    
    if (discounts.length > 0) {
        const avg = discounts.reduce((a, b) => a + b, 0) / discounts.length;
        avgDiscount.textContent = Math.round(avg) + '%';
    } else {
        avgDiscount.textContent = '0%';
    }
    
    // Average rating
    const ratings = allProducts
        .filter(p => p.rating && p.rating > 0)
        .map(p => p.rating);
    
    if (ratings.length > 0) {
        const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        avgRating.textContent = avg.toFixed(1);
    } else {
        avgRating.textContent = '0';
    }
}

/**
 * Log commission information when clicking on a product
 */
function logCommission(event, product) {
    // Calculate commission based on store and price
    const price = parseFloat((product.price || '0').replace(/[^\d.]/g, ''));
    const url = product.affiliate_url || '';
    
    let commissionRate = 0;
    let store = 'Unknown';
    let affiliateId = 'NOT FOUND';
    let hasAffiliateId = false;
    
    if (url.includes('amazon.com')) {
        commissionRate = 3; // Amazon typical rate is 1-10% depending on category, avg ~3%
        store = 'Amazon';
        
        // Extract Amazon Associate Tag from URL
        const tagMatch = url.match(/[?&]tag=([^&]+)/);
        if (tagMatch) {
            affiliateId = decodeURIComponent(tagMatch[1]);
            hasAffiliateId = true;
        }
    } else if (url.includes('aliexpress.com')) {
        commissionRate = 8; // AliExpress typical rate is 5-12%, avg ~8%
        store = 'AliExpress';
        
        // Extract AliExpress tracking ID from URL
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
