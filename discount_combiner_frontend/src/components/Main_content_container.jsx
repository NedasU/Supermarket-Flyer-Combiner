// src/components/Main_content_container.jsx
import React from "react";
import "../Index.css";

/**
 * Props:
 * - offers: flat array of offer objects (for normal mode & infinite scroll)
 * - groupedResults: array of groups: [{ item: "potatoes", results: [offer, offer...] }, ...]
 * - isGrouped: boolean - whether groupedResults should be used
 * - lastOfferRef: optional ref attached to the last rendered offer in flat mode for infinite scroll
 */
export default function Main_content_container({
  offers = [],
  groupedResults = [],
  isGrouped = false,
  lastOfferRef = null,
}) {
  const formatPrice = (p) =>
    p == null ? "" : (p / 100).toLocaleString("en-US", { style: "currency", currency: "EUR" });

  const formatDateRange = (start, end) => {
    if (!start && !end) return "";
    if (start && end) return `${start} - ${end}`;
    if (start) return `Nuo ${start}`;
    return `Iki ${end}`;
  };

  // Render a single offer card - used by both modes
  const OfferCard = ({ offer, refProp }) => {
    return (
      <div
        ref={refProp || null}
        key={offer.id}
        className="flex flex-col p-4 basis-full sm:basis-1/2 lg:basis-1/3 bg-white rounded shadow transition-transform hover:scale-105"
      >
        <div className="relative">
          <img
            src={offer.img}
            loading="lazy"
            alt={offer.title}
            className="w-full h-40 object-contain rounded-lg mb-3"
          />

          {offer.additional_info && (
            <div className="absolute left-2 bottom-2 flex gap-none">
              {Array.from({ length: Math.max(0, (offer.additional_info.match(/X/g) || []).length) }).map(
                (_, i) => (
                  <img
                    key={i}
                    src={`http://localhost:3000/images/${offer.shop}_icon.png`}
                    className="w-4 h-4"
                    alt=""
                  />
                )
              )}
            </div>
          )}

          {offer.discount && (
            <div className="absolute bottom-2 right-2 bg-red-600 text-white text-sm font-bold px-2 py-1 rounded-md">
              {offer.discount}
            </div>
          )}
        </div>

        <img
          src={`http://localhost:3000/images/${offer.shop}.jpg`}
          loading="lazy"
          alt={offer.shop}
          className="w-9 h-auto object-contain mx-auto mb-2"
        />

        <h2 className="text-lg font-semibold mb-2 text-center">{offer.title}</h2>

        <div className="mt-auto text-center">
          {offer.old_price && <p className="text-gray-500 line-through">{formatPrice(offer.old_price)}</p>}
          {offer.price && <p className="text-xl font-bold text-red-600">{formatPrice(offer.price)}</p>}
          <p className="text-sm text-gray-600 mt-2">{formatDateRange(offer.date_start, offer.date_end)}</p>
        </div>
      </div>
    );
  };

  // If grouped mode — iterate groups and render title + grid of group's results
  if (isGrouped && groupedResults.length > 0) {
    return (
      <div className="w-full space-y-8">
        {groupedResults.map((group) => (
          <section key={group.item} className="w-full">
            <h3 className="text-2xl font-bold mb-4">{group.item}</h3>

            {group.results && group.results.length > 0 ? (
              <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                {group.results.map((offer) => (
                  <OfferCard key={offer.id} offer={offer} />
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No results for {group.item}</p>
            )}
          </section>
        ))}
      </div>
    );
  }

  // Normal (flat) mode
  return (
    <div>
      {offers.length === 0 ? (
        <h2 className="font-bold text-3xl">No Results Found!</h2>
      ) : (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 pb-5">
          {offers.map((offer, index) => {
            const isLast = index === offers.length - 1;
            return <OfferCard key={offer.id} offer={offer} refProp={isLast ? lastOfferRef : null} />;
          })}
        </div>
      )}
    </div>
  );
}
