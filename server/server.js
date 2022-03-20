const bodyParser = require('body-parser');
const express = require('express');
const app = express();
var cors = require('cors') // New
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
const fs = require('fs');
const path = require('path');
app.use(cors());

const dataVitals = JSON.parse(fs.readFileSync(path.join(__dirname, 'vitals_face.json')));

app.get("/", async (req, res) => {
    console.log(dataVitals);
    return res.json(dataVitals);
})

const writeToFile = async (data, path) => {
    const json = JSON.stringify(data, null, 2)
    await fs.writeFile(path, json, (err) => {
        if (err) {
            console.error(err)
            throw err
        }
        console.log('Saved data to file.')
    })
}

app.post("/api", async (request, response) => {
    console.log(request.body);
    writeToFile(request.body, "output.json");
    return response.status(202).json("done");
})

app.listen(5000, () => { console.log("Server started on port 5000") })