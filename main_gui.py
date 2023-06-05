import sys
import openai
from googletrans import Translator
import tweepy
import openaiAPI    # OpenAIのAPIキーなどを変数で定義したpyファイル
import twitterAPI   # TwitterのAPIキーなどを変数で定義したpyファイル
import flet as ft

class Chatgpt:
    output = None
    def __init__(self, input=""):
        self.output = input
        
    def trans2en(self, str):
        # 日本語から英語へ変換し、str型で受け取る
        translator = Translator()
        trans_prompt = translator.translate(str, src="ja", dest="en").text
        return trans_prompt
    
    def generate_gtp(self, str):
        # ChatGPTにプロンプトを渡す
        openai.api_key = openaiAPI.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Responses must be 280 characters for Twitter."},
                {"role": "system", "content": "Statements made in the style of anime characters."},
                {"role": "user", "content": str},
            ]   
        )

        msg = response["choices"][0]["message"]["content"]
        return msg
    
    def trans2ja(self, str):
        # 翻訳する
        translator = Translator()
        trans_msg = translator.translate(str, src="en", dest="ja").text
        res_text = trans_msg
        return res_text
    
    def generate(self, str):
            trans_prompt = self.trans2en(str)
            msg = self.generate_gtp(trans_prompt)
            res_text = self.trans2ja(msg)
            self.output = res_text
            return res_text

def main(page: ft.Page):
    page.window_width = 1000        # window's width is 200 px
    page.window_height = 500       # window's height is 200 px
    page.window_resizable = False  # window is not resizable
    page.update()
    chatgpt = Chatgpt()
    system_message = ft.Text("", size=20, text_align=ft.TextAlign.CENTER)

    def tweet(tweet_content):
        system_message.value = ""
        if len(tweet_content) > 140 :
            system_message.value = "ツイート内容が140字を超過しています"
            page.update()
            return
        
        # tweepyオブジェクト作成
        client = tweepy.Client(
            consumer_key = twitterAPI.CONSUMER_KEY,
            consumer_secret = twitterAPI.CONSUMER_SECRET,
            access_token = twitterAPI.ACCESS_TOKEN,
            access_token_secret = twitterAPI.ACCESS_SECRET
        )

        #ツイートする
        client.create_tweet(text=tweet_content)
        system_message.value = "送信完了！"
        page.update()

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.title = "Pythonを使ってChatGPTを呼んでGoogle翻訳を通してTwitterに投げよう作戦"

    def route_change(route):
        textField = ft.TextField(label="プロンプト", autofocus=True, width=800, hint_text="桜についてのツイートを生成してください")
        input_info = ft.Text(value="AIが文章を考えています……", size=20, text_align=ft.TextAlign.CENTER, visible=False)
        def jump_confirm(e, value):
            input_info.visible = True
            page.update()
            prompt = str(value)
            chatgpt.generate(prompt)
            page.go("/confirm")
            
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("ChatGPTへのプロンプトを入力"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("なんか良い感じのプロンプトを書こう！", size=30, text_align=ft.TextAlign.CENTER),
                    ft.Row(
                        [
                            textField,
                            ft.ElevatedButton("確定", on_click=lambda e: jump_confirm(e, textField.value)),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(
                        [
                            input_info,
                        ], alignment=ft.MainAxisAlignment.CENTER),    
                ],
            )
        )
        if page.route == "/confirm":
            # テキストフィールドに変更があったとき文字数を表示
            def onchange_confirm_textField(e):
                length = len(e.control.value)
                print(length)
                confirm_info.value = str(length) + "文字"
                page.update()

            res_text = chatgpt.output
            confirm_info = ft.Text(str(len(res_text)) + "文字")
            confirm_textField = ft.TextField(
                label="140字以内でツイート内容を入力", 
                hint_text="桜の到着は、冬の最も激しいものからも美しさが出てくることができるという穏やかな思い出のようなものです。#CherryBlossOMSEason", 
                value=res_text, 
                multiline=True, 
                min_lines=1, 
                max_lines=10, 
                width=1000,
                on_change=lambda e:onchange_confirm_textField(e)
                )
            
            page.views.append(
                ft.View(
                    "/confirm",
                    [

                        ft.AppBar(title=ft.Text("投稿確認"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Text("この内容で大丈夫？", size=30, text_align=ft.TextAlign.CENTER),
                        ft.Row(
                            [
                                ft.FilledButton("ツイートする", on_click=lambda e: tweet(confirm_textField.value))
                            ], 
                            alignment=ft.MainAxisAlignment.END),
                        confirm_textField,
                        confirm_info,
                        ft.Row(
                        [
                            system_message,
                        ], alignment=ft.MainAxisAlignment.CENTER),    
                        ft.ElevatedButton("やりなおす", on_click=lambda _: page.go("/")),
                    ],
                    
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.theme = ft.Theme(color_scheme_seed="white")
    page.update()
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)