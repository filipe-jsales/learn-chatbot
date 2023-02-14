import { useState } from "react";

const ConditionalRender = () => {
  const [name, setName] = useState("Pedro");
  const [x] = useState(true);
  return (
    <div>
      <h1>Isso será exibido?</h1>
      {x && <h2>Sim</h2>}
      {!x && <h2>Não</h2>}
      {name === "Matheus" ? <div>{name}</div> : <div>Nome não é Matheus</div>}
      <button onClick={() => setName("Matheus")}>Clique aqui</button>
    </div>
  );
};

export default ConditionalRender;
