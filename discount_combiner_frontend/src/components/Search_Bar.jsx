import "../index.css";
import { useEffect, useState } from "react";


export default function Search_bar({searchQuery, setSearchQuery}) {
    const [text, setText] = useState(searchQuery);

    useEffect(() => {
    const id = setTimeout(() => {
      setSearchQuery(text);
    }, 300);

    return () => clearTimeout(id);
    }, [text]);

    return (
        <div className="flex flex-grow items-center w-full h-full px-12">
            <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Search offers..."
                className="
                    w-full
                    max-w-xl
                    px-4 
                    py-2
                    bg-white 
                    rounded-xl
                    border 
                    border-gray-300
                    focus:outline-none 
                    focus:ring-2 
                    focus:ring-blue-500 
                    focus:border-transparent
                    text-gray-800
                "
            />
            <div className={
                searchQuery ? "text-gray-800" : "text-gray-200"

            }>
                X
            </div>
        </div>
    );
};