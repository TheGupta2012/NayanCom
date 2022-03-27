import './App.css';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import React from 'react';
import HomePage from './components/HomePage/HomePage';
import InfoPage from './components/InfoPage/InfoPage';

function App() {
  return (
    <div className="App">
      <Router>
        <Switch>
        <Route exact path="/"> <HomePage /> </Route>
          {/* <Route exact path="/" element={HomePage} /> */}
          <Route exact path="/processing"> <InfoPage /> </Route>
        </Switch>
      </Router>
    </div>
  )
}

export default App;
