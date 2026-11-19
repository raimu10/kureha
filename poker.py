import random
import streamlit as st
from treys import Card, Deck, Evaluator

st.title("ポーカー勝率＆役確率計算ツール")

suits = {"♠": "s", "♡": "h", "♦": "d", "♧": "c"}
ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
all_cards = [s + r for s in suits.keys() for r in ranks]

# 役クラス
rank_names = {
    1: "ストレートフラッシュ（ロイヤル含む）",
    2: "フォーカード",
    3: "フルハウス",
    4: "フラッシュ",
    5: "ストレート",
    6: "スリーカード",
    7: "ツーペア",
    8: "ワンペア",
    9: "ハイカード（役なし）",
}

total_players = st.selectbox(
    "① ポットに参加している人数（自分を含む）を選んでください",
    options=[2, 3, 4, 5, 6],
    index=0,
    format_func=lambda x: f"{x}人（自分 vs 相手{x-1}人）",
)

#カード選択
my_hand_str = st.multiselect(
    "② 自分の手札を【2枚】選んでください", all_cards, max_selections=2
)
board_str = st.multiselect(
    "③ 場のカードを【0〜5枚】選んでください（プリフロップなら0枚）",
    all_cards,
    max_selections=5,
)

#勝率と役の確率計算
if st.button("勝率と役の確率を計算する"):
    #重複チェック
    if len(my_hand_str) != 2:
        st.error("自分の手札をちょうど2枚選んでください")
    elif len(set(my_hand_str + board_str)) != len(my_hand_str) + len(board_str):
        st.error("自分と場のカードで同じカードが重複しています")
    else:
        my_hand = [Card.new(c[1] + suits[c[0]]) for c in my_hand_str]
        board = [Card.new(c[1] + suits[c[0]]) for c in board_str]

        used_cards = my_hand + board
        remaining_deck = [c for c in Deck.GetFullDeck() if c not in used_cards]

        evaluator = Evaluator()
        win = 0
        lose = 0
        tie = 0

        # 役ごとのカウント用辞書を初期化
        hand_counts = {k: 0 for k in rank_names.keys()}

        num_opponents = total_players - 1
        simulations = 5000

        for _ in range(simulations):
            needed_board = 5 - len(board)
            drawn = random.sample(remaining_deck, needed_board + (num_opponents * 2))

            sim_board = board + drawn[:needed_board]
            opp_cards = drawn[needed_board:]

            # 自分のスコアと役クラスを判定
            my_score = evaluator.evaluate(sim_board, my_hand)
            rank_class = evaluator.get_rank_class(my_score)
            hand_counts[rank_class] += 1

            opp_scores = []
            for i in range(num_opponents):
                opp_hand = opp_cards[i * 2 : (i + 1) * 2]
                opp_scores.append(evaluator.evaluate(sim_board, opp_hand))

            best_opp_score = min(opp_scores)

            if my_score < best_opp_score:
                win += 1
            elif my_score > best_opp_score:
                lose += 1
            else:
                tie += 1

        st.subheader(f"計算結果（{total_players}人参加）")

        col1, col2, col3 = st.columns(3)
        col1.metric("勝ち", f"{win / simulations * 100:.1f} %")
        col2.metric("負け", f"{lose / simulations * 100:.1f} %")
        col3.metric("引き分け", f"{tie / simulations * 100:.1f} %")

        st.subheader("自分の最終的な役の完成確率")
        for rank_id, name in rank_names.items():
            prob = hand_counts[rank_id] / simulations * 100
            st.write(f"**{name}**: {prob:.1f} %")
            st.progress(min(prob / 100, 1.0))