import "./App.css";

import CarDetails from "./components/CarDetails";
import ConditionalRender from "./components/ConditionalRender";
import ListRender from "./components/ListRender";
import ManageData from "./components/ManageData";
import ShowUserName from "./components/ShowUserName";

import Fragment from "./components/Fragment";
import Container from "./components/Container";
import ExecuteFunction from "./components/ExecuteFunction";
import Message from "./components/Message";
import { useState } from "react";
import ChangeMessageState from "./components/ChangeMessageState";
import UserDetails from "./components/UserDetails";

function App() {
  const cars = [
    {
      id: 1,
      brand: "VW",
      km: 100000,
      color: "azul",
      newCar: false,
    },
    {
      id: 2,
      brand: "Wolks",
      km: 100000,
      color: "azul",
      newCar: true,
    },
    {
      id: 3,
      brand: "Audi",
      km: 100000,
      color: "azul",
      newCar: false,
    },
  ];

  function showMessage() {
    console.log("Hello World");
  }

  const [message, setMessage] = useState("");

  const handleMessage = (msg) => {
    setMessage(msg);
  };

  return (
    <div className="App">
      <h1>Hello World</h1>
      <ManageData />
      <ListRender />
      <ConditionalRender />
      <ShowUserName name="Matheus" sexo="Masculino" />
      {/* loop object array */}
      {cars.map((car) => (
        <CarDetails
          key={car.id}
          brand={car.brand}
          km={car.km}
          color={car.color}
          newCar={car.newCar}
        />
      ))}
      <Fragment />

      <Container>
        <h1>Children</h1>
        <p>Children</p>
      </Container>

      <ExecuteFunction myFunction={showMessage} />

      {/* state lift */}

      <Message msg={message} />
      <ChangeMessageState handleMessage={handleMessage} />
      <UserDetails />
    </div>
  );
}

export default App;
