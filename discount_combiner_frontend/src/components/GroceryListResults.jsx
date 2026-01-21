export default function GroceryListResults({ groupedResults }) {
  return (
    <div className="w-full mt-6">
      {groupedResults.map((group, idx) => (
        <div key={idx} className="mb-10">
          
          {/* Title of the list item */}
          <h2 className="text-2xl font-bold mb-4">{group.item}</h2>

          {/* Results grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {group.results.map((offer, i) => (
              <div key={i} className="border rounded p-3 shadow">
                <img
                  src={`http://localhost:3000/${offer.img}`}
                  alt={offer.title}
                  className="w-full h-32 object-cover mb-2"
                />
                <h3 className="font-semibold">{offer.title}</h3>
                <p>{offer.shop}</p>
                <p className="font-bold">{offer.price / 100}€</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
