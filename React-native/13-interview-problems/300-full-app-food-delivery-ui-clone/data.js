// data.js — dummy restaurants (replace with API later)
export const RESTAURANTS = [
  { id: 'r1', name: 'Biryani Blues', cuisine: 'Biryani, North Indian', rating: 4.3, time: 30, offer: '50% OFF up to Rs 100',
    menu: [{ id: 'm1', name: 'Chicken Dum Biryani', price: 299 }, { id: 'm2', name: 'Paneer Biryani', price: 249 }, { id: 'm3', name: 'Raita', price: 49 }] },
  { id: 'r2', name: 'Pizza Hub', cuisine: 'Pizza, Italian', rating: 4.1, time: 25, offer: 'Free delivery',
    menu: [{ id: 'm4', name: 'Margherita', price: 199 }, { id: 'm5', name: 'Farmhouse', price: 349 }] },
  { id: 'r3', name: 'South Tiffin', cuisine: 'South Indian', rating: 4.5, time: 20, offer: '20% OFF',
    menu: [{ id: 'm6', name: 'Masala Dosa', price: 99 }, { id: 'm7', name: 'Idli Sambar', price: 79 }] },
];
export const CATEGORIES = ['All', 'Biryani', 'Pizza', 'South Indian']; // filter chips
