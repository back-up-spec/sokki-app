import streamlit as st
import random
import time
from streamlit_drawable_canvas import st_canvas
# 👇 ローカルストレージ（ブラウザへの保存）用の拡張機能を読み込む
from streamlit_local_storage import LocalStorage

# ========================================
# ひらがなリストの設定
# ========================================
SEION = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん")
DAKUON = list("がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ")
YOUON =["きゃ", "きゅ", "きょ", "しゃ", "しゅ", "しょ", "ちゃ", "ちゅ", "ちょ", 
         "にゃ", "にゅ", "にょ", "ひゃ", "ひゅ", "ひょ", "みゃ", "みゅ", "みょ", "りゃ", "りゅ", "りょ",
         "ぎゃ", "ぎゅ", "ぎょ", "じゃ", "じゅ", "じょ", "びゃ", "びゅ", "びょ", "ぴゃ", "ぴゅ", "ぴょ"]
SOKUON = ["っ"]

HIRAGANA_LIST = SEION + DAKUON + YOUON + SOKUON

# ローカルストレージ機能の初期化
localS = LocalStorage()

def generate_question():
    patterns =[1, 2, 3, 4, 5]
    weights =[60, 10, 10, 10, 10]
    pattern = random.choices(patterns, weights=weights, k=1)[0]
    
    if pattern == 1:
        return "".join(random.sample(HIRAGANA_LIST, 5))
    elif pattern == 2:
        chars = random.sample(HIRAGANA_LIST, 4)
        repeat_part = [chars[0], chars[0]]
        others = chars[1:]
        pos = random.randint(0, len(others))
        return "".join(others[:pos] + repeat_part + others[pos:])
    elif pattern == 3:
        chars = random.sample(HIRAGANA_LIST, 3)
        repeat_part =[chars[0], chars[1], chars[0], chars[1]]
        others =[chars[2]]
        pos = random.randint(0, len(others))
        return "".join(others[:pos] + repeat_part + others[pos:])
    elif pattern == 4:
        chars = random.sample(HIRAGANA_LIST, 3)
        return "".join(chars + chars)
    elif pattern == 5:
        chars = random.sample(HIRAGANA_LIST, 4)
        return "".join(chars + chars)

def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 3
    if "questions_list" not in st.session_state:
        st.session_state.questions_list =[]
    if "current_q_index" not in st.session_state:
        st.session_state.current_q_index = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "shuffled_indices" not in st.session_state:
        st.session_state.shuffled_indices =[]
    if "input_method" not in st.session_state:
        st.session_state.input_method = "紙に書く"
    if "drawings" not in st.session_state:
        st.session_state.drawings = {}
    if "total_time" not in st.session_state:
        st.session_state.total_time = 0.0
    if "q_start_time" not in st.session_state:
        st.session_state.q_start_time = None
    if "judged" not in st.session_state:
        st.session_state.judged = False
        
    # 👇 ブラウザの保存領域から「sokki_scores」という名前で過去のスコア履歴を読み込む
    if "score_history" not in st.session_state:
        saved_scores = localS.getItem("sokki_scores")
        # 何も保存されていなければ空のリスト、保存されていればそのリストを使う
        st.session_state.score_history = saved_scores if saved_scores else[]

def reset_game():
    st.session_state.phase = 0
    st.session_state.questions_list =[]
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.shuffled_indices =[]
    st.session_state.drawings = {}
    st.session_state.total_time = 0.0
    st.session_state.q_start_time = None
    st.session_state.judged = False

