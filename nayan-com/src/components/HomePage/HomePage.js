import './HomePage.css';
import React from 'react';
import body_vector from '../../images/body_vector.png';
import Header from '../header/header';
import Form from './form/form.js'


function HomePage() {

    return (
        <div className="homepage" >
            <Header />
            <div className="separator">
                {/* An IoT project for the terminally ill patients. */}
                Redefining patient well being.
            </div>
            <div className="body" >
                <div className="leftBody">
                    <Form />
                </div>
                <div className="rightBody">
                    <img src={body_vector} alt="iot" />
                </div>
            </div>
        </div>
    )
};

export default HomePage;