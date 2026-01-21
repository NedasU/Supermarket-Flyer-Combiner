import "../index.css";

export default function Filter_container({filters, active, onToggle}) {
    return(
    <div className="flex flex-col px-6 pt-3 border-gray-300">
        <h1 className="text-xl lg:text-4xl font-[Open_Sans] pb-2 lg:pb-7 pl-1 text-center">Filtrai</h1>
      <div className="flex flex-row lg:flex-col md:flex-col gap:1 lg:gap-3 px-1 lg:px-0 pb-4 lg:pb-0">
      {filters.map((filter) => (
        <button
          key={filter}
          onClick={() => onToggle(filter)}
          className={`
            px-4 py-2 text-sm rounded-xl uppercase hover:-translate-y-1 hover:scale-110
            ${active.includes(filter)
              ? "bg-blue-600 text-white ease-in-out transition"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200 ease-in-out hover:underline hover:font-bold transition"}
          `}
        >
          <img
            key={filter}
            src={`http://localhost:3000/images/${filter}.jpg`}
            className="w-10 h-10"
            alt=""
          />
        </button>
      ))}
      </div>  
    </div>
    );
}