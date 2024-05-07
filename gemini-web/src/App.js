import { useState } from "react";

const App = () => {
  const [value, setValue] = useState("");
  const [Error, setError] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const surpriseOptions = [
    "Quem ganhou o ultimo Premio Nobel ?",
    "Qual a maior montanha do mundo ?",
    "Qual a maior floresta do mundo ?",
    "Qual o maior rio do mundo ?",
    "Qual a maior cidade do mundo ?",
  ];
  const surprise = () => {
    const randomValue =
      surpriseOptions[Math.floor(Math.random() * surpriseOptions.length)];
    setValue(randomValue);
  };

  const getResponse = async () => {
    if (!value) {
      setError("Erro! Por favor faça uma pergunta!");
      return;
    }
    try {
      const options = {
        method: "POST",
        body: JSON.stringify({
          history: chatHistory,
          message: value,
        }),
      };
    } catch (error) {
      console.error(error);
      setError(
        "Alguma coisa deu errado! Por favor, tente novamente mais tarde."
      );
    }
  };

  return (
    <section className="app">
      <p>Olá, como posso te ajudar ?</p>
      <button className="surprise" onClick={surprise} disabled={!chatHistory}>
        Me Surpreenda!
      </button>
      <div className="input-container">
        <input
          value={value}
          placeholder="Quando e o Natal...?"
          onChange={(e) => setValue(e.target.value)}
        />
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
