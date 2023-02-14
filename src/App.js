import "./App.css";

import CarDetails from "./components/CarDetails";
import ConditionalRender from "./components/ConditionalRender";
import ListRender from "./components/ListRender";
import ManageData from "./components/ManageData";
import ShowUserName from "./components/ShowUserName";

import Fragment from "./components/Fragment";

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
    </div>
  );
}

export default App;
