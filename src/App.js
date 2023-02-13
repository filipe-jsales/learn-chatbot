import "./App.css";

import City from "./assets/city.jpg";
import ConditionalRender from "./components/ConditionalRender";
import ListRender from "./components/ListRender";
import ManageData from "./components/ManageData";

function App() {
  return (
    <div className="App">
      <h1>Hello World</h1>
      <ManageData />
      <ListRender />
      <ConditionalRender />
    </div>
  );
}

export default App;
