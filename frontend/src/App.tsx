import { useState, useEffect } from "react";
import "./App.css";

interface UserProfile {
  username: string;
  money: number;
  wins: number;
  losses: number;
}

function App() {
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    fetch("/api/user/profile")
      .then((res) => res.json())
      .then((data) => setUser(data))
      .catch((err) => console.error("API connection failed"));
  }, []);

  if (!user) return <div>Contacting the vault...</div>;

  // 3. The Visual (Painting the data)
  return (
    <div className="profile-card">
      <h1>Blackjack Royale</h1>
      <div className="stats">
        <h2>Welcome, {user.username}</h2>
        <p>Wallet: ${user.money}</p>
        <p>
          Record: {user.wins}W / {user.losses}L
        </p>
      </div>
    </div>
  );
}

export default App;
