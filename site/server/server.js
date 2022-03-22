const bodyParser = require('body-parser');
const express = require('express');
const { exec } = require("child_process");

const app = express();
var cors = require('cors') // New
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
const fs = require('fs');
const path = require('path');
app.use(cors());

// const dataVitals = JSON.parse(fs.readFileSync(path.join(__dirname, 'vitals_face.json')));
const dataVitals = JSON.parse(fs.readFileSync("/home/harshit/college/Sem-6/IOT/Project/NayanCom/site/server/vitals_face.json"));

// let dirName = path.join(__dirname, 'vitals_face.json');
var python_started = false;

app.get("/", async (req, res) => {
    // console.log(dirName);
    console.log(dataVitals);

    if(python_started == false){

        // run the file 
        var yourscript = exec('bash run_python.sh',
        (error, stdout, stderr) => {
            console.log(stdout);
            console.log(stderr);
            if (error !== null) {
                console.log(`exec error: ${error}`);
            }
        });
        python_started = true;
    }

    // add command for bash script 
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