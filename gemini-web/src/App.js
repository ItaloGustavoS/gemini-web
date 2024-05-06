import { useState } from "react";

const App = () => {
  const [Error, setError] = useState("");
  return (
    <section className="app">
      <p>Olá, como posso te ajudar ?</p>
      <button className="surprise">Me Surpreenda!</button>
      <div className="input-container">
        <input value={""} placeholder="Quando e o Natal...?" onChange={""} />
        {!Error && <button>Enviar</button>}
        {Error && <button>Apagar</button>}
      </div>
      {error && <p>{error}</p>}
      <div className="search-result">
        <div key={""}>
          <p classname="answer"></p>
        </div>
      </div>
    </section>
  );
};

export default App;
