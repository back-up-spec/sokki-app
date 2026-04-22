import streamlit as st
import random
from streamlit_drawable_canvas import st_canvas

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

def generate_question():
    patterns = [1, 2, 3, 4, 5]
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
    # 👇 描画モード（ペンか消しゴムか）を管理する変数
    if "drawing_mode" not in st.session_state:
        st.session_state.drawing_mode = "freedraw" # freedraw=ペン, transform=消しゴムの代用(選択して消す)等の回避策

def reset_game():
    st.session_state.phase = 0
    st.session_state.questions_list =[]
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.shuffled_indices =[]
    st.session_state.drawings = {}
    st.session_state.drawing_mode = "freedraw"

def main():
    # スマホ対応のため、layoutを"wide"にして横幅を広げやすくする
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

    # ========================================
    # フェーズ1：連続書き取りフェーズ
    # ========================================
    elif st.session_state.phase == 1:
        st.header("1. 連続書き取りフェーズ")
        
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
            # 線の色をモードによって切り替える（消しゴムの代用として白ペンを使う）
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ ペンで書く", use_container_width=True):
                    st.session_state.drawing_mode = "ペン"
            with col2:
                if st.button("🧽 消しゴム (白ペン)", use_container_width=True):
                    st.session_state.drawing_mode = "消しゴム"
            
            # モードに応じた設定
            stroke_color = "#000000" if st.session_state.drawing_mode == "ペン" else "#FFFFFF"
            stroke_width = 3 if st.session_state.drawing_mode == "ペン" else 20 # 消しゴムは太くする
            
            st.caption(f"現在のモード: **{st.session_state.drawing_mode}**")
            
            # CSSで横幅いっぱいになるように調整
            st.markdown(
                """
                <style>
                canvas {
                    width: 100% !important;
                    touch-action: none; /* スマホのスワイプ誤爆を防ぐ */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 1)", 
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="#FFFFFF",
                height=300, # 縦幅を広げて書きやすく
                width=400,  # ベースサイズ（CSSで100%に引き伸ばされる）
                drawing_mode="freedraw",
                key=f"canvas_{st.session_state.current_q_index}_{st.session_state.drawing_mode}", 
            )
            st.caption("※下のゴミ箱アイコンで全消去できます")
        else:
            st.write("手元の紙に速記してください。")
            
        st.markdown("<br>", unsafe_allow_html=True)

        if current_num < total:
            if st.button("書き終わったら次のお題へ", type="primary", use_container_width=True):
                if st.session_state.input_method == "画面に直接手書きする（テスト機能）" and canvas_result is not None:
                    st.session_state.drawings[st.session_state.current_q_index] = canvas_result.image_data
                st.session_state.current_q_index += 1
                st.session_state.drawing_mode = "ペン" # 次の問題に行ったらペンに戻す
                st.rerun()
        else:
            if st.button("すべて書き終わった！反訳テストへ", type="primary", use_container_width=True):
                if st.session_state.input_method == "画面に直接手書きする（テスト機能）" and canvas_result is not None:
                    st.session_state.drawings[st.session_state.current_q_index] = canvas_result.image_data
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
            st.header("🏆 判定結果")
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
            
            st.markdown("---")
            st.markdown(f"### あなたの正答率： **{correct_count} / {total}**")
            
            if correct_count == total:
                st.balloons()
                st.success("🎉 全問正解です！素晴らしい！")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("もう一度最初から練習する", type="primary", use_container_width=True):
                reset_game()
                st.rerun()

if __name__ == "__main__":
    main()
