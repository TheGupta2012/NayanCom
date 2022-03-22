import React from 'react';
import './header.css';
import nayanComLogo from '../../images/nayanComLogo.png';

const Header = () => {
    return (
        <div className="header" >
            <div className="logo" >
                <img link="" src={nayanComLogo} alt="logo" />
                <span className="logo-text"> Nayan <span style={{ color: 'black', fontWeight: '600' }}> Com </span> </span>
            </div>
        </div >
    )
};

export default Header;