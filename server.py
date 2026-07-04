from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    description: str
    price: float
    image: str
    stock: int = 100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    category: str
    description: str
    price: float
    image: str
    stock: int = 100

class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    product_price: float
    product_image: str
    quantity: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1

class SearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None

# Import recommendation engine
from recommendation import RecommendationEngine

# Initialize recommendation engine (will be loaded when products are available)
rec_engine = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "AI E-commerce Recommendation System"}

@api_router.post("/products/seed")
async def seed_products():
    """Seed initial product data"""
    # Check if products already exist
    existing = await db.products.count_documents({})
    if existing > 0:
        return {"message": f"Products already seeded. Count: {existing}"}
    
    # Sample products across multiple categories
    sample_products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Laptop",
            "category": "Electronics",
            "description": "High-performance laptop with 16GB RAM, 512GB SSD, Intel i7 processor, perfect for work and gaming",
            "price": 1299.99,
            "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop",
            "stock": 50,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Mouse",
            "category": "Electronics",
            "description": "Ergonomic wireless mouse with precision tracking, compatible with laptops and computers",
            "price": 29.99,
            "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&h=500&fit=crop",
            "stock": 200,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Laptop Bag",
            "category": "Accessories",
            "description": "Durable laptop bag with padded compartments, water-resistant material, fits 15-inch laptops",
            "price": 49.99,
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&h=500&fit=crop",
            "stock": 100,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mechanical Keyboard",
            "category": "Electronics",
            "description": "RGB mechanical keyboard with tactile switches, perfect companion for gaming and productivity laptops",
            "price": 89.99,
            "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&h=500&fit=crop",
            "stock": 75,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smartphone",
            "category": "Electronics",
            "description": "Latest smartphone with 5G connectivity, 128GB storage, high-resolution camera, AMOLED display",
            "price": 899.99,
            "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop",
            "stock": 80,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Phone Case",
            "category": "Accessories",
            "description": "Protective phone case with shock absorption, slim design for smartphones, multiple colors available",
            "price": 19.99,
            "image": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500&h=500&fit=crop",
            "stock": 300,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Headphones",
            "category": "Electronics",
            "description": "Noise-cancelling wireless headphones with premium sound quality, long battery life, Bluetooth connectivity",
            "price": 199.99,
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop",
            "stock": 120,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Watch",
            "category": "Electronics",
            "description": "Fitness tracking smartwatch with heart rate monitor, GPS, water-resistant, compatible with smartphones",
            "price": 249.99,
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop",
            "stock": 60,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "USB-C Hub",
            "category": "Accessories",
            "description": "Multi-port USB-C hub for laptops, HDMI output, SD card reader, multiple USB ports for connectivity",
            "price": 39.99,
            "image": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500&h=500&fit=crop",
            "stock": 150,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Portable Charger",
            "category": "Accessories",
            "description": "High-capacity portable charger power bank for smartphones and tablets, fast charging technology",
            "price": 34.99,
            "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&h=500&fit=crop",
            "stock": 180,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Monitor Stand",
            "category": "Accessories",
            "description": "Adjustable monitor stand with storage space, ergonomic design for better posture with laptops and monitors",
            "price": 45.99,
            "image": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=500&h=500&fit=crop",
            "stock": 90,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tablet",
            "category": "Electronics",
            "description": "High-resolution tablet with stylus support, powerful processor, perfect for work and entertainment",
            "price": 599.99,
            "image": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500&h=500&fit=crop",
            "stock": 70,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.products.insert_many(sample_products)
    
    # Initialize recommendation engine
    global rec_engine
    products_list = await db.products.find({}, {"_id": 0}).to_list(1000)
    rec_engine = RecommendationEngine(products_list)
    
    return {"message": f"Successfully seeded {len(sample_products)} products"}

@api_router.get("/products", response_model=List[Product])
async def get_products():
    """Get all products"""
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if isinstance(product.get('created_at'), str):
        product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return product

@api_router.get("/products/{product_id}/recommendations")
async def get_recommendations(product_id: str, limit: int = 4):
    """Get recommended products based on similarity"""
    global rec_engine
    
    # Get the product
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Initialize recommendation engine if not already done
    if rec_engine is None:
        products_list = await db.products.find({}, {"_id": 0}).to_list(1000)
        rec_engine = RecommendationEngine(products_list)
    
    # Get recommendations
    recommendations = rec_engine.get_recommendations(product_id, limit)
    
    return {"recommendations": recommendations}

@api_router.post("/search")
async def search_products(search_req: SearchRequest):
    """Search and filter products"""
    query_filter = {}
    
    # Add category filter if provided
    if search_req.category and search_req.category.lower() != "all":
        query_filter["category"] = search_req.category
    
    # Add text search if query provided
    if search_req.query:
        # Case-insensitive search in name, description, or category
        query_filter["$or"] = [
            {"name": {"$regex": search_req.query, "$options": "i"}},
            {"description": {"$regex": search_req.query, "$options": "i"}},
            {"category": {"$regex": search_req.query, "$options": "i"}}
        ]
    
    products = await db.products.find(query_filter, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps
    for product in products:
        if isinstance(product.get('created_at'), str):
            product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return {"products": products}

@api_router.get("/categories")
async def get_categories():
    """Get all unique product categories"""
    categories = await db.products.distinct("category")
    return {"categories": ["All"] + sorted(categories)}

# Cart Routes
@api_router.post("/cart")
async def add_to_cart(cart_item: CartItemCreate):
    """Add item to cart"""
    # Get product details
    product = await db.products.find_one({"id": cart_item.product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already exists in cart
    existing_item = await db.cart.find_one({"product_id": cart_item.product_id})
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item["quantity"] + cart_item.quantity
        await db.cart.update_one(
            {"product_id": cart_item.product_id},
            {"$set": {"quantity": new_quantity}}
        )
        return {"message": "Cart updated", "quantity": new_quantity}
    else:
        # Create new cart item
        cart_doc = CartItem(
            product_id=cart_item.product_id,
            product_name=product["name"],
            product_price=product["price"],
            product_image=product["image"],
            quantity=cart_item.quantity
        )
        
        doc = cart_doc.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        
        await db.cart.insert_one(doc)
        return {"message": "Added to cart", "item": cart_doc}

@api_router.get("/cart", response_model=List[CartItem])
async def get_cart():
    """Get all cart items"""
    cart_items = await db.cart.find({}, {"_id": 0}).to_list(1000)
    
    for item in cart_items:
        if isinstance(item.get('timestamp'), str):
            item['timestamp'] = datetime.fromisoformat(item['timestamp'])
    
    return cart_items

@api_router.delete("/cart/{cart_id}")
async def remove_from_cart(cart_id: str):
    """Remove item from cart"""
    result = await db.cart.delete_one({"id": cart_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return {"message": "Item removed from cart"}

@api_router.delete("/cart")
async def clear_cart():
    """Clear all cart items"""
    await db.cart.delete_many({})
    return {"message": "Cart cleared"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()