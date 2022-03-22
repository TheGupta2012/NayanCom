import './InfoPage.css';
import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import vital_not_gif from '../../images/Vitals_not_working.gif';
import face_not_gif from '../../images/Face_not_detected.gif';
import vital_gif from '../../images/giphy.gif';
import face_gif from '../../images/face.gif';
import Header from '../header/header';


function InfoPage() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true)
    const getData = () => {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const options = {
            method: 'GET',
            headers: myHeaders,
            redirect: "follow",
        }
        fetch("http://localhost:5000", options).then((response) => response.json())
            .then(async (myJson) => {
                console.log(myJson)
                await setData(myJson)

                setLoading(false)
            }).then(() => {
                console.log(data);
            }).catch((err) => console.log('error1236'));

    }
    const onSubmit = (() => getData());
    const offSubmit = () => {
        setLoading(true)
    }

    // useEffect(() => {
    //     setInterval(() => {
    //         onSubmit();
    //     }, 5000);
    // });

    return (
        <div className="ihomepage" >
            <Header />
            <div className="iseparator">
                Patient Monitoring Redefined
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
                {/* <div className="ileftBody">
                    {loading ? <></> : data.patient.vitals_detected ? <img src={vital_gif} alt="loading..." /> : <img src={vital_not_gif} alt="loading..." />}
                </div> */}
                <div className="irightBody">
                    {loading ? <></> : data.patient.in_view ? <img src={face_gif} alt="loading..." /> : <img src={face_not_gif} alt="loading..." />}
                </div>
            </div>
        </div>
    )
};

export default InfoPage;