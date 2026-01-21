// routes/offers.js
const express = require("express");
const router = express.Router();
const pool = require("../db");
const unidecode = require("unidecode");

function normalize(str = "") {
  return unidecode(String(str).toLowerCase());
}

function parseFilters(filters) {
  if (!filters) return null;
  if (Array.isArray(filters)) return filters.map(f => f.toLowerCase());
  return filters.split(",").map(f => f.toLowerCase());
}

/**
 * GET /api/search (this router is mounted at /api/search)
 * Query params:
 *   q: search query
 *   filters: comma-separated shops (optional)
 *   limit: number (default 40)
 *   offset: number (default 0)
 */
router.get("/", async (req, res) => {
  try {
    const rawQ = req.query.q ?? "";
    const qTrim = rawQ.trim();
    const q = normalize(rawQ).trim();
    const filters = parseFilters(req.query.filters);
    const limit = Math.min(parseInt(req.query.limit || "40", 10), 200);
    const offset = parseInt(req.query.offset || "0", 10);

    // If no search query -> simple filtered list (paged)
    if (!qTrim) {
      const sql = `
        SELECT id, title, shop, price, old_price, date_start, date_end, img, additional_info, discount
        FROM main_offers
        ${filters ? "WHERE shop = ANY($1)" : ""}
        ORDER BY id ASC
        LIMIT $${filters ? 2 : 1} OFFSET $${filters ? 3 : 2};
      `;
      const params = filters ? [filters, limit, offset] : [limit, offset];
      const r = await pool.query(sql, params);
      return res.json(r.rows);
    }

    // If searching: 1) try full-text search with ranking
    // Use deterministic ordering: rank DESC then id ASC so paging is stable
    const fullTextSql = `
      SELECT id, title, shop, price, old_price, date_start, date_end, img, additional_info, discount,
        ts_rank_cd(to_tsvector('simple', title_normalized), plainto_tsquery('simple', $1)) AS rank
      FROM main_offers
      WHERE to_tsvector('simple', title_normalized) @@ plainto_tsquery('simple', $1)
      ${filters ? "AND shop = ANY($2)" : ""}
      ORDER BY rank DESC, id ASC
      LIMIT $${filters ? 3 : 2} OFFSET $${filters ? 4 : 3};
    `;
    const fullTextParams = filters ? [q, filters, limit, offset] : [q, limit, offset];

    const fullTextResult = await pool.query(fullTextSql, fullTextParams);

    // If full-text returns results for this page, return them.
    if (fullTextResult.rows.length > 0) {
      return res.json(fullTextResult.rows);
    }

    // 2) Fallback to ILIKE match (if no full-text matches)
    // Use same deterministic ordering (id ASC)
    const likeSql = `
      SELECT id, title, shop, price, old_price, date_start, date_end, img, additional_info, discount
      FROM main_offers
      WHERE title_normalized ILIKE $1
      ${filters ? "AND shop = ANY($2)" : ""}
      ORDER BY id ASC
      LIMIT $${filters ? 3 : 2} OFFSET $${filters ? 4 : 3};
    `;
    const likeParams = filters ? [`%${q}%`, filters, limit, offset] : [`%${q}%`, limit, offset];

    const likeResult = await pool.query(likeSql, likeParams);
    return res.json(likeResult.rows);

  } catch (err) {
    console.error("Offers route error:", err);
    res.status(500).json({ error: "Server error" });
  }
});

module.exports = router;
