const { Pool, types } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

types.setTypeParser(1082, (val) => val);

const pool = new Pool({
    user: "postgres",
    host: "localhost",
    database: "grocery_discounts",
    password: process.env.POSTGRESQL_PASSWORD,
    port: 5432,
});

module.exports = pool;