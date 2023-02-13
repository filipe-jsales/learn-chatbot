import { useState } from "react";

const ManageData = () => {
  let someData = 10;

  const [number, setNumber] = useState(11);

  return (
    <div>
      <div>
        <h1>Manage Data</h1>
        <p>Valor: {someData}</p>
        <button onClick={() => setNumber(999)}>Mudar variável</button>
      </div>
      <div>
        <p>Valor: {number}</p>
      </div>
    </div>
  );
};
export default ManageData;
