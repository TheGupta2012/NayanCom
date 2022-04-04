const bodyParser = require('body-parser');
const express = require('express');
const { exec  }= require('child_process');
const app = express();
var cors = require('cors') // New
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
const fs = require('fs');
const path = require('path');
app.use(cors());

var python_start = false;

const reset_patient = {
        "patient" : {
            "in_view" : false,
            "vitals_detected" : false
        }
    }
// write the details of caretaker to the file 
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

// route for the starting of python script and the reading of patient vars
app.get("/backendVitals", async (req, res) => {
    var dataVitals = JSON.parse(fs.readFileSync(path.join(__dirname, './data/vitals_face.json')));
    console.log(dataVitals);

    if (python_start == false) {
        // run the file 
        var yourscript = exec('bash run_python.sh',
            (error, stdout, stderr) => {
                console.log(stdout);
                console.log(stderr);
                if (error !== null) {
                    console.log(`exec error: ${error}`);
                }
            });
        python_start = true;
    }
    return res.json(dataVitals);
})

app.get("/readVitals", async (req, res) => {
    var dataVitals = JSON.parse(fs.readFileSync(path.join(__dirname, './data/vitals_face.json')));
    console.log(dataVitals);
    return res.json(dataVitals);
})

// stopping the python scripts 
app.get("/stopScript", async (req, res) => {
    var pid_vitals = JSON.parse(fs.readFileSync(path.join(__dirname, './data/pid_vitals.json')));
    var pid_cv = JSON.parse(fs.readFileSync(path.join(__dirname, './data/pid_cv.json')));

    if (python_start == true) {
        // kill the scripts
        if (pid_vitals != "None")
        {   var killscript1 = exec(`kill ${pid_vitals.id}`,
                (error, stdout, stderr) => {
                    console.log(stdout);
                    console.log(stderr);
                    if (error !== null) {
                        console.log(`exec error: ${error}`);
                    }
                });
        }
        if(pid_cv != "None")
        {
        var killscript2 = exec(`kill ${pid_cv.id}`,
            (error, stdout, stderr) => {
                console.log(stdout);
                console.log(stderr);
                if (error !== null) {
                    console.log(`exec error: ${error}`);
                }
            });
        }
        python_start = false;
    }
    writeToFile(reset_patient, "./data/vitals_face.json");
})



app.post("/api", async (request, response) => {
    console.log(request.body);
    writeToFile(request.body, "./data/contact_details.json");
    return response.status(202).json("done");
})

app.listen(5000, () => { console.log("Server started on port 5000") })