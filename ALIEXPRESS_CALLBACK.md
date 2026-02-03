# AliExpress Affiliate Callback Configuration

## 📌 Overview

Your application now supports AliExpress affiliate callbacks. Use these endpoints to receive notifications about orders, commissions, and other affiliate events.

## 🔗 Callback URLs

### Callback Endpoint
```
https://yourdomain.com/api/aliexpress/callback
```
This endpoint accepts both GET and POST requests and is used for general affiliate callbacks.

### Webhook Endpoint
```
https://yourdomain.com/api/aliexpress/webhook
```
This endpoint is specifically for order notifications and event webhooks (POST only).

## 🎯 How to Use

### 1. Access Configuration Page
Visit: `http://localhost:5000/callback-config` (or your deployed URL)

This page will show you:
- Your current callback URLs
- Step-by-step configuration instructions
- Copy buttons for easy URL copying

### 2. Configure AliExpress
1. Go to [AliExpress Affiliate Portal](https://portals.aliexpress.com/)
2. Navigate to your app settings
3. Find "Callback URL" or "Webhook Settings"
4. Paste your callback URL
5. Save and test

### 3. Environment Variables
Make sure these are set in your `.env` file:

```env
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here
ALIEXPRESS_AFFILIATE_TRACKING=your_tracking_id
```

## 🧪 Testing Locally

### Using ngrok (Recommended for local testing)

1. Install ngrok:
   ```bash
   # On macOS
   brew install ngrok
   
   # On Linux/Windows
   # Download from https://ngrok.com/download
   ```

2. Start your Flask app:
   ```bash
   python app.py
   ```

3. In another terminal, start ngrok:
   ```bash
   ngrok http 5000
   ```

4. Use the https URL from ngrok (e.g., `https://abc123.ngrok.io`) as your base URL
   - Callback: `https://abc123.ngrok.io/api/aliexpress/callback`
   - Webhook: `https://abc123.ngrok.io/api/aliexpress/webhook`

## 📊 Monitoring Callbacks

Check your server logs for callback data:

```bash
[ALIEXPRESS CALLBACK] Received callback from AliExpress
[CALLBACK DATA] {'order_id': '12345', 'commission': '5.50', 'status': 'paid'}
```

## 🚀 Production Deployment

When deploying to production (Render, Railway, Heroku, etc.):

1. Your callback URLs will automatically use your production domain
2. Visit `/callback-config` on your production site to get the correct URLs
3. Update AliExpress portal with your production callback URLs

## 📝 Callback Data Structure

AliExpress typically sends:

```json
{
  "order_id": "12345678",
  "commission": "5.50",
  "status": "paid",
  "product_id": "4000123456789",
  "timestamp": "2026-01-29T10:00:00Z"
}
```

The callback endpoint logs all received data for debugging.

## 🔒 Security Considerations

1. **Verify Signatures**: Add signature verification for production
2. **Rate Limiting**: Consider adding rate limiting to prevent abuse
3. **HTTPS Only**: Always use HTTPS in production
4. **Log Monitoring**: Monitor logs for suspicious activity

## 💡 Tips

- Keep your app keys secure
- Test callbacks thoroughly before going live
- Monitor callback logs regularly
- Update callback URLs if you change domains

## 🆘 Troubleshooting

**Callback not received?**
- Check if your URL is publicly accessible
- Verify the URL is correct in AliExpress portal
- Check server logs for errors
- Test with ngrok if running locally

**Getting errors?**
- Verify environment variables are set
- Check network connectivity
- Review AliExpress API documentation
- Check firewall settings

## 📚 Additional Resources

- [AliExpress Affiliate API Docs](https://portals.aliexpress.com/help.htm)
- [Ngrok Documentation](https://ngrok.com/docs)
- Your callback config page: `/callback-config`
