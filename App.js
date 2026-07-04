import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import Navbar from "@/components/Navbar";
import ProductList from "@/components/ProductList";
import ProductDetail from "@/components/ProductDetail";
import Cart from "@/components/Cart";
import { Toaster } from "@/components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [cartCount, setCartCount] = useState(0);

  // Fetch cart count
  const fetchCartCount = async () => {
    try {
      const response = await axios.get(`${API}/cart`);
      const totalItems = response.data.reduce((sum, item) => sum + item.quantity, 0);
      setCartCount(totalItems);
    } catch (error) {
      console.error("Error fetching cart count:", error);
    }
  };

  useEffect(() => {
    // Seed products on first load
    const initializeProducts = async () => {
      try {
        await axios.post(`${API}/products/seed`);
      } catch (error) {
        console.error("Error seeding products:", error);
      }
    };

    initializeProducts();
    fetchCartCount();
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <Navbar cartCount={cartCount} />
        <Routes>
          <Route path="/" element={<ProductList onCartUpdate={fetchCartCount} />} />
          <Route path="/product/:id" element={<ProductDetail onCartUpdate={fetchCartCount} />} />
          <Route path="/cart" element={<Cart onCartUpdate={fetchCartCount} />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </div>
  );
}

export default App;