def main():
    st.set_page_config(page_title="速記反復練習アプリ", page_icon="📝", layout="centered")
    st.title("速記反復練習アプリ 📝")
    
    init_state()

    # ========================================
    # フェーズ0：設定フェーズ
    # ========================================
    if st.session_state.phase == 0:
        st.header("⚙️ 設定フェーズ")
        
        st.session_state.input_method = st.radio(
            "メモの方法を選択してください：",["紙に書く", "画面に直接手書きする（テスト機能）"]
        )
        
        st.session_state.total_questions = st.number_input(
            "練習回数", min_value=1, max_value=50, value=5, step=1
        )
        
        if st.button("この設定でスタート", type="primary"):
            st.session_state.questions_list =[generate_question() for _ in range(st.session_state.total_questions)]
            st.session_state.phase = 1
            st.rerun()
            
        # これまでのスコアをリセットする機能
        if len(st.session_state.score_history) > 0:
            st.markdown("---")
            if st.button("🗑️ スコアの履歴を削除する"):
                st.session_state.score_history = []
                localS.setItem("sokki_scores",[])
                st.success("スコアの履歴を削除しました。")
                st.rerun()

    # ========================================
    # フェーズ1：連続書き取りフェーズ
    # ========================================
    elif st.session_state.phase == 1:
        st.header("1. 連続書き取りフェーズ")
        
        if st.session_state.q_start_time is None:
            st.session_state.q_start_time = time.time()
        
        current_num = st.session_state.current_q_index + 1
        total = st.session_state.total_questions
        
        st.subheader(f"第 {current_num} 問 / 全 {total} 問")
        
        current_target = st.session_state.questions_list[st.session_state.current_q_index]
        st.markdown(
            f"<div style='text-align: center; font-size: 60px; font-weight: bold; letter-spacing: 10px; margin: 30px 0;'>"
            f"{current_target}</div>", 
            unsafe_allow_html=True
        )
        
        canvas_result = None
        
        if st.session_state.input_method == "画面に直接手書きする（テスト機能）":
            st.markdown(
                """
                <style>
                canvas { width: 100% !important; touch-action: none; }
                </style>
                """,
                unsafe_allow_html=True,
            )
            
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 1)", 
                stroke_width=4,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=300, 
                width=400,  
                drawing_mode="freedraw",
                key=f"canvas_{st.session_state.current_q_index}", 
            )
            st.caption("※下のゴミ箱アイコンで全消去できます")
        else:
            st.write("手元の紙に速記してください。")
            
        st.markdown("<br>", unsafe_allow_html=True)

        if current_num < total:
            if st.button("書き終わったら次のお題へ", type="primary", use_container_width=True):
                if st.session_state.input_method == "画面に直接手書きする（テスト機能）" and canvas_result is not None:
                    st.session_state.drawings[st.session_state.current_q_index] = canvas_result.image_data
                
                st.session_state.total_time += time.time() - st.session_state.q_start_time
                st.session_state.q_start_time = None
                
                st.session_state.current_q_index += 1
                st.rerun()
        else:
            if st.button("すべて書き終わった！反訳テストへ", type="primary", use_container_width=True):
                if st.session_state.input_method == "画面に直接手書きする（テスト機能）" and canvas_result is not None:
                    st.session_state.drawings[st.session_state.current_q_index] = canvas_result.image_data
                
                st.session_state.total_time += time.time() - st.session_state.q_start_time
                st.session_state.q_start_time = None
                
                indices = list(range(st.session_state.total_questions))
                random.shuffle(indices)
                st.session_state.shuffled_indices = indices
                st.session_state.current_q_index = 0
                st.session_state.phase = 2 
                st.rerun()

    # ========================================
    # フェーズ2：ランダム連続反訳フェーズ ＆ 結果発表
    # ========================================
    elif st.session_state.phase == 2:
        st.header("2. 連続反訳フェーズ")
        total = st.session_state.total_questions
        
        if st.session_state.input_method == "画面に直接手書きする（テスト機能）":
            with st.container(height=350):
                st.markdown("📝 **【あなたのデジタルメモ】**")
                for i in range(total):
                    if i in st.session_state.drawings and st.session_state.drawings[i] is not None:
                        st.caption(f"第 {i+1} 問")
                        st.image(st.session_state.drawings[i], use_container_width=True)
            st.markdown("---")
        
        if st.session_state.current_q_index < total:
            target_idx = st.session_state.shuffled_indices[st.session_state.current_q_index]
            display_num = target_idx + 1
            progress_num = st.session_state.current_q_index + 1
            
            st.subheader(f"解答入力 ({progress_num}/{total})")
            st.warning(f"👀 メモから **「第 {display_num} 問」** を探して入力してください。")
            
            with st.form(key=f"answer_form_{st.session_state.current_q_index}"):
                user_input = st.text_input("読み取った文字を入力:", key=f"input_{st.session_state.current_q_index}")
                submit = st.form_submit_button("次の解答へ", use_container_width=True)
                if submit:
                    st.session_state.user_answers[target_idx] = user_input
                    st.session_state.current_q_index += 1
                    st.rerun()
                    
        else:
            # スコア計算と保存の処理
            if not st.session_state.judged:
                correct_count = sum([1 for i in range(total) if st.session_state.questions_list[i] == st.session_state.user_answers.get(i, "")])
                
                avg_time = st.session_state.total_time / total
                base_score = correct_count * 1000
                speed_bonus = correct_count * max(0, 10 - avg_time) * 100
                final_score = int(base_score + speed_bonus)
                
                # スコアをリストに追加し、ブラウザのストレージにも保存する
                st.session_state.score_history.append(final_score)
                localS.setItem("sokki_scores", st.session_state.score_history)
                
                st.session_state.judged = True

            st.header("🏆 判定結果")
            
            st.success(f"### 🎯 今回のスコア： {st.session_state.score_history[-1]:,} 点")
            avg_time_display = st.session_state.total_time / total
            st.write(f"⏱️ 平均書き取り時間: 1問あたり **{avg_time_display:.1f} 秒**")
            
            # グラフ表示（過去分を含めて2回以上プレイしている場合）
            if len(st.session_state.score_history) > 1:
                st.markdown("📈 **スコアの推移（過去からの成長記録）**")
                st.line_chart(st.session_state.score_history)
            
            st.markdown("---")
            
            correct_count = 0
            for i in range(total):
                st.markdown(f"**第 {i+1} 問**")
                correct_ans = st.session_state.questions_list[i]
                user_ans = st.session_state.user_answers.get(i, "")
                if correct_ans == user_ans:
                    st.success(f"⭕ 正解！ (入力: {user_ans})")
                    correct_count += 1
                else:
                    st.error(f"❌ 不正解... (入力: {user_ans} / 正解: {correct_ans})")
            
            st.markdown(f"**正答率： {correct_count} / {total}**")
            
            if correct_count == total:
                st.balloons()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("もう一度最初から練習する", type="primary", use_container_width=True):
                reset_game()
                st.rerun()

if __name__ == "__main__":
    main()
