const axios = require("axios");
const express = require("express");
const fetch = require("node-fetch");

const app = express();
const port = process.env.PORT || 3000;
// include data
const public_data = require("./public_table_data.json"); 

app.use(express.json());
app.use(express.static("public"));

app.listen(port, () => {
    console.log(`Starting server at: ${port}`);
});

// send data to DataTable API
app.get("/publicData", function (req, res) {
    res.json({
        "data": public_data
    })
});
