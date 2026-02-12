import { useState, useEffect } from "react";
import "./App.css";

interface GameResponse {
  game_id: number;
  player_hand: { rank: string; suit: string }[];
  user_money: number;
  message: string;
}

function App() {
  const [gameId, setGameId] = useState<number | null>(null);
  const [money, setMoney] = useState<number>(1000);
  const [message, setMessage] = useState<string>("Ready to play?");

  useEffect(() => {
    fetch("/api/test")
      .then((res) => res.json())
      .then((data) => console.log("System Check:", data.message))
      .catch((err) => console.error("System Offline:", err));
  }, []);

  async function handleDeal() {
    console.log("Dealing...");

    try {
      const response = await fetch("/api/deal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ bet_amount: 50 }),
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data: GameResponse = await response.json();
      console.log("Server replied:", data);

      setGameId(data.game_id);
      setMoney(data.user_money);
      setMessage(data.message);
    } catch (error) {
      console.error("Failed to deal:", error);
      setMessage("Connection failed. Are you logged in?");
    }
  }

  return (
    <div className="card">
      <h1>Operator Blackjack</h1>
      <p>Money: ${money}</p>
      <p>Status: {message}</p>

      {/* The Button triggers the function above */}
      <button onClick={handleDeal}>Deal Hand ($50)</button>

      {gameId && <p>Game Active: ID #{gameId}</p>}
    </div>
  );
}
export default App;
