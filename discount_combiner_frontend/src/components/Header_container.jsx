import "../index.css";

export default function Header_container({children}){
    return(
        <div className="flex  w-full h-[10vh] lg:h-[20vh] md:h-[20vh] border-b-[1px] border-b-gray-200">
            { children }
        </div>
    )
}