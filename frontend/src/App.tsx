import { useState, useEffect } from "react";
import "./App.css";

interface GameResponse {
  game_id: number;
  player_hand: { rank: string; suit: string }[];
  dealer_hand?: { rank: string; suit: string }[];
  dealer_card?: { rank: string; suit: string };
  user_money: number;
  message: string;
  status: string;
}
interface LoginResponse {
  message: string;
  username: string;
  error?: string;
}

function App() {
  // Auth State
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [user, setUser] = useState<string>("");

  // Game State
  const [gameId, setGameId] = useState<number | null>(null);
  const [money, setMoney] = useState<number>(1000);
  const [message, setMessage] = useState<string>("Ready to play?");
  const [hand, setHand] = useState<{ rank: string; suit: string }[]>([]);
  const [dealerHand, setDealerHand] = useState<
    { rank: string; suit: string }[]
  >([]);

  // --- System Check on Load ---
  useEffect(() => {
    // Backend check
    fetch("/api/test")
      .then((res) => res.json())
      .then((data) => console.log("System Check:", data.message))
      .catch((err) => console.error("System Offline:", err));

    // Check if the user was logged in
    fetch("/api/user/profile").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setIsLoggedIn(true);
        setUser(data.username);
        setMoney(data.money);
      }
    });
  }, []);

  // --- Login Logic ---
  async function handleLogin(e: React.FormEvent) {
    e.preventDefault(); // Stop page reload

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data: LoginResponse = await response.json();

      if (!response.ok) {
        setMessage(data.error || "Login failed");
      } else {
        setIsLoggedIn(true);
        setUser(data.username);
        setMessage(`Welcome, ${data.username}`);
        // Fetch fresh money
        fetchProfile();
      }
    } catch (err) {
      console.error(err);
      setMessage("Network Error");
    }
  }

  // --- Profile Fetcher---
  async function fetchProfile() {
    const res = await fetch("/api/user/profile");
    if (res.ok) {
      const data = await res.json();
      setMoney(data.money);
    }
  }

  // --- Game Logic---
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
      if (response.status === 401) {
        setIsLoggedIn(false);
        setMessage("Session expired. Login again.");
        return;
      }

      const data: GameResponse = await response.json();
      console.log("Server replied:", data);

      setGameId(data.game_id);
      setMoney(data.user_money);
      setHand(data.player_hand);

      if (data.dealer_card) {
        setDealerHand([data.dealer_card]);
      }
      setMessage(data.message);
    } catch (error) {
      console.error("Failed to deal:", error);
      setMessage("Connection failed. Are you logged in?");
    }
  }
  // --- Game Action:Hit ---
  async function handleHit() {
    if (!gameId) return; // Prevents to hit without the game was started

    try {
      const response = await fetch("/api/hit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId }),
      });

      const data = await response.json();
      setHand(data.player_hand);
      setMessage(data.message);

      // If the player busts, the API reutrns status: "dealer wit"
      if (data.status !== "active") {
        setGameId(null); // Ends the active game loop
        fetchProfile(); // Wallet update
      }
    } catch (error) {
      console.error("Hit failed:", error);
    }
  }
  // --- Game Action: Stand ---
  async function handleStand() {
    if (!gameId) return;

    try {
      const response = await fetch("/api/stand", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId }),
      });

      const data = await response.json();
      if (data.dealer_hand) setDealerHand(data.dealer_hand);
      setMessage(data.message);
      setGameId(null); // End of game loop
      fetchProfile(); // Wallet update
    } catch (error) {
      console.error("Stand failed", error);
    }
  }
  // --- The Render ---
  return (
    <div className="card">
      <h1>♠️ Operator Blackjack ♦️</h1>
      <p>Status: {message}</p>

      {!isLoggedIn ? (
        // --- LOGIN FORM ---
        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Login</button>
        </form>
      ) : (
        // --- GAME INTERFACE ---
        <div className="game-board">
          <h2>
            Player: {user} | Cash: ${money}
          </h2>

          <div className="actions">
            {!gameId ? (
              <button onClick={handleDeal}>Deal Hand ($50)</button>
            ) : (
              <>
                <button onClick={handleHit} style={{ marginRight: "10px" }}>
                  Hit
                </button>
                <button onClick={handleStand}>Stand</button>
              </>
            )}
          </div>

          {/* THE TABLE */}
          <div className="table" style={{ marginTop: "20px" }}>
            {/* DEALER ZONE */}
            {dealerHand.length > 0 && (
              <div
                className="hand dealer-hand"
                style={{ marginBottom: "20px" }}
              >
                <h3>Dealer's Hand:</h3>
                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                    justifyContent: "center",
                  }}
                >
                  {dealerHand.map((card, idx) => (
                    <div
                      key={idx}
                      style={{
                        border: "1px solid red",
                        padding: "10px",
                        minWidth: "80px",
                      }}
                    >
                      {card.rank} of {card.suit}
                    </div>
                  ))}
                  {gameId && dealerHand.length === 1 && (
                    <div
                      style={{
                        border: "1px solid gray",
                        padding: "10px",
                        minWidth: "80px",
                        backgroundColor: "#333",
                      }}
                    >
                      [Hidden]
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* PLAYER ZONE */}
            {hand.length > 0 && (
              <div className="hand player-hand">
                <h3>Your Hand:</h3>
                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                    justifyContent: "center",
                  }}
                >
                  {hand.map((card, idx) => (
                    <div
                      key={idx}
                      style={{
                        border: "1px solid #4CAF50",
                        padding: "10px",
                        minWidth: "80px",
                      }}
                    >
                      {card.rank} of {card.suit}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
export default App;
