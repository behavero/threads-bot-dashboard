# Image Usage Tracking Implementation 🖼️

## 🎯 Overview

Implemented comprehensive image usage tracking to prevent posting the same image twice in a row across accounts. This enhances anti-detection by ensuring image variety and preventing repetitive posting patterns.

## 🏗️ Architecture

### **ImageUsageTracker Class**
- **Location**: `enhanced_bot.py` (lines 269-383)
- **Purpose**: Tracks image usage across all accounts with cooldown periods
- **Features**: Global and account-specific cooldowns, usage statistics, cleanup

### **Enhanced MediaVariationManager**
- **Location**: `enhanced_bot.py` (lines 384-481)
- **Integration**: Uses ImageUsageTracker for intelligent image selection
- **Features**: Cross-account tracking, fallback mechanisms, periodic cleanup

## 🔧 Key Features

### **1. Cross-Account Image Tracking** 📊
```python
class ImageUsageTracker:
    def __init__(self):
        self.image_usage_history = {}  # image_path -> usage_data
        self.account_image_history = {}  # username -> recent_images
        self.max_account_history = 5  # Keep last 5 images per account
        self.global_cooldown = 1800  # 30 minutes global cooldown
        self.account_cooldown = 3600  # 1 hour per account cooldown
```

### **2. Dual Cooldown System** ⏰
- **Global Cooldown**: 30 minutes - prevents same image across all accounts
- **Account Cooldown**: 1 hour - prevents same image for specific account
- **Configurable**: Both cooldowns can be adjusted via environment variables

### **3. Usage Statistics** 📈
```python
def get_image_stats(self, image_path: str) -> Dict:
    return {
        'total_uses': stats['total_uses'],
        'last_used': stats['last_global_use'],
        'account_count': len(stats['account_usage']),
        'available': current_time - stats['last_global_use'] >= self.global_cooldown
    }
```

### **4. Intelligent Image Selection** 🎯
```python
def get_available_images(self, images: List[Path], username: str) -> List[Path]:
    """Get list of images available for use by this account"""
    available_images = []
    
    for img in images:
        if self.can_use_image(str(img), username):
            available_images.append(img)
    
    return available_images
```

## 🔄 Integration Points

### **Enhanced Bot Integration**
```python
# In process_account method
image = self.media_variation_manager.get_varied_image(self.images, account.username)
```

### **Dashboard Integration**
```python
# Flask API endpoint
@app.route('/api/images/usage', methods=['GET'])
def get_image_usage():
    """Get image usage statistics for dashboard"""
```

### **React Frontend**
```javascript
// Images component shows usage statistics
const stats = usageStats[image.name] || {};
<Typography variant="caption" display="block" color="text.secondary">
  Uses: {stats.total_uses || 0}
</Typography>
```

## 📊 Usage Tracking Details

### **Global Tracking**
- **Tracks**: All image usage across all accounts
- **Stores**: Last global use time, total uses, account usage map
- **Cooldown**: 30 minutes minimum between global uses

### **Account-Specific Tracking**
- **Tracks**: Per-account image usage history
- **Stores**: Last 5 images used per account
- **Cooldown**: 1 hour minimum between uses for same account

### **Statistics Available**
- **Total Uses**: How many times image has been posted
- **Account Count**: How many different accounts used the image
- **Last Used**: Timestamp of last usage
- **Availability**: Whether image is currently available for use

## 🛡️ Anti-Detection Benefits

### **1. Prevents Repetitive Patterns**
- ✅ **No same image twice in a row** across accounts
- ✅ **Account-specific cooldowns** prevent individual account repetition
- ✅ **Global cooldowns** prevent cross-account repetition

### **2. Human-like Behavior**
- ✅ **Varied image selection** based on usage history
- ✅ **Natural cooldown periods** simulate human posting patterns
- ✅ **Fallback mechanisms** when no images are available

### **3. Intelligent Fallbacks**
```python
# If no images available due to usage restrictions
if not available_images:
    logger.warning(f"⚠️  No images available for {username} due to usage restrictions")
    # Fall back to basic reuse delay check
    available_images = []
    for img in images:
        last_used = self.image_reuse_delays.get(str(img), 0)
        if current_time - last_used >= self.min_reuse_delay:
            available_images.append(img)
```

