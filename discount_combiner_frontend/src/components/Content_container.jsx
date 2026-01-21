import "../index.css";

export default function Content_container({ children }) {
    return(
        <div className="flex lg:flex-row flex-col w-full h-full border-[1px] border-gray-100">
            { children }
        </div>
)};