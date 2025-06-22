from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import uuid
from functools import wraps

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
    }
})

# API Key configuration
API_KEY = os.environ.get('API_KEY', 'your-secret-api-key-here')  # Set this in environment variables

def require_api_key(f):
    """Decorator to require API key for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
        
        if not api_key:
            return jsonify({
                "responseType": "error",
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "API key is required",
                    "details": "Please provide API key in 'X-API-Key' or 'Authorization' header"
                }
            }), 401
        
        # Remove 'Bearer ' prefix if present
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        if api_key != API_KEY:
            return jsonify({
                "responseType": "error",
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key",
                    "details": "The provided API key is not valid"
                }
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Mock data for the restaurant
STORE_DATA = {
    "name": "Tasty Bites Bangalore",
    "description": "Authentic South Indian & North Indian Cuisine",
    "address": "123 MG Road, Bangalore, Karnataka 560001",
    "phone": "+91-80-12345678",
    "email": "tastybites@email.com",
    "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&h=300&fit=crop",
    "rating": 4.2,
    "delivery_time": "30-45 mins",
    "cuisine": ["South Indian", "North Indian", "Biryani"],
    "status": "open"
}

# Mock menu items with real food images
MENU_ITEMS = {
    "item_001": {
        "id": "item_001",
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice with tender chicken pieces",
        "category": "Biryani",
        "image": "https://images.unsplash.com/photo-1563379091339-03246963d51a?w=300&h=200&fit=crop",
        "available": True,
        "prices": {
            "zomato": 299,
            "swiggy": 315
        },
        "original_price": 320
    },
    "item_002": {
        "id": "item_002",
        "name": "Masala Dosa",
        "description": "Crispy dosa with spiced potato filling",
        "category": "South Indian",
        "image": "https://images.unsplash.com/photo-1630383249896-424e482df921?w=300&h=200&fit=crop",
        "available": True,
        "prices": {
            "zomato": 120,
            "swiggy": 125
        },
        "original_price": 130
    },
    "item_003": {
        "id": "item_003",
        "name": "Paneer Butter Masala",
        "description": "Rich and creamy paneer curry",
        "category": "North Indian",
        "image": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=300&h=200&fit=crop",
        "available": True,
        "prices": {
            "zomato": 250,
            "swiggy": 260
        },
        "original_price": 270
    },
    "item_004": {
        "id": "item_004",
        "name": "Mutton Biryani",
        "description": "Flavorful mutton biryani with aromatic spices",
        "category": "Biryani",
        "image": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=300&h=200&fit=crop",
        "available": True,
        "prices": {
            "zomato": 399,
            "swiggy": 420
        },
        "original_price": 450
    },
    "item_005": {
        "id": "item_005",
        "name": "Samosa",
        "description": "Crispy pastry filled with spiced vegetables",
        "category": "Snacks",
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300&h=200&fit=crop",
        "available": False,
        "prices": {
            "zomato": 40,
            "swiggy": 45
        },
        "original_price": 50
    }
}

# Mock offers data
OFFERS = {
    "zomato": [
        {
            "id": "ZOMATO20",
            "title": "ZOMATO20",
            "description": "Get 20% off on orders above ₹299",
            "discount_type": "percentage",
            "discount_value": 20,
            "max_discount": 100,
            "min_order": 299,
            "valid_until": "2025-12-31",
            "active": True
        },
        {
            "id": "FIRSTORDER",
            "title": "FIRSTORDER",
            "description": "₹150 off on your first order",
            "discount_type": "fixed",
            "discount_value": 150,
            "max_discount": 150,
            "min_order": 300,
            "valid_until": "2025-12-31",
            "active": True
        }
    ],
    "swiggy": [
        {
            "id": "SWIGGY25",
            "title": "SWIGGY25",
            "description": "25% off up to ₹125 on orders above ₹399",
            "discount_type": "percentage",
            "discount_value": 25,
            "max_discount": 125,
            "min_order": 399,
            "valid_until": "2025-12-31",
            "active": True
        },
        {
            "id": "WELCOME100",
            "title": "WELCOME100",
            "description": "₹100 off on orders above ₹249",
            "discount_type": "fixed",
            "discount_value": 100,
            "max_discount": 100,
            "min_order": 249,
            "valid_until": "2025-12-31",
            "active": True
        }
    ]
}

# Routes for Zomato UI
@app.route('/')
def index():
    return '''
    <h1>Food Delivery Platform Mock</h1>
    <div style="margin: 20px; font-family: Arial;">
        <h2>Available Platforms:</h2>
        <div style="display: flex; gap: 20px;">
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                <h3 style="color: #cb202d;">Zomato Merchant Dashboard</h3>
                <p>Access the Zomato-style merchant interface</p>
                <a href="/zomato" style="background: #cb202d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Open Zomato UI</a>
            </div>
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                <h3 style="color: #fc8019;">Swiggy Merchant Dashboard</h3>
                <p>Access the Swiggy-style merchant interface</p>
                <a href="/swiggy" style="background: #fc8019; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Open Swiggy UI</a>
            </div>
        </div>
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <h3>API Endpoints for Agent Integration:</h3>
            <ul>
                <li><strong>GET /tools</strong> - Get available tools</li>
                <li><strong>POST /tools/updateMenuPrice</strong> - Update item price</li>
                <li><strong>POST /tools/createOffer</strong> - Create new offer</li>
                <li><strong>POST /tools/toggleItemAvailability</strong> - Toggle item availability</li>
                <li><strong>POST /tools/getStoreInfo</strong> - Get store information</li>
                <li><strong>POST /tools/getMenuItems</strong> - Get menu items</li>
                <li><strong>POST /tools/getActiveOffers</strong> - Get active offers</li>
            </ul>
        </div>
    </div>
    '''

@app.route('/zomato')
def zomato_dashboard():
    return render_template('zomato.html', 
                         store=STORE_DATA, 
                         menu_items=MENU_ITEMS, 
                         offers=OFFERS['zomato'],
                         platform='zomato')

@app.route('/swiggy')
def swiggy_dashboard():
    return render_template('swiggy.html', 
                         store=STORE_DATA, 
                         menu_items=MENU_ITEMS, 
                         offers=OFFERS['swiggy'],
                         platform='swiggy')

# API Routes following the original agent specification
@app.route('/tools', methods=['GET'])
@require_api_key
def get_tools():
    """Get available tools - following original agent spec"""
    with open('tools.json', 'r') as f:
        tools = json.load(f)
    
    return tools

@app.route('/tools/<tool_name>', methods=['POST'])
@require_api_key
def execute_tool(tool_name):
    """Execute a specific tool - following original agent spec"""
    try:
        data = request.get_json() or {}
        
        if tool_name == 'updateMenuPrice':
            return update_menu_price(data)
        elif tool_name == 'createOffer':
            return create_offer(data)
        elif tool_name == 'toggleItemAvailability':
            return toggle_item_availability(data)
        elif tool_name == 'getStoreInfo':
            return get_store_info(data)
        elif tool_name == 'getMenuItems':
            return get_menu_items(data)
        elif tool_name == 'getActiveOffers':
            return get_active_offers(data)
        elif tool_name == 'updateStoreInfo':
            return update_store_info(data)
        else:
            return jsonify({
                "responseType": "error",
                "error": {
                    "code": "TOOL_NOT_FOUND",
                    "message": f"Tool '{tool_name}' not found",
                    "details": f"Available tools: updateMenuPrice, createOffer, toggleItemAvailability, getStoreInfo, getMenuItems, getActiveOffers, updateStoreInfo"
                }
            }), 404
            
    except Exception as e:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "details": str(e)
            }
        }), 500

# Tool implementation functions
def update_menu_price(data):
    """Update menu item price on specified platform"""
    required_fields = ['item_id', 'platform', 'new_price']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "MISSING_PARAMETERS",
                "message": f"Missing required parameters: {', '.join(missing_fields)}",
                "details": "Required: item_id, platform, new_price"
            }
        }), 400
    
    item_id = data['item_id']
    platform = data['platform']
    new_price = data['new_price']
    
    if item_id not in MENU_ITEMS:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "ITEM_NOT_FOUND",
                "message": f"Menu item '{item_id}' not found",
                "details": f"Available items: {', '.join(MENU_ITEMS.keys())}"
            }
        }), 404
    
    if platform not in ['zomato', 'swiggy']:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "INVALID_PLATFORM",
                "message": "Platform must be 'zomato' or 'swiggy'",
                "details": "Supported platforms: zomato, swiggy"
            }
        }), 400
    
    old_price = MENU_ITEMS[item_id]['prices'][platform]
    MENU_ITEMS[item_id]['prices'][platform] = new_price
    
    return jsonify({
        "responseType": "success",
        "data": {
            "item_id": item_id,
            "item_name": MENU_ITEMS[item_id]['name'],
            "platform": platform,
            "old_price": old_price,
            "new_price": new_price,
            "message": f"Price updated for {MENU_ITEMS[item_id]['name']} on {platform.title()}: ₹{old_price} → ₹{new_price}"
        }
    })

def create_offer(data):
    """Create a new discount offer"""
    required_fields = ['platform', 'title', 'description', 'discount_type', 'discount_value', 'min_order']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "MISSING_PARAMETERS",
                "message": f"Missing required parameters: {', '.join(missing_fields)}",
                "details": "Required: platform, title, description, discount_type, discount_value, min_order"
            }
        }), 400
    
    platform = data['platform']
    if platform not in ['zomato', 'swiggy']:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "INVALID_PLATFORM",
                "message": "Platform must be 'zomato' or 'swiggy'",
                "details": "Supported platforms: zomato, swiggy"
            }
        }), 400
    
    new_offer = {
        "id": data['title'],
        "title": data['title'],
        "description": data['description'],
        "discount_type": data['discount_type'],
        "discount_value": data['discount_value'],
        "max_discount": data.get('max_discount', data['discount_value'] if data['discount_type'] == 'fixed' else 200),
        "min_order": data['min_order'],
        "valid_until": data.get('valid_until', '2025-12-31'),
        "active": data.get('active', True)
    }
    
    OFFERS[platform].append(new_offer)
    
    return jsonify({
        "responseType": "success",
        "data": {
            "offer": new_offer,
            "platform": platform,
            "message": f"Offer '{data['title']}' created successfully on {platform.title()}"
        }
    })

def toggle_item_availability(data):
    """Toggle menu item availability"""
    if 'item_id' not in data:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "MISSING_PARAMETERS",
                "message": "Missing required parameter: item_id",
                "details": "Required: item_id"
            }
        }), 400
    
    item_id = data['item_id']
    if item_id not in MENU_ITEMS:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "ITEM_NOT_FOUND",
                "message": f"Menu item '{item_id}' not found",
                "details": f"Available items: {', '.join(MENU_ITEMS.keys())}"
            }
        }), 404
    
    MENU_ITEMS[item_id]['available'] = not MENU_ITEMS[item_id]['available']
    status = "available" if MENU_ITEMS[item_id]['available'] else "unavailable"
    
    return jsonify({
        "responseType": "success",
        "data": {
            "item_id": item_id,
            "item_name": MENU_ITEMS[item_id]['name'],
            "available": MENU_ITEMS[item_id]['available'],
            "message": f"{MENU_ITEMS[item_id]['name']} is now {status}"
        }
    })

def get_store_info(data):
    """Get restaurant store information"""
    platform = data.get('platform', 'all')
    
    if platform == 'all':
        return jsonify({
            "responseType": "success",
            "data": {
                "store": STORE_DATA,
                "platforms": {
                    "zomato": {"active": True, "commission": "20%"},
                    "swiggy": {"active": True, "commission": "22%"}
                }
            }
        })
    elif platform in ['zomato', 'swiggy']:
        return jsonify({
            "responseType": "success",
            "data": {
                "store": STORE_DATA,
                "platform": platform,
                "platform_info": {
                    "active": True,
                    "commission": "20%" if platform == 'zomato' else "22%"
                }
            }
        })
    else:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "INVALID_PLATFORM",
                "message": "Platform must be 'zomato', 'swiggy', or 'all'",
                "details": "Supported platforms: zomato, swiggy, all"
            }
        }), 400

def get_menu_items(data):
    """Get menu items with platform-specific pricing"""
    platform = data.get('platform', 'all')
    category = data.get('category')
    available_only = data.get('available_only', False)
    
    filtered_items = {}
    for item_id, item in MENU_ITEMS.items():
        # Filter by availability
        if available_only and not item['available']:
            continue
        
        # Filter by category
        if category and item['category'].lower() != category.lower():
            continue
        
        # Prepare item data
        item_data = item.copy()
        if platform != 'all' and platform in ['zomato', 'swiggy']:
            item_data['price'] = item['prices'][platform]
            item_data['platform'] = platform
        
        filtered_items[item_id] = item_data
    
    return jsonify({
        "responseType": "success",
        "data": {
            "items": filtered_items,
            "total_count": len(filtered_items),
            "filters": {
                "platform": platform,
                "category": category,
                "available_only": available_only
            }
        }
    })

def get_active_offers(data):
    """Get active offers for platforms"""
    platform = data.get('platform', 'all')
    
    if platform == 'all':
        return jsonify({
            "responseType": "success",
            "data": {
                "offers": OFFERS,
                "total_count": sum(len(offers) for offers in OFFERS.values())
            }
        })
    elif platform in ['zomato', 'swiggy']:
        active_offers = [offer for offer in OFFERS[platform] if offer['active']]
        return jsonify({
            "responseType": "success",
            "data": {
                "offers": {platform: active_offers},
                "total_count": len(active_offers),
                "platform": platform
            }
        })
    else:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "INVALID_PLATFORM",
                "message": "Platform must be 'zomato', 'swiggy', or 'all'",
                "details": "Supported platforms: zomato, swiggy, all"
            }
        }), 400

def update_store_info(data):
    """Update restaurant store information"""
    updatable_fields = ['name', 'description', 'phone', 'email']
    updated_fields = []
    
    for field in updatable_fields:
        if field in data:
            STORE_DATA[field] = data[field]
            updated_fields.append(field)
    
    if not updated_fields:
        return jsonify({
            "responseType": "error",
            "error": {
                "code": "NO_UPDATES",
                "message": "No valid fields provided for update",
                "details": f"Updatable fields: {', '.join(updatable_fields)}"
            }
        }), 400
    
    return jsonify({
        "responseType": "success",
        "data": {
            "store": STORE_DATA,
            "updated_fields": updated_fields,
            "message": f"Store information updated: {', '.join(updated_fields)}"
        }
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=3000)