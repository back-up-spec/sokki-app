import streamlit as st
import random

# 『あ』〜『ん』の一般的なひらがな（清音）リストを用意
HIRAGANA_LIST = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん")

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
    
    # セッションステートの初期化
    init_state()

    # ========================================
    # フェーズ1：書き取りフェーズ
    # ========================================
    if st.session_state.phase == 1:
        st.header("1. 書き取りフェーズ")
        
        # お題の文字が未生成の場合、ランダムに5文字抽出
        if not st.session_state.target_chars:
            st.session_state.target_chars = "".join(random.sample(HIRAGANA_LIST, 5))
            
        st.write("以下のひらがな5文字を手元の紙に速記してください。")
        
        # HTML/CSSを使って大きく表示
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
        
        # カメラ入力を配置
        img = st.camera_input("カメラで撮影")
        
        # 撮影完了後の処理
        if img is not None:
            st.success("画像を取得しました！")
            
            # 撮影した画像をセッションに保存して次へ
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
        
        # フェーズ2で撮影した画像を表示
        if st.session_state.captured_image is not None:
            st.image(st.session_state.captured_image, caption="あなたの速記メモ", use_container_width=True)
            
        # ユーザーの入力用テキストボックス
        user_input = st.text_input("読み取った5文字を入力してください:", max_chars=5)
        
        # 判定ボタン
        if st.button("判定", type="primary"):
            st.session_state.judged = True
            
        # 判定結果の表示
        if st.session_state.judged:
            if user_input == st.session_state.target_chars:
                st.success("大正解です！お見事！🎉")
            else:
                st.error(f"不正解です...\n\n正解は『 **{st.session_state.target_chars}** 』でした。")
                
        st.markdown("---")
        # 最初からやり直す処理
        if st.button("もう一度最初から"):
            st.session_state.phase = 1
            st.session_state.target_chars = ""
            st.session_state.captured_image = None
            st.session_state.judged = False
            st.rerun()

if __name__ == "__main__":
    main()
