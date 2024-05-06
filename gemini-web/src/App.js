import { useState } from "react";

const App = () => {
  const [Error, setError] = useState("");
  return (
    <div className="app">
      <section className="search-section">
        <p>Olá, como posso te ajudar ?</p>
        <button className="surprise">Me Surpreenda!</button>
        <div className="input-container">
          <input value={""} placeholder="Quando e o Natal...?" onChange={""} />
          {!Error && <button>Enviar</button>}
          {Error && <button>Apagar</button>}
        </div>
      </section>
    </div>
  );
};

export default App;
