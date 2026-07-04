#!/usr/bin/env python3
"""
Utility script to add new products to the database.
Usage: python add_product.py
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Sample products you can add
SAMPLE_PRODUCTS = [
    {
        "name": "Gaming Monitor",
        "category": "Electronics",
        "description": "27-inch 4K gaming monitor with 144Hz refresh rate, HDR support, and ultra-low latency for competitive gaming",
        "price": 399.99,
        "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&h=500&fit=crop",
        "stock": 30
    },
    {
        "name": "External SSD",
        "category": "Electronics",
        "description": "1TB portable external SSD with USB-C connectivity, fast data transfer speeds for laptops and computers",
        "price": 129.99,
        "image": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500&h=500&fit=crop",
        "stock": 100
    },
    {
        "name": "Webcam HD",
        "category": "Electronics",
        "description": "1080p HD webcam with auto-focus and built-in microphone, perfect for video calls and streaming with laptop",
        "price": 79.99,
        "image": "https://images.unsplash.com/photo-1625926080331-450dc9a84b98?w=500&h=500&fit=crop",
        "stock": 75
    },
    {
        "name": "Desk Lamp",
        "category": "Accessories",
        "description": "LED desk lamp with adjustable brightness and color temperature, perfect for working with laptop at night",
        "price": 45.99,
        "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&h=500&fit=crop",
        "stock": 60
    }
]

async def add_products():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print(f"\n{'='*80}")
    print(f"➕ ADD NEW PRODUCTS TO DATABASE")
    print(f"{'='*80}\n")
    
    print("Available products to add:\n")
    for i, product in enumerate(SAMPLE_PRODUCTS, 1):
        print(f"{i}. {product['name']} ({product['category']}) - ${product['price']}")
        print(f"   {product['description'][:80]}...")
        print()
    
    print("Options:")
    print("  [1-4] - Add specific product")
    print("  [all] - Add all products")
    print("  [custom] - Add custom product")
    print("  [exit] - Exit\n")
    
    choice = input("Your choice: ").strip().lower()
    
    products_to_add = []
    
    if choice == "exit":
        print("👋 Goodbye!")
        return
    elif choice == "all":
        products_to_add = SAMPLE_PRODUCTS
    elif choice == "custom":
        print("\n📝 Enter product details:")
        custom_product = {
            "name": input("Product name: ").strip(),
            "category": input("Category (Electronics/Accessories): ").strip(),
            "description": input("Description: ").strip(),
            "price": float(input("Price: $").strip()),
            "image": input("Image URL (or press Enter for default): ").strip() or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop",
            "stock": int(input("Stock quantity: ").strip())
        }
        products_to_add = [custom_product]
    elif choice.isdigit() and 1 <= int(choice) <= len(SAMPLE_PRODUCTS):
        products_to_add = [SAMPLE_PRODUCTS[int(choice) - 1]]
    else:
        print("❌ Invalid choice!")
        return
    
    # Add products to database
    print(f"\n⏳ Adding {len(products_to_add)} product(s)...\n")
    
    for product in products_to_add:
        product_doc = {
            "id": str(uuid.uuid4()),
            "name": product["name"],
            "category": product["category"],
            "description": product["description"],
            "price": product["price"],
            "image": product["image"],
            "stock": product["stock"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.products.insert_one(product_doc)
        print(f"✅ Added: {product['name']} (ID: {product_doc['id'][:8]}...)")
    
    # Show updated count
    total_count = await db.products.count_documents({})
    print(f"\n📊 Total products in database: {total_count}")
    print(f"\n💡 Run 'python test_recommendations.py' to see updated recommendations!\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_products())
