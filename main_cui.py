import sys
import openai
from googletrans import Translator
import tweepy
import openaiAPI    # OpenAIのAPIキーなどを変数で定義したpyファイル
import twitterAPI   # TwitterのAPIキーなどを変数で定義したpyファイル
from split_str import split_str

# 標準入力からChatGPTへ入力するプロンプトを受け取る
prompt = input("プロンプトを入力してください: ")
print("対象文字列 : " + prompt)

# 日本語から英語へ変換し、str型で受け取る
translator = Translator()
trans_prompt = translator.translate(prompt, src="ja", dest="en").text
print("変換後 : " + trans_prompt)

# ChatGPTにプロンプトを渡す
openai.api_key = openaiAPI.OPENAI_API_KEY
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Responses must be 240 characters for Twitter."},
        {"role": "user", "content": trans_prompt},
    ]   
)

print(response)
msg = response["choices"][0]["message"]["content"]
# 翻訳する
trans_msg = translator.translate(msg, src="en", dest="ja").text

print("翻訳後 : \n" + trans_msg)

tweet_content = '(ChatGPTから生成)\n' + trans_msg
TWEET_MAX_LEN = 140
# 140文字を超過した分は切り捨て
if(len(tweet_content) > TWEET_MAX_LEN):
    tweet_content = split_str(tweet_content, TWEET_MAX_LEN)[0]

print("ツイート内容 : \n" + tweet_content)
while True:
    apply = input("この内容でツイートしますか？(y/n) : ")
    if apply == "y" or apply == "Y" :
        break
    if apply == "n" or apply == "N" :
        print("プログラム中止")
        sys.exit()
    print("yかnのみが許可されます")

# tweepyオブジェクト作成
client = tweepy.Client(
	consumer_key = twitterAPI.CONSUMER_KEY,
	consumer_secret = twitterAPI.CONSUMER_SECRET,
	access_token = twitterAPI.ACCESS_TOKEN,
	access_token_secret = twitterAPI.ACCESS_SECRET
)

#ツイートする
client.create_tweet(text=tweet_content)