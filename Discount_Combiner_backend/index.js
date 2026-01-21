const express = require("express");
const pool = require("./db");
const cors = require("cors");
const path = require("path");

const { spawn } = require("child_process");

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(cors());
app.use("/images", express.static(path.join(__dirname, "images")));

const offersRoute = require("./routes/offers");
app.use("/api/search", offersRoute);

function startScraperOnBoot() {
  const process = spawn("python", ["../Flyer_reader/csv_to_sql.py"], {
    stdio: "inherit", // shows logs in backend console
  });

  process.on("close", (code) => {
    console.log("Scraper finished with code:", code);
  });

  process.on("error", (err) => {
    console.error("Failed to start scraper:", err);
  });
}



app.get("/", (req, res) => res.send("Backend running"));

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  startScraperOnBoot();
});

