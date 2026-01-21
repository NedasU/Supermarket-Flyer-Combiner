// src/App.jsx
import { useState, useEffect, useRef } from "react";
import "./App.css";

import Main_container from "./components/Main_container.jsx";
import Header_container from "./components/Header_container.jsx";
import Filter_container from "./components/filter_container.jsx";
import Main_content_container from "./components/Main_content_container.jsx";
import Content_container from "./components/Content_container.jsx";
import Search_Bar from "./components/Search_Bar.jsx";
import GroceryListPanel from "./components/GroceryListPanel.jsx";

function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  const [activeFilters, setActiveFilters] = useState([]);
  const [offers, setOffers] = useState([]);

  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const [groceryList, setGroceryList] = useState([]);
  const [groupedResults, setGroupedResults] = useState([]);

  const LIMIT = 40;
  const abortRef = useRef(null);
  const filters = ["maxima", "iki", "rimi", "lidl"];

  // -----------------------------
  // Debounce search
  // -----------------------------
  useEffect(() => {
    const id = setTimeout(() => {
      setDebouncedQuery(searchQuery.trim());

      // if user manually searches → exit grocery list mode
      if (searchQuery.trim() !== "") {
        setGroupedResults([]);
      }
    }, 300);

    return () => clearTimeout(id);
  }, [searchQuery]);

  // -----------------------------
  // Toggle shop filter
  // -----------------------------
  function toggleFilter(filter) {
    setActiveFilters(prev =>
      prev.includes(filter)
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    );

    // If filters changed → exit grocery list mode
    setGroupedResults([]);
  }

  // -----------------------------
  // Normal offer fetch
  // -----------------------------
  async function fetchOffers(reset = false) {
    if (loading) return;
    setLoading(true);

    // abort previous pending fetch if resetting
    if (reset && abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const offset = reset ? 0 : offers.length;

      const q = encodeURIComponent(debouncedQuery);
      const filtersParam = encodeURIComponent(activeFilters.join(","));

      const url = `http://localhost:3000/api/search?q=${q}&filters=${filtersParam}&limit=${LIMIT}&offset=${offset}`;

      const res = await fetch(url, { signal: controller.signal });
      const data = await res.json();

      if (reset) {
        setOffers(data);
      } else {
        // prevent duplicates
        setOffers(prev => {
          const existing = new Set(prev.map(p => p.id));
          const add = data.filter(d => !existing.has(d.id));
          return [...prev, ...add];
        });
      }

      setHasMore(data.length === LIMIT);
    } catch (err) {
      if (err.name !== "AbortError") console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // -----------------------------
  // Fetch grouped grocery list results
  // -----------------------------
  async function fetchGroceryListResults() {
    if (groceryList.length === 0) {
      setGroupedResults([]);
      return;
    }

    const groups = [];
    for (const item of groceryList) {
      const res = await fetch(
        `http://localhost:3000/api/search?q=${encodeURIComponent(item)}&limit=40`
      );
      const data = await res.json();

      groups.push({ item, results: data });
    }

    setGroupedResults(groups);
  }

  useEffect(() => {
    fetchGroceryListResults();
  }, [groceryList]);

  // -----------------------------
  // Reset offers on search/filter change
  // -----------------------------
  useEffect(() => {
    // Only fetch offers if not in grouped list mode
    if (groupedResults.length > 0) return;

    setOffers([]);
    setHasMore(true);
    fetchOffers(true);
  }, [debouncedQuery, activeFilters]);

  // -----------------------------
  // Infinite scroll
  // -----------------------------
  useEffect(() => {
    if (!hasMore || loading || groupedResults.length > 0) return;

    function onScroll() {
      const nearBottom =
        window.innerHeight + window.scrollY >=
        document.body.offsetHeight - 400;

      if (nearBottom) fetchOffers(false);
    }

    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [hasMore, loading, groupedResults]);

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <Main_container>
      <Header_container>
        <Search_Bar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
        <GroceryListPanel
          groceryList={groceryList}
          setGroceryList={setGroceryList}
        />
      </Header_container>

      <Content_container>
        <Filter_container
          active={activeFilters}
          onToggle={toggleFilter}
          filters={filters}
        />
      <Main_content_container
        offers={offers}
        groupedResults={groupedResults}
        isGrouped={groupedResults && groupedResults.length > 0}
      />
      </Content_container>

      {loading && <div className="text-center py-4 text-gray-600">Loading...</div>}
    </Main_container>
  );
}

export default App;
