// Product Management JavaScript

// Load saved products on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSavedProducts();
    updateStats();
});

// Load saved products
async function loadSavedProducts() {
    const loading = document.getElementById('loadingSaved');
    const grid = document.getElementById('savedProductsGrid');
    
    if (loading) loading.style.display = 'block';
    if (grid) grid.innerHTML = '';
    
    try {
        const response = await fetch('/api/products/saved');
        const data = await response.json();
        
        if (loading) loading.style.display = 'none';
        
        if (data.success && data.products) {
            displaySavedProducts(data.products);
            updateStats();
        } else {
            if (grid) grid.innerHTML = '<p>אין מוצרים שמורים</p>';
        }
    } catch (error) {
        console.error('Error loading saved products:', error);
        if (loading) loading.style.display = 'none';
        if (grid) grid.innerHTML = '<p>שגיאה בטעינת המוצרים</p>';
    }
}

// Display saved products
function displaySavedProducts(products) {
    const grid = document.getElementById('savedProductsGrid');
    if (!grid) return;
    
    if (products.length === 0) {
        grid.innerHTML = '<p>אין מוצרים שמורים</p>';
        return;
    }
    
    grid.innerHTML = '';
    
    products.forEach(product => {
        const card = createProductCard(product, true); // true = show remove button
        grid.appendChild(card);
    });
}

