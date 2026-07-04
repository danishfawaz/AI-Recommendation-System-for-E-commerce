#!/usr/bin/env python3
"""
Utility script to test and view product recommendations.
Usage: python test_recommendations.py
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from recommendation import RecommendationEngine

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def main():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Fetch all products
    products = await db.products.find({}, {"_id": 0}).to_list(1000)
    
    if not products:
        print("❌ No products found. Please seed products first.")
        return
    
    print(f"\n{'='*80}")
    print(f"🤖 AI PRODUCT RECOMMENDATION SYSTEM - Testing Tool")
    print(f"{'='*80}\n")
    print(f"Total products in database: {len(products)}\n")
    
    # Initialize recommendation engine
    rec_engine = RecommendationEngine(products)
    
    # Test recommendations for each product
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']} ({product['category']}) - ${product['price']}")
        
        # Get recommendations
        recommendations = rec_engine.get_recommendations(product['id'], num_recommendations=4)
        
        if recommendations:
            print(f"   📊 Recommended products:")
            for rec in recommendations:
                similarity_percent = round(rec['similarity_score'] * 100)
                print(f"      → {rec['name']} ({rec['category']}) - {similarity_percent}% match - ${rec['price']}")
        else:
            print(f"   ℹ️  No recommendations available")
        
        print()
    
    # Summary statistics
    print(f"\n{'='*80}")
    print(f"📈 RECOMMENDATION STATISTICS")
    print(f"{'='*80}\n")
    
    categories = {}
    for product in products:
        cat = product['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("Products by category:")
    for cat, count in sorted(categories.items()):
        print(f"  • {cat}: {count} products")
    
    print(f"\n✅ Recommendation engine is working correctly!")
    print(f"💡 Add more products to improve recommendation accuracy.\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
