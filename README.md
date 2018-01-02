### line-bot-example
[line-bot-sdk](https://github.com/line/line-bot-sdk-python) \

## 架構
設計上將程式碼與回覆內容做了分割，可以提升修改的便利性 \
每種回覆內容設計一個專門處理的 function \
 message 內的 json 檔 只需填寫必要回覆內容 \

## example 機器人
![](https://i.imgur.com/5lj827q.png)

## 功能展示
在對話中輸入：
* text (文字訊息)
* buttons (表單按鈕)
* carousel (可滑動的表單)
* confirm (確認表單)
* imagemap (可再進行互動的圖片)