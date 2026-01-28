// Products page JavaScript

// Load saved products on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSavedProducts();
    
    // Allow Enter key to trigger search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProducts();
            }
        });
    }
});

// Load saved products
async function loadSavedProducts() {
    const loading = document.getElementById('loadingSaved');
    const grid = document.getElementById('savedProductsGrid');
    const noProducts = document.getElementById('noSavedProducts');
    
    if (loading) loading.style.display = 'block';
    if (grid) grid.innerHTML = '';
    if (noProducts) noProducts.style.display = 'none';
    
    try {
        const response = await fetch('/api/products/saved');
        const data = await response.json();
        
        if (loading) loading.style.display = 'none';
        
        if (data.success && data.products && data.products.length > 0) {
            displayProducts(data.products, grid);
            if (noProducts) noProducts.style.display = 'none';
            
            // Update count
            const countElement = document.getElementById('savedProductsCount');
            if (countElement) {
                countElement.textContent = `(${data.products.length} מוצרים)`;
            }
        } else {
            if (grid) grid.innerHTML = '';
            if (noProducts) noProducts.style.display = 'block';
            
            // Update count
            const countElement = document.getElementById('savedProductsCount');
            if (countElement) {
                countElement.textContent = '(0 מוצרים)';
            }
        }
    } catch (error) {
        console.error('Error loading saved products:', error);
        if (loading) loading.style.display = 'none';
        if (noProducts) noProducts.style.display = 'block';
    }
}

// Display products in grid
function displayProducts(products, gridElement) {
    if (!gridElement) return;
    
    gridElement.innerHTML = '';
    
    products.forEach(product => {
        const productCard = createProductCard(product);
        gridElement.appendChild(productCard);
    });
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
    
    // Extract ASIN for product detail link
    const asin = extractASIN(product);
    const detailLink = asin ? `/product/${asin}` : '#';
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${title}" class="product-image" onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
        <div class="product-info">
            <h3 class="product-title">
                <a href="${detailLink}" style="color: inherit; text-decoration: none; cursor: pointer;" 
                   onmouseover="this.style.color='#667eea'" 
                   onmouseout="this.style.color='inherit'">${title}</a>
            </h3>
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
                <a href="${affiliateUrl}" target="_blank" class="btn btn-success" style="flex: 1; text-align: center; text-decoration: none;">
                    <i class="fas fa-shopping-cart"></i> קנה עכשיו
                </a>
                <button onclick="generateVideo('${title}', ${JSON.stringify(product).replace(/'/g, "&#39;")})" class="btn btn-secondary">
                    <i class="fas fa-video"></i> צור סרטון
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Extract ASIN from product
function extractASIN(product) {
    const url = product.affiliate_url || '';
    const match = url.match(/\/dp\/([A-Z0-9]{10})/);
    return match ? match[1] : '';
}

// Search products function
async function searchProducts() {
    const searchInput = document.getElementById('searchInput');
    const keywords = searchInput.value.trim();
    const searchType = document.querySelector('input[name="searchType"]:checked')?.value || 'keywords';
    const store = document.querySelector('input[name="store"]:checked')?.value || 'amazon';
    
    if (!keywords) {
        alert('אנא הזן מילות חיפוש');
        return;
    }
    
    const loading = document.getElementById('loading');
    const productsGrid = document.getElementById('productsGrid');
    const searchResultsSection = document.getElementById('searchResultsSection');
    
    if (loading) loading.style.display = 'block';
    if (productsGrid) productsGrid.innerHTML = '';
    if (searchResultsSection) searchResultsSection.style.display = 'block';
    
    // Scroll to search results
    if (searchResultsSection) {
        searchResultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    try {
        let response;
        
        if (searchType === 'url') {
            response = await fetch('/api/product/url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: keywords, store: store })
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
                    store: store,
                    count: 20
                })
            });
        }
        
        const data = await response.json();
        
        if (loading) loading.style.display = 'none';
        
        if (data.success && data.products) {
            displayProducts(data.products, productsGrid);
        } else if (data.product) {
            // Single product result
            displayProducts([data.product], productsGrid);
        } else {
            if (productsGrid) {
                productsGrid.innerHTML = '<p style="text-align: center; padding: 2rem;">לא נמצאו מוצרים</p>';
            }
        }
    } catch (error) {
        console.error('Error searching products:', error);
        if (loading) loading.style.display = 'none';
        if (productsGrid) {
            productsGrid.innerHTML = '<p style="text-align: center; padding: 2rem; color: #dc3545;">שגיאה בחיפוש מוצרים</p>';
        }
    }
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