// Create product card with remove option
function createProductCard(product, showRemove = false) {
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
    const asin = extractASIN(product);
    
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
                <a href="${affiliateUrl}" target="_blank" class="btn btn-success" style="flex: 1; text-align: center; text-decoration: none;">
                    <i class="fas fa-shopping-cart"></i> קנה עכשיו
                </a>
                <button onclick="generateVideo('${title.replace(/'/g, "\\'")}', ${JSON.stringify(product).replace(/'/g, "&#39;")})" class="btn btn-secondary">
                    <i class="fas fa-video"></i> צור סרטון
                </button>
                ${showRemove ? `
                    <button onclick="editProduct('${asin}')" class="btn" style="background: #667eea; color: white; padding: 0.5rem;">
                        <i class="fas fa-edit"></i> ערוך
                    </button>
                    <button onclick="removeProduct('${asin}')" class="btn" style="background: #dc3545; color: white; padding: 0.5rem;">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        </div>
    `;
    
    return card;
}

// Extract ASIN from product
function extractASIN(product) {
    // Try multiple sources for ASIN
    if (product.asin) {
        return product.asin;
    }
    
    const url = product.affiliate_url || product.url || '';
    if (url) {
        // Try /dp/ pattern
        let match = url.match(/\/dp\/([A-Z0-9]{10})/);
        if (match) return match[1];
        
        // Try /gp/product/ pattern
        match = url.match(/\/gp\/product\/([A-Z0-9]{10})/);
        if (match) return match[1];
        
        // Try ?product= pattern (VDP links)
        match = url.match(/[?&]product=([A-Z0-9]{10})/);
        if (match) return match[1];
    }
    
    return '';
}

// Make functions globally accessible
window.updatePlaceholder = function() {
    const urlInput = document.getElementById('productUrlInput');
    if (!urlInput) return;
    
    const linkType = document.querySelector('input[name="linkType"]:checked')?.value || 'regular';
    const store = document.querySelector('input[name="store"]:checked')?.value || 'amazon';
    
    let placeholder = '';
    if (store === 'aliexpress') {
        if (linkType === 'affiliate') {
            placeholder = 'הדבק קישור שותפים מ-AliExpress (לדוגמה: https://aliexpress.com/item/1234567890.html?aff_platform=...)';
        } else {
            placeholder = 'הדבק קישור מוצר מ-AliExpress (לדוגמה: https://aliexpress.com/item/1234567890.html)';
        }
    } else {
        if (linkType === 'affiliate') {
            placeholder = 'הדבק קישור שותפים מ-Amazon (לדוגמה: https://amazon.com/dp/B08N5WRWNW?tag=your-tag-20)';
        } else {
            placeholder = 'הדבק קישור מוצר מ-Amazon (לדוגמה: https://amazon.com/dp/B08N5WRWNW)';
        }
    }
    
    urlInput.placeholder = placeholder;
};

// Add product from URL (supports both regular and affiliate links)
window.addProductFromUrl = async function() {
    const urlInput = document.getElementById('productUrlInput');
    const statusDiv = document.getElementById('addProductStatus');
    
    if (!urlInput) {
        alert('שדה הקישור לא נמצא');
        return;
    }
    
    const url = urlInput.value.trim();
    const linkType = document.querySelector('input[name="linkType"]:checked')?.value || 'regular';
    const store = document.querySelector('input[name="store"]:checked')?.value || 'amazon';
    
    if (!url) {
        alert('אנא הזן קישור מוצר');
        return;
    }
    
    // Validate URL format based on selected store
    if (store === 'aliexpress') {
        if (!url.includes('aliexpress.com')) {
            alert('אנא הזן קישור תקני מ-AliExpress');
            return;
        }
    } else {
        // Allow Amazon URLs including short links
        if (!url.includes('amazon.com') && !url.includes('amzn.to') && !url.includes('amazon.')) {
            alert('אנא הזן קישור תקני מ-Amazon (כולל קישורים קצרים amzn.to)');
            return;
        }
    }
    
    if (statusDiv) {
        statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> מוסיף מוצר...';
        statusDiv.style.color = '#667eea';
    }
    
    try {
        // Prepare request body
        const requestBody = { url: url, store: store };
        if (linkType === 'affiliate') {
            requestBody.affiliate_link = url;
        }
        
        const response = await fetch('/api/products/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.success) {
            let message = '<i class="fas fa-check-circle"></i> המוצר נוסף בהצלחה!';
            if (data.is_affiliate) {
                message += '<br><small>קישור שותפים זוהה ועובד בהצלחה</small>';
            }
            
            if (statusDiv) {
                statusDiv.innerHTML = message;
                statusDiv.style.color = '#28a745';
            }
            urlInput.value = '';
            loadSavedProducts();
            updateStats();
        } else {
            if (statusDiv) {
                statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> שגיאה: ' + (data.error || 'Unknown error');
                statusDiv.style.color = '#dc3545';
            }
        }
    } catch (error) {
        console.error('Error adding product:', error);
        if (statusDiv) {
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> שגיאה בהוספת המוצר: ' + error.message;
            statusDiv.style.color = '#dc3545';
        }
    }
};


// Remove product
window.removeProduct = async function(asin) {
    if (!confirm('האם אתה בטוח שברצונך להסיר את המוצר?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/products/remove/${asin}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('המוצר הוסר בהצלחה');
            loadSavedProducts();
            updateStats();
        } else {
            alert('שגיאה בהסרת המוצר: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error removing product:', error);
        alert('שגיאה בהסרת המוצר');
    }
}

// Search saved products
async function searchSavedProducts() {
    const query = document.getElementById('searchSavedInput').value.trim();
    const grid = document.getElementById('savedProductsGrid');
    
    try {
        const response = await fetch('/api/products/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (data.success && data.products) {
            displaySavedProducts(data.products);
        }
    } catch (error) {
        console.error('Error searching products:', error);
    }
}

// Import products from file
async function importProducts() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/products/import', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`יובאו ${data.count} מוצרים בהצלחה!`);
            loadSavedProducts();
            updateStats();
        } else {
            alert('שגיאה בייבוא: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error importing products:', error);
        alert('שגיאה בייבוא המוצרים');
    }
    
    // Reset file input
    fileInput.value = '';
}

// Export products to file
async function exportProducts() {
    try {
        const response = await fetch('/api/products/export');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'products_export.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            alert('המוצרים יוצאו בהצלחה!');
        } else {
            alert('שגיאה בייצוא המוצרים');
        }
    } catch (error) {
        console.error('Error exporting products:', error);
        alert('שגיאה בייצוא המוצרים');
    }
}

// Update statistics
async function updateStats() {
    try {
        const productsResponse = await fetch('/api/products/saved');
        const productsData = await productsResponse.json();
        
        const videosResponse = await fetch('/api/videos');
        const videosData = await videosResponse.json();
        
        const totalProducts = productsData.success ? productsData.count : 0;
        const totalVideos = videosData.videos ? videosData.videos.length : 0;
        
        const totalProductsEl = document.getElementById('totalProducts');
        const totalVideosEl = document.getElementById('totalVideos');
        
        if (totalProductsEl) totalProductsEl.textContent = totalProducts;
        if (totalVideosEl) totalVideosEl.textContent = totalVideos;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Edit product
window.editProduct = async function(asin) {
    try {
        // Get product from saved products
        const savedResponse = await fetch('/api/products/saved');
        const savedData = await savedResponse.json();
        
        if (!savedData.success || !savedData.products) {
            alert('שגיאה בטעינת המוצרים');
            return;
        }
        
        const product = savedData.products.find(p => extractASIN(p) === asin);
        
        if (!product) {
            alert('מוצר לא נמצא במוצרים השמורים');
            return;
        }
        
        openEditModal(product);
    } catch (error) {
        console.error('Error loading product for edit:', error);
        alert('שגיאה בטעינת המוצר לעריכה: ' + error.message);
    }
}

// Open edit modal
function openEditModal(product) {
    console.log('Opening edit modal for product:', product);
    
    const modal = document.getElementById('editProductModal');
    if (!modal) {
        console.error('Edit modal not found!');
        alert('שגיאה: חלון העריכה לא נמצא');
        return;
    }
    
    // Try to extract ASIN from multiple sources
    let asin = product.asin || extractASIN(product);
    
    if (!asin) {
        console.error('No ASIN found for product:', product);
        alert('לא ניתן לערוך מוצר ללא ASIN. אנא הוסף קישור Amazon למוצר.');
        return;
    }
    
    console.log('Product ASIN:', asin);
    
    // Fill form with product data
    const asinInput = document.getElementById('editProductASIN');
    const titleInput = document.getElementById('editProductTitle');
    const descInput = document.getElementById('editProductDescription');
    const imageInput = document.getElementById('editProductImage');
    const videoInput = document.getElementById('editProductVideo');
    const priceInput = document.getElementById('editProductPrice');
    const originalPriceInput = document.getElementById('editProductOriginalPrice');
    
    if (!asinInput || !titleInput || !descInput || !imageInput || !videoInput || !priceInput || !originalPriceInput) {
        console.error('Form inputs not found!');
        alert('שגיאה: שדות הטופס לא נמצאו');
        return;
    }
    
    asinInput.value = asin;
    titleInput.value = product.title || '';
    descInput.value = product.description || product.custom_description || '';
    
    // Hebrew description field
    const descHebrewInput = document.getElementById('editProductDescriptionHebrew');
    if (descHebrewInput) {
        descHebrewInput.value = product.description_hebrew || product.custom_description_hebrew || '';
    }
    
    imageInput.value = product.image_url || '';
    videoInput.value = product.video_url || product.custom_video || '';
    // הצג את המחיר המקורי של אמזון אם קיים, אחרת את המחיר הנוכחי
    priceInput.value = product.amazon_original_price || product.price || '';
    originalPriceInput.value = product.original_price || '';
    
    // Show modal
    modal.style.display = 'block';
    console.log('Modal displayed');
}

// Close edit modal
window.closeEditModal = function() {
    const modal = document.getElementById('editProductModal');
    if (modal) modal.style.display = 'none';
}

// Save product edit
window.saveProductEdit = async function(event) {
    event.preventDefault();
    
    const asin = document.getElementById('editProductASIN').value;
    const updates = {
        title: document.getElementById('editProductTitle').value,
        description: document.getElementById('editProductDescription').value,
        description_hebrew: document.getElementById('editProductDescriptionHebrew').value,
        image_url: document.getElementById('editProductImage').value,
        video_url: document.getElementById('editProductVideo').value,
        // לא מעדכנים את המחיר - נשאיר את המחיר המקורי של אמזון
        original_price: document.getElementById('editProductOriginalPrice').value
    };
    
    try {
        const response = await fetch(`/api/products/update/${asin}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('המוצר עודכן בהצלחה!');
            closeEditModal();
            loadSavedProducts();
        } else {
            alert('שגיאה בעדכון המוצר: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error updating product:', error);
        alert('שגיאה בעדכון המוצר');
    }
}

// Upload image
window.uploadImage = async function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/products/upload-image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update image URL in form
            const fullUrl = window.location.origin + data.url;
            document.getElementById('editProductImage').value = fullUrl;
            alert('תמונה הועלתה בהצלחה!');
        } else {
            alert('שגיאה בהעלאת תמונה: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('שגיאה בהעלאת תמונה');
    }
}

// Upload video
window.uploadVideo = async function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/products/upload-video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update video URL in form
            const fullUrl = window.location.origin + data.url;
            document.getElementById('editProductVideo').value = fullUrl;
            alert('סרטון הועלה בהצלחה!');
        } else {
            alert('שגיאה בהעלאת סרטון: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error uploading video:', error);
        alert('שגיאה בהעלאת סרטון');
    }
}

// Translate description to Hebrew
window.translateDescription = async function() {
    const englishDesc = document.getElementById('editProductDescription').value;
    const hebrewDescInput = document.getElementById('editProductDescriptionHebrew');
    
    if (!englishDesc || englishDesc.trim() === '') {
        alert('אנא הזן תיאור באנגלית תחילה');
        return;
    }
    
    // Show loading
    const originalValue = hebrewDescInput.value;
    hebrewDescInput.value = 'ממתין לתרגום...';
    hebrewDescInput.disabled = true;
    
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: englishDesc,
                target: 'he'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.translated) {
            hebrewDescInput.value = data.translated;
            alert('התיאור תורגם בהצלחה!');
        } else {
            hebrewDescInput.value = originalValue;
            alert('לא ניתן לתרגם כרגע. אנא הזן תיאור בעברית ידנית.\n' + (data.message || data.error || ''));
        }
    } catch (error) {
        console.error('Translation error:', error);
        hebrewDescInput.value = originalValue;
        alert('שגיאה בתרגום. אנא הזן תיאור בעברית ידנית.');
    } finally {
        hebrewDescInput.disabled = false;
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('editProductModal');
    if (event.target === modal) {
        closeEditModal();
    }
}

// Allow Enter key to add product
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('productUrlInput');
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addProductFromUrl();
            }
        });
    }
});
