import { useState } from "react";

export default function GroceryListPanel({ groceryList, setGroceryList }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");

  function addItem() {
    if (!input.trim()) return;
    setGroceryList(prev => [...prev, input.trim()]);
    setInput("");
  }

  return (
    <div className="relative">
      {/* Toggle Button */}
      <button
        onClick={() => setOpen(!open)}
        className="px-3 py-2 bg-gray-200 rounded shadow text-sm font-semibold"
      >
        My List
      </button>

      {/* Sliding Panel */}
      {open && (
        <div className="absolute right-0 mt-2 min-w-64 bg-white shadow-xl p-4 rounded z-50 border">
          <h3 className="font-bold mb-2 text-lg">Grocery List</h3>

          {/* Input */}
          <div className="flex gap-2 mb-3">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Add item..."
              className="flex-1 border rounded px-2 py-1"
            />
            <button
              onClick={addItem}
              className="bg-blue-500 text-white px-2 py-1 rounded"
            >
              Add
            </button>
          </div>

          {/* List Items */}
          <ul className="space-y-1 max-h-48 overflow-y-auto">
            {groceryList.map((item, i) => (
              <li key={i} className="flex justify-between items-center">
                <span>{item}</span>
                <button
                  className="text-red-500"
                  onClick={() =>
                    setGroceryList(prev => prev.filter((_, idx) => idx !== i))
                  }
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

