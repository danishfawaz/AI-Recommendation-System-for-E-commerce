import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, ShoppingCart, Sparkles, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProductDetail = ({ onCartUpdate }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProductDetails();
  }, [id]);

  const fetchProductDetails = async () => {
    try {
      // Fetch product details
      const productResponse = await axios.get(`${API}/products/${id}`);
      setProduct(productResponse.data);

      // Fetch recommendations
      const recResponse = await axios.get(`${API}/products/${id}/recommendations`);
      setRecommendations(recResponse.data.recommendations);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching product details:', error);
      toast.error('Failed to load product details');
      setLoading(false);
    }
  };

  const addToCart = async (productToAdd) => {
    try {
      await axios.post(`${API}/cart`, {
        product_id: productToAdd.id,
        quantity: 1
      });
      toast.success(`${productToAdd.name} added to cart!`);
      onCartUpdate();
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error('Failed to add to cart');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading product...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 text-lg mb-4">Product not found</p>
          <Button onClick={() => navigate('/')}>Back to Products</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Button
          data-testid="back-button"
          onClick={() => navigate('/')}
          variant="ghost"
          className="mb-6 hover:bg-gray-100"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Products
        </Button>

        {/* Product Details */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Product Image */}
          <div className="relative">
            <div className="aspect-square rounded-2xl overflow-hidden bg-white shadow-xl border-2 border-gray-100">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
            <Badge className="absolute top-4 left-4 bg-blue-600 text-white px-4 py-2 text-sm">
              {product.category}
            </Badge>
          </div>

          {/* Product Info */}
          <div className="flex flex-col justify-center space-y-6">
            <div>
              <h1 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {product.name}
              </h1>
              <p className="text-base text-gray-600 leading-relaxed">
                {product.description}
              </p>
            </div>

            <div className="flex items-baseline space-x-4">
              <span className="text-5xl font-bold text-blue-600">
                ${product.price.toFixed(2)}
              </span>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <Package className="w-5 h-5 text-green-600" />
                <span className="font-medium">{product.stock} in stock</span>
              </div>
            </div>

            <Button
              data-testid="add-to-cart-detail"
              onClick={() => addToCart(product)}
              className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
            >
              <ShoppingCart className="w-5 h-5 mr-2" />
              Add to Cart
            </Button>
          </div>
        </div>

        {/* AI Recommendations */}
        {recommendations.length > 0 && (
          <div className="mt-16">
            <div className="flex items-center space-x-3 mb-8">
              <Sparkles className="w-6 h-6 text-purple-600" />
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                You May Also Like
              </h2>
            </div>
            <p className="text-gray-600 mb-8 text-base">
              AI-powered recommendations based on product similarity
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {recommendations.map((rec) => (
                <Card
                  key={rec.id}
                  data-testid={`recommendation-${rec.id}`}
                  onClick={() => navigate(`/product/${rec.id}`)}
                  className="group cursor-pointer overflow-hidden hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-purple-200 bg-white"
                >
                  <div className="relative aspect-square overflow-hidden">
                    <img
                      src={rec.image}
                      alt={rec.name}
                      className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute top-2 right-2 bg-purple-600 text-white text-xs font-semibold px-2 py-1 rounded-full">
                      {Math.round(rec.similarity_score * 100)}% match
                    </div>
                  </div>

                  <CardContent className="p-4">
                    <h3 className="font-semibold text-base mb-2 line-clamp-1 group-hover:text-purple-600 transition-colors">
                      {rec.name}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                      {rec.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xl font-bold text-purple-600">
                        ${rec.price.toFixed(2)}
                      </span>
                      <Button
                        data-testid={`add-rec-${rec.id}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          addToCart(rec);
                        }}
                        size="sm"
                        className="bg-purple-600 hover:bg-purple-700"
                      >
                        <ShoppingCart className="w-3 h-3 mr-1" />
                        Add
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;