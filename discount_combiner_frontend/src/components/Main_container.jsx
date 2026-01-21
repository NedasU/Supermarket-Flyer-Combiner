import "../index.css";


export default function Main_container({ children }) {
 
  return (
    <div className="bg-gray-100 min-h-screen flex flex-col h-full w-full px-[10%] mx-auto my-auto">
        { children }
    </div>
  );
}