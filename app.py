import streamlit as st
import random
# 👇 画面にお絵かきするための拡張機能を読み込む
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
    """速記の反復記号練習用に、様々なパターンの問題をランダム生成する"""
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
    """セッションステートの初期化"""
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
    # 👇 メモの方法と、デジタルメモの画像データを保存する変数を追加
    if "input_method" not in st.session_state:
        st.session_state.input_method = "紙に書く"
    if "drawings" not in st.session_state:
        st.session_state.drawings = {}

def reset_game():
    """ゲームのリセット（最初から）"""
    st.session_state.phase = 0
    st.session_state.questions_list =[]
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.shuffled_indices =[]
    st.session_state.drawings = {} # デジタルメモもリセット

def main():
    st.set_page_config(page_title="速記反復練習アプリ", page_icon="📝")
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
        
        st.write("今回練習する問題数（回数）を決めてください。")
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
        
        # デジタルメモを選択した場合のみ、キャンバスを表示する
        if st.session_state.input_method == "画面に直接手書きする（テスト機能）":
            st.write("▼ 下の白い枠内に指で速記を書いてください")
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",  # 塗りつぶしなし
                stroke_width=4,                 # ペンの太さ
                stroke_color="#000000",         # ペンの色（黒）
                background_color="#FFFFFF",     # 背景色（白）
                height=250,                     # キャンバスの高さ
                width=350,                      # スマホでもはみ出ない幅
                drawing_mode="freedraw",
                key=f"canvas_{st.session_state.current_q_index}", # 問題ごとにキャンバスを切り替える
            )
        else:
            st.write("手元の紙に速記してください。")
            
        st.markdown("<br>", unsafe_allow_html=True)

        if current_num < total:
            if st.button("書き終わったら次のお題へ", type="primary"):
                # デジタルメモの場合、書いた画像を保存してから次へ
                if st.session_state.input_method == "画面に直接手書きする（テスト機能）" and canvas_result is not None:
                    st.session_state.drawings[st.session_state.current_q_index] = canvas_result.image_data
                    
                st.session_state.current_q_index += 1
                st.rerun()
        else:
            if st.button("すべて書き終わった！反訳テストへ", type="primary"):
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
        
        # デジタルメモの場合は、これまでに書いたメモをスクロールできる箱の中にまとめて表示する
        if st.session_state.input_method == "画面に直接手書きする（テスト機能）":
            with st.container(height=300):
                st.markdown("📝 **【あなたのデジタルメモ】**")
                for i in range(total):
                    if i in st.session_state.drawings and st.session_state.drawings[i] is not None:
                        st.caption(f"第 {i+1} 問")
                        st.image(st.session_state.drawings[i])
            st.markdown("---")
        
        if st.session_state.current_q_index < total:
            target_idx = st.session_state.shuffled_indices[st.session_state.current_q_index]
            display_num = target_idx + 1
            progress_num = st.session_state.current_q_index + 1
            
            st.subheader(f"解答入力 ({progress_num}/{total})")
            st.warning(f"👀 メモから **「第 {display_num} 問」** に書いた内容を探して、入力してください。")
            
            with st.form(key=f"answer_form_{st.session_state.current_q_index}"):
                user_input = st.text_input("読み取った文字を入力:", key=f"input_{st.session_state.current_q_index}")
                submit = st.form_submit_button("次の解答へ")
                
                if submit:
                    st.session_state.user_answers[target_idx] = user_input
                    st.session_state.current_q_index += 1
                    st.rerun()
                    
        else:
            st.header("🏆 判定結果")
            st.write("※第1問から順番に結果を表示しています。")
            
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
            if st.button("もう一度最初から練習する", type="primary"):
                reset_game()
                st.rerun()

if __name__ == "__main__":
    main()
