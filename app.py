import streamlit as st
import random
from streamlit_back_camera_input import back_camera_input

# ========================================
# ひらがなリストの設定
# ========================================
SEION = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん")
DAKUON = list("がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ")
YOUON =["きゃ", "きゅ", "きょ", "しゃ", "しゅ", "しょ", "ちゃ", "ちゅ", "ちょ", 
         "にゃ", "にゅ", "にょ", "ひゃ", "ひゅ", "ひょ", "みゃ", "みゅ", "みょ", "りゃ", "りゅ", "りょ",
         "ぎゃ", "ぎゅ", "ぎょ", "じゃ", "じゅ", "じょ", "びゃ", "びゅ", "びょ", "ぴゃ", "ぴゅ", "ぴょ"]
SOKUON = ["っ"]

# すべて結合して1つのリストにする
HIRAGANA_LIST = SEION + DAKUON + YOUON + SOKUON

def generate_question():
    """速記の反復記号練習用に、様々なパターンの問題をランダム生成する"""
    # 1: 通常（ランダム5ブロック）
    # 2: 1音の繰り返し（例：あかかいう）
    # 3: 2音の繰り返し（例：あかいかき）
    # 4: 3音の繰り返し（例：あいうあいう）
    # 5: 4音の繰り返し（例：あいうえあいうえ）
    
    # どのパターンを出すかランダムに決定
    pattern = random.choice([1, 2, 3, 4, 5])
    
    if pattern == 1:
        return "".join(random.sample(HIRAGANA_LIST, 5))
        
    elif pattern == 2:
        # 1音の繰り返し(AA) ＋ 他3音
        chars = random.sample(HIRAGANA_LIST, 4)
        repeat_part = [chars[0], chars[0]] # AAを作る
        others = chars[1:]
        # ランダムな位置に挿入
        pos = random.randint(0, len(others))
        return "".join(others[:pos] + repeat_part + others[pos:])
        
    elif pattern == 3:
        # 2音の繰り返し(ABAB) ＋ 他1音
        chars = random.sample(HIRAGANA_LIST, 3)
        repeat_part =[chars[0], chars[1], chars[0], chars[1]] # ABABを作る
        others =[chars[2]]
        pos = random.randint(0, len(others))
        return "".join(others[:pos] + repeat_part + others[pos:])
        
    elif pattern == 4:
        # 3音の繰り返し (ABCABC)
        chars = random.sample(HIRAGANA_LIST, 3)
        return "".join(chars + chars)
        
    elif pattern == 5:
        # 4音の繰り返し (ABCDABCD)
        chars = random.sample(HIRAGANA_LIST, 4)
        return "".join(chars + chars)

def init_state():
    """セッションステートの初期化"""
    if "phase" not in st.session_state:
        st.session_state.phase = 1
    if "target_chars" not in st.session_state:
        st.session_state.target_chars = ""
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
    if "judged" not in st.session_state:
        st.session_state.judged = False

def main():
    st.set_page_config(page_title="速記練習アプリ", page_icon="📝")
    st.title("速記練習アプリ 📝")
    
    init_state()

    # ========================================
    # フェーズ1：書き取りフェーズ
    # ========================================
    if st.session_state.phase == 1:
        st.header("1. 書き取りフェーズ")
        
        if not st.session_state.target_chars:
            # 専用関数を使ってお題を生成
            st.session_state.target_chars = generate_question()
            
        st.write("以下の文字を手元の紙に速記してください。")
        
        st.markdown(
            f"<div style='text-align: center; font-size: 80px; font-weight: bold; letter-spacing: 10px; margin: 30px 0;'>"
            f"{st.session_state.target_chars}</div>", 
            unsafe_allow_html=True
        )
        
        if st.button("書き終わったら次へ", type="primary"):
            st.session_state.phase = 2
            st.rerun()

    # ========================================
    # フェーズ2：撮影フェーズ
    # ========================================
    elif st.session_state.phase == 2:
        st.header("2. 撮影フェーズ")
        st.write("速記した手元の紙をカメラで撮影してください。")
        st.info("💡 画面に映っているカメラ映像を直接タップすると無音で撮影できます。")
        
        # 無音・写真保存なしのブラウザ内蔵カメラ
        img = back_camera_input()
        
        if img is not None:
            st.success("画像を取得しました！")
            
            if st.button("この画像で次へ", type="primary"):
                st.session_state.captured_image = img
                st.session_state.phase = 3
                st.rerun()

    # ========================================
    # フェーズ3：反訳（読み取り）フェーズ
    # ========================================
    elif st.session_state.phase == 3:
        st.header("3. 反訳（読み取り）フェーズ")
        st.write("撮影したメモを見ながら、読み取った文字を入力してください。")
        
        if st.session_state.captured_image is not None:
            st.image(st.session_state.captured_image, caption="あなたの速記メモ", use_container_width=True)
            
        user_input = st.text_input("読み取った文字を入力してください:")
        
        if st.button("判定", type="primary"):
            st.session_state.judged = True
            
        if st.session_state.judged:
            if user_input == st.session_state.target_chars:
                st.success("大正解です！お見事！🎉")
            else:
                st.error(f"不正解です...\n\n正解は『 **{st.session_state.target_chars}** 』でした。")
                
        st.markdown("---")
        if st.button("もう一度最初から"):
            st.session_state.phase = 1
            st.session_state.target_chars = ""
            st.session_state.captured_image = None
            st.session_state.judged = False
            st.rerun()

if __name__ == "__main__":
    main()
