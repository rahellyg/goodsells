// Product detail page JavaScript

async function loadProductDetail() {
    const productDetail = document.getElementById('productDetail');
    const loading = document.getElementById('loading');
    
    if (!asin) {
        productDetail.innerHTML = '<p>שגיאה: אין ASIN</p>';
        return;
    }
    
    try {
        const response = await fetch(`/api/product/${asin}`);
        const data = await response.json();
        
        if (loading) loading.style.display = 'none';
        
        if (data.success && data.product) {
            displayProductDetail(data.product);
        } else {
            productDetail.innerHTML = '<p>מוצר לא נמצא</p>';
        }
    } catch (error) {
        console.error('Error loading product:', error);
        if (loading) loading.style.display = 'none';
        productDetail.innerHTML = '<p>שגיאה בטעינת המוצר</p>';
    }
}

function displayProductDetail(product) {
    const productDetail = document.getElementById('productDetail');
    
    const imageUrl = product.image_url || 'https://via.placeholder.com/500x500?text=No+Image';
    const title = product.title || 'מוצר ללא שם';
    // השתמש במחיר המקורי של אמזון אם קיים, אחרת במחיר הנוכחי
    const price = product.amazon_original_price || product.price || '$0';
    const originalPrice = product.original_price || '';
    const discount = product.discount || '';
    const rating = product.rating || 0;
    const reviewsCount = product.reviews_count || 0;
    // Prefer Hebrew description if available
    const description = product.description_hebrew || product.custom_description_hebrew || product.description || 'אין תיאור זמין';
    const affiliateUrl = product.affiliate_url || '#';
    const videoUrl = product.video_url || '';
    
    productDetail.innerHTML = `
        <div class="detail-grid">
            <div>
                <img src="${imageUrl}" alt="${title}" class="detail-image" onerror="this.src='https://via.placeholder.com/500x500?text=No+Image'">
            </div>
            <div class="detail-info">
                <h1>${title}</h1>
                <div class="detail-price">
                    ${price}
                    ${originalPrice ? `<span style="font-size: 1rem; color: #999; text-decoration: line-through; margin-right: 1rem;">${originalPrice}</span>` : ''}
                    ${discount ? `<span class="discount-badge">${discount} הנחה</span>` : ''}
                </div>
                ${rating > 0 ? `
                    <div class="product-rating" style="margin: 1rem 0;">
                        <i class="fas fa-star"></i>
                        <span>${rating} (${reviewsCount.toLocaleString()} ביקורות)</span>
                    </div>
                ` : ''}
                <div class="detail-description">
                    ${description}
                </div>
                <div style="margin-top: 2rem;">
                    <a href="${affiliateUrl}" target="_blank" class="btn btn-success" style="text-decoration: none; display: inline-block; margin-left: 1rem;">
                        <i class="fas fa-shopping-cart"></i> קנה עכשיו ב-Amazon
                    </a>
                    <button onclick="generateVideo('${title}', ${JSON.stringify(product).replace(/'/g, "&#39;")})" class="btn btn-secondary" style="margin-right: 1rem;">
                        <i class="fas fa-video"></i> צור סרטון שיווק
                    </button>
                </div>
            </div>
        </div>
        ${videoUrl ? `
            <div class="video-section">
                <h2>סרטון מוצר</h2>
                <div class="video-container">
                    <video controls>
                        <source src="${videoUrl}" type="video/mp4">
                        הדפדפן שלך לא תומך בסרטונים.
                    </video>
                </div>
            </div>
        ` : ''}
    `;
}

// Load product when page loads
if (typeof asin !== 'undefined') {
    loadProductDetail();
}
