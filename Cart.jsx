import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Trash2, ShoppingBag, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Cart = ({ onCartUpdate }) => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API}/cart`);
      setCartItems(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching cart:', error);
      toast.error('Failed to load cart');
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId, itemName) => {
    try {
      await axios.delete(`${API}/cart/${itemId}`);
      toast.success(`${itemName} removed from cart`);
      fetchCart();
      onCartUpdate();
    } catch (error) {
      console.error('Error removing from cart:', error);
      toast.error('Failed to remove item');
    }
  };

  const clearCart = async () => {
    try {
      await axios.delete(`${API}/cart`);
      toast.success('Cart cleared');
      fetchCart();
      onCartUpdate();
    } catch (error) {
      console.error('Error clearing cart:', error);
      toast.error('Failed to clear cart');
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.product_price * item.quantity), 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading cart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Button
          data-testid="back-to-products"
          onClick={() => navigate('/')}
          variant="ghost"
          className="mb-6 hover:bg-gray-100"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Continue Shopping
        </Button>

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Shopping Cart
          </h1>
          <p className="text-base text-gray-600">
            {cartItems.length === 0 ? 'Your cart is empty' : `${cartItems.length} item${cartItems.length > 1 ? 's' : ''} in your cart`}
          </p>
        </div>

        {cartItems.length === 0 ? (
          <div className="text-center py-16">
            <ShoppingBag className="w-24 h-24 text-gray-300 mx-auto mb-6" />
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Your cart is empty</h2>
            <p className="text-gray-600 mb-8">Looks like you haven't added anything to your cart yet.</p>
            <Button
              data-testid="start-shopping"
              onClick={() => navigate('/')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3"
            >
              Start Shopping
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2 space-y-4">
              {cartItems.map((item) => (
                <Card key={item.id} data-testid={`cart-item-${item.id}`} className="overflow-hidden hover:shadow-lg transition-shadow bg-white">
                  <CardContent className="p-4">
                    <div className="flex gap-4">
                      {/* Product Image */}
                      <div
                        className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer"
                        onClick={() => navigate(`/product/${item.product_id}`)}
                      >
                        <img
                          src={item.product_image}
                          alt={item.product_name}
                          className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                        />
                      </div>

                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <h3
                          className="font-semibold text-lg mb-1 cursor-pointer hover:text-blue-600 transition-colors"
                          onClick={() => navigate(`/product/${item.product_id}`)}
                        >
                          {item.product_name}
                        </h3>
                        <p className="text-gray-600 text-sm mb-2">Quantity: {item.quantity}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold text-blue-600">
                            ${(item.product_price * item.quantity).toFixed(2)}
                          </span>
                          <Button
                            data-testid={`remove-item-${item.id}`}
                            onClick={() => removeFromCart(item.id, item.product_name)}
                            variant="destructive"
                            size="sm"
                            className="bg-red-500 hover:bg-red-600"
                          >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Remove
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              <Button
                data-testid="clear-cart"
                onClick={clearCart}
                variant="outline"
                className="w-full border-red-500 text-red-500 hover:bg-red-50"
              >
                Clear Cart
              </Button>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-24 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
                <CardContent className="p-6 space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">Order Summary</h2>

                  <div className="space-y-3">
                    <div className="flex justify-between text-gray-600">
                      <span>Subtotal</span>
                      <span className="font-medium">${calculateTotal().toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-gray-600">
                      <span>Shipping</span>
                      <span className="font-medium text-green-600">FREE</span>
                    </div>
                    <div className="border-t border-gray-300 pt-3">
                      <div className="flex justify-between text-xl font-bold">
                        <span>Total</span>
                        <span data-testid="cart-total" className="text-blue-600">${calculateTotal().toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                  <Button
                    data-testid="checkout-button"
                    className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
                    onClick={() => toast.success('Checkout feature coming soon!')}
                  >
                    Proceed to Checkout
                  </Button>

                  <p className="text-xs text-gray-500 text-center">
                    Secure checkout powered by AI recommendations
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cart;