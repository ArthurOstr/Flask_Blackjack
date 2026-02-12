export interface Card {
  rank: string;
  suit: string;
}

export interface GameState {
  game_id: number;
  player_hand: Card[];
  dealer_hand?: Card[];
  dealer_card?: Card;
  player_score?: number;
  dealer_score?: number;
  user_money: number;
  status: "active" | "player_win" | "dealer_win" | "push";
  message: string;
}

export interface User {
  username: string;
  money: number;
}
