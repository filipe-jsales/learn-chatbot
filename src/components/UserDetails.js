const userDetailsObjects = {
  user1: {
    name: "John",
    age: 30,
    city: "New York",
  },
  user2: {
    name: "Mary",
    age: 25,
    city: "Boston",
  },
};

const UserDetails = () => {
  const users = Object.values(userDetailsObjects);
  console.log(users.name);
  return (
    <div>
      {users.map((user, index) => (
        <div key={index}>
          <p>Name : {user.name}</p>
          <p>Age: {user.age}</p>
          <p>City: {user.city}</p>
          {user.city >= 18 && <p>Pode tirar habilitação</p>}
        </div>
      ))}
    </div>
  );
};

export default UserDetails;