## 🧹 Memory Management

### **Automatic Cleanup**
```python
def cleanup_old_records(self, max_age_hours: int = 24):
    """Clean up old usage records to prevent memory bloat"""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # Clean up image usage history
    images_to_remove = []
    for image_path, usage_data in self.image_usage_history.items():
        if current_time - usage_data['last_global_use'] > max_age_seconds:
            images_to_remove.append(image_path)
```

### **Periodic Cleanup**
- **Trigger**: 10% chance on each image selection
- **Age**: 24 hours default (configurable)
- **Purpose**: Prevents memory bloat from old records

## 📈 Dashboard Integration

### **API Endpoint**
```python
GET /api/images/usage
{
  "success": true,
  "usage_stats": {
    "image1.jpg": {
      "total_uses": 5,
      "last_used": 1640995200,
      "account_count": 3,
      "available": true,
      "file_size": 1024000,
      "modified": "2024-01-01T12:00:00"
    }
  },
  "total_images": 10
}
```

### **Frontend Display**
- **Usage Count**: Shows total times image has been used
- **Account Count**: Shows how many accounts used the image
- **Availability Status**: Shows if image is in cooldown or available
- **Color Coding**: Green for available, yellow for in cooldown

## 🔧 Configuration Options

### **Environment Variables**
```bash
# Image usage tracking cooldowns (in seconds)
GLOBAL_IMAGE_COOLDOWN=1800    # 30 minutes
ACCOUNT_IMAGE_COOLDOWN=3600    # 1 hour
MAX_ACCOUNT_HISTORY=5          # Keep last 5 images per account
CLEANUP_MAX_AGE_HOURS=24       # Cleanup records older than 24 hours
```

### **Runtime Configuration**
```python
# In ImageUsageTracker
self.global_cooldown = 1800  # 30 minutes
self.account_cooldown = 3600  # 1 hour
self.max_account_history = 5  # Keep last 5 images per account
```

## 🎯 Success Indicators

### **Bot Behavior**
- ✅ **No duplicate images** posted in sequence across accounts
- ✅ **Account-specific cooldowns** respected
- ✅ **Global cooldowns** prevent cross-account repetition
- ✅ **Fallback mechanisms** work when no images available
- ✅ **Memory cleanup** prevents bloat

### **Dashboard Features**
- ✅ **Usage statistics** displayed for each image
- ✅ **Real-time availability** status shown
- ✅ **Account usage tracking** visible
- ✅ **File information** with usage data

### **Anti-Detection Benefits**
- ✅ **Human-like posting patterns** with varied image selection
- ✅ **No repetitive image sequences** across accounts
- ✅ **Intelligent cooldown periods** simulate natural behavior
- ✅ **Graceful fallbacks** when restrictions apply

## 🔄 Future Enhancements

### **Planned Features**
- **Image Similarity Detection**: Prevent posting visually similar images
- **Content Analysis**: Analyze image content for better variation
- **Usage Analytics**: Advanced reporting on image performance
- **Dynamic Cooldowns**: Adjust cooldowns based on account activity

### **Technical Improvements**
- **Database Storage**: Move tracking to database for persistence
- **Redis Caching**: Use Redis for faster lookups
- **Machine Learning**: ML-based image selection
- **Advanced Analytics**: Detailed usage patterns and insights

## 🎉 Summary

The image usage tracking implementation provides:

- ✅ **Cross-account image tracking** with dual cooldown system
- ✅ **Intelligent image selection** based on usage history
- ✅ **Comprehensive statistics** for monitoring and analysis
- ✅ **Dashboard integration** with real-time usage display
- ✅ **Memory management** with automatic cleanup
- ✅ **Anti-detection features** preventing repetitive patterns
- ✅ **Graceful fallbacks** when restrictions apply

**The image usage tracking is now fully implemented and prevents posting the same image twice in a row across accounts!** 🖼️ 