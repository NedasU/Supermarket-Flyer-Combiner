const { Pool, types } = require('pg');
require('dotenv').config();

types.setTypeParser(1082, (val) => val);

// Create a pool of connections to PostgreSQL
const pool = new Pool({
    user: "postgres",
    host: "localhost",
    "database": "grocery_discounts",
    password: process.env.PostGreSQL_password,
    port: 5432,
});

module.exports = pool;