const ShowUserName = (props) => {
  return (
    <div>
      <h2>Nome do usuário é: {props.name} </h2>
      <h2>Sexo é: {props.sexo}</h2>
    </div>
  );
};

export default ShowUserName;
