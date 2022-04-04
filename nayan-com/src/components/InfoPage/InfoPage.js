import './InfoPage.css';
import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

// gifs
// import vital_not_gif from '../../images/Vitals_not_working.gif';
// import face_not_gif from '../../images/Face_not_detected.gif';
// import vital_gif from '../../images/giphy.gif';
// import face_gif from '../../images/face.gif';

// images
import vital_not_gif from '../../images/not_vitals.png';
import face_not_gif from '../../images/not_face.png';
import vital_gif from '../../images/has_vitals.png';
import face_gif from '../../images/has_face.png';

import Header from '../header/header';


function InfoPage() {
    const [data, setData] = useState([]);
    const [data2, setData2] = useState(false);
    const [loading, setLoading] = useState(true)
    const getData = (x) => {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const options = {
            method: 'GET',
            headers: myHeaders,
            redirect: "follow",
        }
        fetch(`http://localhost:5000/${x}`, options).then((response) => response.json())
            .then(async (myJson) => {
                console.log(myJson)
                await setData(myJson)
                setLoading(false)
            }).then(() => {
                console.log(data);
            }).catch((err) => console.log('error1236'));
    }
    
    const onSubmit = () => {
        setData2(false);
        getData("backendVitals");
    };

    const offSubmit = () => {
        setLoading(true);
        setData2(true);
        getData("stopScript");
    };

    useEffect(() => {
        setInterval(() => {
            getData("backendVitals");
            console.log("hi")
        }, 7000);
    }, []);

    return (
        <div className="ihomepage" >
            <Header />
            <div className="iseparator">
                Redefining patient well being.
            </div>
            <div className="ibutton">
                <button defaultValue={false} onClick={() => onSubmit()} className="btn btn-primary my-3" value="Submit" >
                    Start Processing
                </button>
                <button defaultValue={false} onClick={() => offSubmit()} className="btn btn-danger my-3" value="Submit" >
                    Stop Processing
                </button>
            </div>
            <div className="ibody" >
                 <div className="ileftBody" style={{ visibility: data2 == false ? 'visible': 'hidden'}}>
                    {loading ? <></> : data.patient.vitals_detected ? <img src={vital_gif} alt="loading..." /> : <img src={vital_not_gif} alt="loading..." />}
                </div>
                <div className="irightBody" style={{ visibility: data2 == false ? 'visible': 'hidden'}}>
                    {loading ? <></> : data.patient.in_view ? <img src={face_gif} alt="loading..." /> : <img src={face_not_gif} alt="loading..." />}
                </div>
            </div>
        </div>
    )
};

export default InfoPage;