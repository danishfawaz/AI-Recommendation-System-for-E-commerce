import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingCart, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const Navbar = ({ cartCount }) => {
  const location = useLocation();

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center transform group-hover:scale-110 transition-transform duration-200">
              <Package className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SmartShop AI
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-4">
            <Link to="/">
              <Button
                data-testid="home-nav-button"
                variant={location.pathname === '/' ? 'default' : 'ghost'}
                className="font-medium"
              >
                Products
              </Button>
            </Link>

            <Link to="/cart">
              <Button
                data-testid="cart-nav-button"
                variant={location.pathname === '/cart' ? 'default' : 'ghost'}
                className="relative font-medium"
              >
                <ShoppingCart className="w-5 h-5 mr-2" />
                Cart
                {cartCount > 0 && (
                  <Badge
                    data-testid="cart-count-badge"
                    className="absolute -top-2 -right-2 bg-red-500 text-white px-2 py-0.5 text-xs"
                  >
                    {cartCount}
                  </Badge>
                )}
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;